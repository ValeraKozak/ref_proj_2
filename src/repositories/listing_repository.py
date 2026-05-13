from datetime import datetime
from re import escape

from pymongo import DESCENDING

from src.models.entities import Category, Listing, ListingStatus
from src.repositories.base import Repository
from src.utils.listing_sort_strategy import ListingSortStrategyFactory


class ListingRepository(Repository[Listing]):
    def __init__(self, db):
        super().__init__(db, Listing)

    def list_visible(
        self,
        *,
        query: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[Listing]:
        mongo_query: dict[str, object] = {"status": ListingStatus.APPROVED.value}
        if category_id is not None:
            mongo_query["category_id"] = category_id
        if min_price is not None or max_price is not None:
            price_filter: dict[str, float] = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            mongo_query["price"] = price_filter
        if query:
            category_ids = [
                category.id
                for category in self.db.find_many(
                    Category,
                    {"name": {"$regex": escape(query.strip()), "$options": "i"}},
                )
            ]
            mongo_query["$or"] = [
                {"title": {"$regex": escape(query.strip()), "$options": "i"}},
                {"description": {"$regex": escape(query.strip()), "$options": "i"}},
                {"category_id": {"$in": category_ids or [-1]}},
            ]

        sort_strategy = ListingSortStrategyFactory.build(sort_by=sort_by, sort_order=sort_order)
        return self.db.find_many(
            Listing,
            mongo_query,
            sort=sort_strategy.to_mongo_sort(),
        )

    def list_for_moderation(self) -> list[Listing]:
        return self.db.find_many(
            Listing,
            {"status": ListingStatus.PENDING.value},
            sort=[("created_at", DESCENDING), ("id", DESCENDING)],
        )

    def list_owned(self, owner_id: int) -> list[Listing]:
        return self.db.find_many(
            Listing,
            {"owner_id": owner_id},
            sort=[("created_at", DESCENDING), ("id", DESCENDING)],
        )

    def touch(self, listing: Listing) -> None:
        listing.updated_at = datetime.utcnow()
