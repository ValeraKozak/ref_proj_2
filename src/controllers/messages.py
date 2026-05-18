from typing import Annotated

from fastapi import APIRouter, Depends

from src.core.security import get_current_user
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import DeleteResponseDTO, MessageCreateDTO, MessageReadDTO
from src.models.entities import User
from src.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])

DbSessionDep = Annotated[DatabaseSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("", status_code=201)
def send_message(
    payload: MessageCreateDTO,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> MessageReadDTO:
    return MessageService(db).send(payload, current_user)


@router.get("/me")
def my_messages(
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> list[MessageReadDTO]:
    return MessageService(db).list_user_messages(current_user.id)


@router.get("/{message_id}")
def get_message(
    message_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> MessageReadDTO:
    return MessageService(db).get_user_message(message_id, current_user.id)


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> DeleteResponseDTO:
    return MessageService(db).delete_user_message(message_id, current_user.id)
