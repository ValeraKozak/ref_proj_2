from fastapi import APIRouter, Depends

from src.db.database import DatabaseSession, get_db
from src.dto.schemas import TokenDTO, UserCreateDTO, UserLoginDTO, UserReadDTO
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: UserCreateDTO, db: DatabaseSession = Depends(get_db)) -> UserReadDTO:
    return AuthService(db).register(payload)


@router.post("/login")
def login(payload: UserLoginDTO, db: DatabaseSession = Depends(get_db)) -> TokenDTO:
    return AuthService(db).login(payload)
