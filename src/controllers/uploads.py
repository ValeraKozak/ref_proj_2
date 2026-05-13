from pathlib import Path
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


@router.post("/images", status_code=201)
async def upload_images(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadImageBatchDTO:
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

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files: list[UploadImageReadDTO] = []
    for file in files:
        extension = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
        if extension is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image type: {file.content_type or 'unknown'}",
            )

        contents = await file.read()
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

        filename = f"{uuid4().hex}{extension}"
        destination = upload_dir / filename
        destination.write_bytes(contents)
        uploaded_files.append(
            UploadImageReadDTO(url=f"{settings.uploads_url_prefix.rstrip('/')}/{filename}")
        )

    return UploadImageBatchDTO(files=uploaded_files)
