from fastapi import APIRouter, Depends

from src.core.security import get_current_user
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import DeleteResponseDTO, MessageCreateDTO, MessageReadDTO
from src.models.entities import User
from src.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", status_code=201)
def send_message(
    payload: MessageCreateDTO,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageReadDTO:
    return MessageService(db).send(payload, current_user)


@router.get("/me")
def my_messages(
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageReadDTO]:
    return MessageService(db).list_user_messages(current_user.id)


@router.get("/{message_id}")
def get_message(
    message_id: int,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageReadDTO:
    return MessageService(db).get_user_message(message_id, current_user.id)


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeleteResponseDTO:
    return MessageService(db).delete_user_message(message_id, current_user.id)
