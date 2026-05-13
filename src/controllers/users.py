from fastapi import APIRouter, Depends, status

from src.core.security import get_current_user, require_role
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import DeleteResponseDTO, UserAdminUpdateDTO, UserReadDTO, UserUpdateDTO
from src.models.entities import Role, User
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)) -> UserReadDTO:
    return current_user


@router.patch("/me")
def update_me(
    payload: UserUpdateDTO,
    db: DatabaseSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserReadDTO:
    return UserService(db).update_self(current_user, payload)


@router.get("")
def list_users(
    db: DatabaseSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> list[UserReadDTO]:
    return UserService(db).list_all()


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: DatabaseSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> UserReadDTO:
    return UserService(db).get_by_id(user_id)


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    payload: UserAdminUpdateDTO,
    db: DatabaseSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> UserReadDTO:
    return UserService(db).update_by_admin(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: DatabaseSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> DeleteResponseDTO:
    UserService(db).delete(user_id)
    return DeleteResponseDTO(message="User deleted")
