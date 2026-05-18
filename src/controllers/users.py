from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core.security import get_current_user, require_role
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import DeleteResponseDTO, UserAdminUpdateDTO, UserReadDTO, UserUpdateDTO
from src.models.entities import Role, User
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

DbSessionDep = Annotated[DatabaseSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
AdminUserDep = Annotated[User, Depends(require_role(Role.ADMIN))]


@router.get("/me")
def get_me(current_user: CurrentUserDep) -> UserReadDTO:
    return current_user


@router.patch("/me")
def update_me(
    payload: UserUpdateDTO,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> UserReadDTO:
    return UserService(db).update_self(current_user, payload)


@router.get("")
def list_users(
    db: DbSessionDep,
    _: AdminUserDep,
) -> list[UserReadDTO]:
    return UserService(db).list_all()


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: DbSessionDep,
    _: AdminUserDep,
) -> UserReadDTO:
    return UserService(db).get_by_id(user_id)


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    payload: UserAdminUpdateDTO,
    db: DbSessionDep,
    _: AdminUserDep,
) -> UserReadDTO:
    return UserService(db).update_by_admin(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: DbSessionDep,
    _: AdminUserDep,
) -> DeleteResponseDTO:
    UserService(db).delete(user_id)
    return DeleteResponseDTO(message="User deleted")
