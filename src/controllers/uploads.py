from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.core.config import get_settings
from src.core.security import get_current_user
from src.dto.schemas import UploadImageBatchDTO, UploadImageReadDTO
from src.models.entities import User

router = APIRouter(prefix="/uploads", tags=["uploads"])
settings = get_settings()

ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_FILES_PER_REQUEST = 6
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


def _detect_image_extension(contents: bytes) -> str | None:
    if contents.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if contents.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if contents.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if len(contents) >= 12 and contents.startswith(b"RIFF") and contents[8:12] == b"WEBP":
        return ".webp"
    return None


def _ensure_upload_request_allowed(current_user: User, files: list[UploadFile]) -> None:
    if current_user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Blocked users cannot upload images",
        )
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can upload at most {MAX_FILES_PER_REQUEST} images at once",
        )


def _resolve_upload_dir() -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _get_declared_extension(file: UploadFile) -> str:
    extension = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {file.content_type or 'unknown'}",
        )
    return extension


def _validate_file_contents(file: UploadFile, contents: bytes, expected_extension: str) -> None:
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {file.filename or 'image'} is empty",
        )
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {file.filename or 'image'} is larger than 5 MB",
        )
    detected_extension = _detect_image_extension(contents)
    if detected_extension != expected_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {file.filename or 'image'} does not match the declared image type",
        )


async def _store_upload_file(file: UploadFile, upload_dir: Path) -> UploadImageReadDTO:
    extension = _get_declared_extension(file)
    contents = await file.read()
    _validate_file_contents(file, contents, extension)

    with NamedTemporaryFile(
        dir=upload_dir,
        prefix=f"{uuid4().hex}-",
        suffix=extension,
        delete=False,
    ) as temporary_file:
        temporary_file.write(contents)
        filename = Path(temporary_file.name).name

    return UploadImageReadDTO(url=f"{settings.uploads_url_prefix.rstrip('/')}/{filename}")


@router.post("/images", status_code=201)
async def upload_images(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadImageBatchDTO:
    _ensure_upload_request_allowed(current_user, files)
    upload_dir = _resolve_upload_dir()
    uploaded_files = [await _store_upload_file(file, upload_dir) for file in files]

    return UploadImageBatchDTO(files=uploaded_files)
