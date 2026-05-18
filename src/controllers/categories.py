from typing import Annotated

from fastapi import APIRouter, Depends

from src.core.security import require_role
from src.db.database import DatabaseSession, get_db
from src.dto.schemas import CategoryCreateDTO, CategoryReadDTO, CategoryUpdateDTO, DeleteResponseDTO
from src.models.entities import Role, User
from src.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

DbSessionDep = Annotated[DatabaseSession, Depends(get_db)]
ModeratorUserDep = Annotated[User, Depends(require_role(Role.ADMIN, Role.MODERATOR))]
AdminUserDep = Annotated[User, Depends(require_role(Role.ADMIN))]


@router.post("", status_code=201)
def create_category(
    payload: CategoryCreateDTO,
    db: DbSessionDep,
    _: ModeratorUserDep,
) -> CategoryReadDTO:
    return CategoryService(db).create(payload)


@router.get("")
def list_categories(db: DbSessionDep) -> list[CategoryReadDTO]:
    return CategoryService(db).list_all()


@router.get("/{category_id}")
def get_category(category_id: int, db: DbSessionDep) -> CategoryReadDTO:
    return CategoryService(db).get_by_id(category_id)


@router.put("/{category_id}")
def update_category(
    category_id: int,
    payload: CategoryUpdateDTO,
    db: DbSessionDep,
    _: ModeratorUserDep,
) -> CategoryReadDTO:
    return CategoryService(db).update(category_id, payload)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: DbSessionDep,
    _: AdminUserDep,
) -> DeleteResponseDTO:
    CategoryService(db).delete(category_id)
    return DeleteResponseDTO(message="Category deleted")
