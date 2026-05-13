from fastapi import APIRouter, Depends

from src.core.security import require_role
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import ListingReadDTO, ModerationDecisionDTO
from src.models.entities import Role, User
from src.services.moderation_service import ModerationService

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.post("/listings/{listing_id}")
def review_listing(
    listing_id: int,
    payload: ModerationDecisionDTO,
    db: DatabaseSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN, Role.MODERATOR)),
) -> ListingReadDTO:
    return ModerationService(db).review(listing_id, payload)
