from __future__ import annotations

from pymongo import MongoClient

try:  # pragma: no cover - optional test dependency
    import mongomock
except ImportError:  # pragma: no cover - optional test dependency
    mongomock = None


class DatabaseClientFactory:
    @staticmethod
    def create(database_url: str) -> MongoClient:
        if database_url.startswith("mongomock://"):
            if mongomock is None:
                raise RuntimeError("mongomock is required for mongomock:// database URLs")
            return mongomock.MongoClient()
        return MongoClient(database_url, tz_aware=True)
