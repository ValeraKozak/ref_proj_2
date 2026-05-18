import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.controllers import auth, categories, listings, messages, moderation, uploads, users
from src.core.config import get_settings
from src.db.database import initialize_database

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("bulletin_board")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    initialize_database()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "REST API for managing listings, categories, moderation workflows "
            "and messages."
        ),
        contact={"name": "Course Project Maintainer", "email": "maintainer@example.com"},
        lifespan=lifespan,
    )
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    allowed_origins = settings.frontend_origins_list
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    application.include_router(auth.router)
    application.include_router(categories.router)
    application.include_router(listings.router)
    application.include_router(messages.router)
    application.include_router(moderation.router)
    application.include_router(uploads.router)
    application.include_router(users.router)
    application.mount(
        settings.uploads_url_prefix,
        StaticFiles(directory=settings.upload_dir),
        name="uploads",
    )
    return application


app = create_app()


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
