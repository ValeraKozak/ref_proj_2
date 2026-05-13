import logging

from fastapi import HTTPException, status

from src.db.database import DatabaseSession
from src.dto.schemas import DeleteResponseDTO, ListingCreateDTO, ListingUpdateDTO
from src.models.entities import Category, Listing, ListingImage, ListingStatus, Role, User
from src.repositories.listing_repository import ListingRepository

logger = logging.getLogger(__name__)
LISTING_NOT_FOUND_DETAIL = "Listing not found"


class ListingService:
    def __init__(self, db: DatabaseSession) -> None:
        self.db = db
        self.listings = ListingRepository(db)

    def create(self, payload: ListingCreateDTO, owner: User) -> Listing:
        if owner.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Blocked users cannot post",
            )
        category = self.db.get(Category, payload.category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        listing = Listing(
            title=payload.title.strip(),
            description=payload.description.strip(),
            price=payload.price,
            category_id=payload.category_id,
            owner_id=owner.id,
            status=ListingStatus.PENDING,
        )
        self._set_images(listing, payload.image_urls)
        self.listings.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        self._enrich_listing(listing)
        logger.info("Listing created listing_id=%s owner_id=%s", listing.id, owner.id)
        return listing

    def update(self, listing_id: int, payload: ListingUpdateDTO, owner: User) -> Listing:
        listing = self._get_owned_listing(listing_id, owner.id)
        if payload.category_id is not None and self.db.get(Category, payload.category_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        for field, value in payload.model_dump(exclude_none=True, exclude={"image_urls"}).items():
            setattr(listing, field, value.strip() if isinstance(value, str) else value)
        if payload.image_urls is not None:
            self._set_images(listing, payload.image_urls)
        listing.status = ListingStatus.PENDING
        listing.rejection_reason = None
        self.db.commit()
        self.db.refresh(listing)
        self._enrich_listing(listing)
        logger.info("Listing updated listing_id=%s owner_id=%s", listing.id, owner.id)
        return listing

    def get_public(
        self,
        *,
        query: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[Listing]:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price",
            )
        listings = self.listings.list_visible(
            query=query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return self._enrich_listings(listings)

    def get_by_id(self, listing_id: int, current_user: User | None = None) -> Listing:
        listing = self.db.get(Listing, listing_id)
        if listing is None:
            self._raise_listing_not_found()
        if listing.status == ListingStatus.APPROVED:
            self._enrich_listing(listing)
            return listing
        if not self._can_view_unpublished_listing(listing, current_user):
            self._raise_listing_not_found()
        self._enrich_listing(listing)
        return listing

    def get_owned(self, owner: User) -> list[Listing]:
        return self._enrich_listings(self.listings.list_owned(owner.id))

    def get_for_moderation(self) -> list[Listing]:
        return self._enrich_listings(self.listings.list_for_moderation())

    def delete(self, listing_id: int, owner: User) -> DeleteResponseDTO:
        listing = self._get_owned_listing(listing_id, owner.id)
        self.listings.delete(listing)
        self.db.commit()
        logger.info("Listing deleted listing_id=%s owner_id=%s", listing.id, owner.id)
        return DeleteResponseDTO(message="Listing deleted")

    def _get_owned_listing(self, listing_id: int, owner_id: int) -> Listing:
        listing = self.db.get(Listing, listing_id)
        if listing is None:
            self._raise_listing_not_found()
        if listing.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your listing")
        return listing

    @staticmethod
    def _can_view_unpublished_listing(listing: Listing, current_user: User | None) -> bool:
        if current_user is None:
            return False
        return current_user.id == listing.owner_id or current_user.role in {
            Role.ADMIN,
            Role.MODERATOR,
        }

    @staticmethod
    def _raise_listing_not_found() -> None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LISTING_NOT_FOUND_DETAIL,
        )

    @staticmethod
    def _set_images(listing: Listing, image_urls) -> None:
        listing.images = [
            ListingImage(url=str(image_url), position=index)
            for index, image_url in enumerate(image_urls)
        ]

    def _enrich_listing(self, listing: Listing) -> Listing:
        if listing.owner_id is not None:
            owner = self.db.get(User, listing.owner_id)
            listing.owner_name = owner.full_name if owner is not None else None
        return listing

    def _enrich_listings(self, listings: list[Listing]) -> list[Listing]:
        return [self._enrich_listing(listing) for listing in listings]
