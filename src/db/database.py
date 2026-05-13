from __future__ import annotations

import logging
from collections.abc import Generator
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from typing import Any

from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from src.core.config import get_settings
from src.db.client_factory import DatabaseClientFactory
from src.models.entities import Category, Listing, ListingImage, ListingStatus, Message, Role, User

logger = logging.getLogger(__name__)
settings = get_settings()

COLLECTIONS: dict[type, str] = {
    User: "users",
    Category: "categories",
    Listing: "listings",
    ListingImage: "listing_images",
    Message: "messages",
}


def _normalize_datetime(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class DatabaseSession:
    def __init__(self, database: Database) -> None:
        self.database = database
        self._tracked: dict[tuple[type, int], Any] = {}
        self._deleted: set[tuple[type, int]] = set()

    def close(self) -> None:
        self._tracked.clear()
        self._deleted.clear()

    def collection(self, name: str) -> Collection:
        return self.database[name]

    def add(self, entity: Any) -> Any:
        collection_name = COLLECTIONS[type(entity)]
        if entity.id is None:
            entity.id = self.next_id(collection_name)
        self._tracked[(type(entity), entity.id)] = entity
        self._deleted.discard((type(entity), entity.id))
        return entity

    def add_all(self, entities: list[Any]) -> None:
        for entity in entities:
            self.add(entity)

    def get(self, model: type, entity_id: int) -> Any | None:
        tracked = self._tracked.get((model, entity_id))
        if tracked is not None:
            return tracked
        document = self.collection(COLLECTIONS[model]).find_one({"id": entity_id})
        if document is None:
            return None
        entity = deserialize(model, document, self)
        self._tracked[(model, entity_id)] = entity
        return entity

    def delete(self, entity: Any) -> None:
        if entity.id is None:
            return
        self._deleted.add((type(entity), entity.id))
        self._tracked.pop((type(entity), entity.id), None)

    def refresh(self, entity: Any) -> None:
        if entity.id is None:
            return
        document = self.collection(COLLECTIONS[type(entity)]).find_one({"id": entity.id})
        if document is None:
            return
        fresh = deserialize(type(entity), document, self)
        for key, value in vars(fresh).items():
            setattr(entity, key, value)
        self._tracked[(type(entity), entity.id)] = entity

    def commit(self) -> None:
        for model, entity_id in list(self._deleted):
            collection_name = COLLECTIONS[model]
            self.collection(collection_name).delete_one({"id": entity_id})
            if model is Listing:
                self.collection("listing_images").delete_many({"listing_id": entity_id})
                self.collection("messages").delete_many({"listing_id": entity_id})
            self._deleted.discard((model, entity_id))

        for (model, entity_id), entity in list(self._tracked.items()):
            payload = serialize(entity)
            self.collection(COLLECTIONS[model]).replace_one({"id": entity_id}, payload, upsert=True)
            if model is Listing:
                self._sync_listing_images(entity)

    def next_id(self, sequence_name: str) -> int:
        result = self.collection("counters").find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            return 1
        return int(result["seq"])

    def find_one(self, model: type, query: dict[str, Any]) -> Any | None:
        document = self.collection(COLLECTIONS[model]).find_one(query)
        if document is None:
            return None
        entity = deserialize(model, document, self)
        self._tracked[(model, entity.id)] = entity
        return entity

    def find_many(
        self,
        model: type,
        query: dict[str, Any] | None = None,
        *,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[Any]:
        cursor = self.collection(COLLECTIONS[model]).find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        entities = [deserialize(model, document, self) for document in cursor]
        for entity in entities:
            self._tracked[(model, entity.id)] = entity
        return entities

    def count(self, model: type, query: dict[str, Any] | None = None) -> int:
        return int(self.collection(COLLECTIONS[model]).count_documents(query or {}))

    def _sync_listing_images(self, listing: Listing) -> None:
        if listing.id is None:
            return
        images: list[dict[str, Any]] = []
        for position, image in enumerate(listing.images):
            if image.id is None:
                image.id = self.next_id("listing_images")
            image.listing_id = listing.id
            image.position = position
            images.append(serialize(image))
        self.collection("listing_images").delete_many({"listing_id": listing.id})
        if images:
            self.collection("listing_images").insert_many(images)


def serialize(entity: Any) -> dict[str, Any]:
    if not is_dataclass(entity):
        raise TypeError(f"Unsupported entity type: {type(entity)!r}")
    payload = asdict(entity)
    payload.pop("images", None)
    payload.pop("owner_name", None)
    payload.pop("sender_name", None)
    payload.pop("recipient_name", None)
    payload["_id"] = payload["id"]
    if isinstance(entity, User):
        payload["role"] = entity.role.value
    if isinstance(entity, Listing):
        payload["status"] = entity.status.value
        payload["created_at"] = _normalize_datetime(entity.created_at)
        payload["updated_at"] = _normalize_datetime(entity.updated_at)
    if isinstance(entity, Message):
        payload["created_at"] = _normalize_datetime(entity.created_at)
    if isinstance(entity, User):
        payload["created_at"] = _normalize_datetime(entity.created_at)
    return payload


def deserialize(model: type, document: dict[str, Any], db: DatabaseSession) -> Any:
    payload = {key: value for key, value in document.items() if key != "_id"}
    if model is User:
        payload["role"] = Role(payload.get("role", "user"))
        return User(**payload)
    if model is Category:
        return Category(**payload)
    if model is Listing:
        payload["status"] = ListingStatus(payload.get("status", ListingStatus.DRAFT.value))
        listing = Listing(**payload)
        image_docs = (
            db.collection("listing_images")
            .find({"listing_id": listing.id})
            .sort("position", 1)
        )
        listing.images = [
            ListingImage(**{key: value for key, value in image_doc.items() if key != "_id"})
            for image_doc in image_docs
        ]
        return listing
    if model is ListingImage:
        return ListingImage(**payload)
    if model is Message:
        return Message(**payload)
    raise TypeError(f"Unsupported entity type: {model!r}")


def _create_client() -> MongoClient:
    return DatabaseClientFactory.create(settings.database_url)


def _resolve_database_name(url: str) -> str:
    database_name = url.rsplit("/", maxsplit=1)[-1]
    database_name = database_name.split("?", maxsplit=1)[0]
    return database_name or "bulletin_board"


client = _create_client()
database = client[_resolve_database_name(settings.database_url)]


def get_db() -> Generator[DatabaseSession, None, None]:
    db = DatabaseSession(database)
    try:
        yield db
    finally:
        db.close()


def initialize_database(target_database: Database | None = None) -> None:
    active_database = target_database or database
    existing_collections = set(active_database.list_collection_names())
    for collection_name in ("users", "categories", "listings", "listing_images", "messages"):
        if collection_name not in existing_collections:
            active_database.create_collection(collection_name)
    active_database["users"].create_index([("email", ASCENDING)], unique=True)
    active_database["categories"].create_index([("name", ASCENDING)], unique=True)
    active_database["listings"].create_index([("status", ASCENDING), ("created_at", DESCENDING)])
    active_database["listing_images"].create_index(
        [("listing_id", ASCENDING), ("position", ASCENDING)]
    )
    active_database["messages"].create_index(
        [("listing_id", ASCENDING), ("created_at", DESCENDING)]
    )
    logger.info(
        "MongoDB initialized database=%s collections=%s",
        active_database.name,
        ",".join(sorted(active_database.list_collection_names())),
    )


def reset_database(db: DatabaseSession) -> None:
    for collection_name in (
        "users",
        "categories",
        "listings",
        "listing_images",
        "messages",
        "counters",
    ):
        db.collection(collection_name).delete_many({})


def safe_insert(entity: Any, db: DatabaseSession) -> Any:
    try:
        db.add(entity)
        db.commit()
        return entity
    except DuplicateKeyError as exc:
        raise ValueError("Duplicate key") from exc
