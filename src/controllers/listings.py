from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security import get_current_user, require_role
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import DeleteResponseDTO, ListingCreateDTO, ListingReadDTO, ListingUpdateDTO
from src.models.entities import Role, User
from src.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])
optional_bearer = HTTPBearer(auto_error=False)


@router.post("", status_code=201)
def create_listing(
    payload: ListingCreateDTO,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListingReadDTO:
    return ListingService(db).create(payload, current_user)


@router.put("/{listing_id}")
def update_listing(
    listing_id: int,
    payload: ListingUpdateDTO,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListingReadDTO:
    return ListingService(db).update(listing_id, payload, current_user)


@router.get("")
def public_listings(
    db: DatabaseSession = Depends(get_db),
    query: str | None = Query(default=None, min_length=1, max_length=100),
    category_id: int | None = Query(default=None, gt=0),
    min_price: float | None = Query(default=None, gt=0),
    max_price: float | None = Query(default=None, gt=0),
    sort_by: Literal["created_at", "price"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
) -> list[ListingReadDTO]:
    return ListingService(db).get_public(
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/me/owned")
def my_listings(
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ListingReadDTO]:
    return ListingService(db).get_owned(current_user)


@router.get("/moderation/pending")
def moderation_queue(
    db: DatabaseSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN, Role.MODERATOR)),
) -> list[ListingReadDTO]:
    return ListingService(db).get_for_moderation()


@router.get("/{listing_id}")
def get_listing(
    listing_id: int,
    db: DatabaseSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
) -> ListingReadDTO:
    current_user = None
    if credentials is not None:
        current_user = get_current_user(credentials=credentials, db=db)
    return ListingService(db).get_by_id(listing_id, current_user)


@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeleteResponseDTO:
    return ListingService(db).delete(listing_id, current_user)
