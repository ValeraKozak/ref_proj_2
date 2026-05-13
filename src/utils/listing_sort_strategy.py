from __future__ import annotations

from dataclasses import dataclass

from pymongo import ASCENDING, DESCENDING


@dataclass(frozen=True)
class ListingSortStrategy:
    primary_field: str
    primary_direction: int
    fallback_field: str = "id"
    fallback_direction: int = DESCENDING

    def to_mongo_sort(self) -> list[tuple[str, int]]:
        return [
            (self.primary_field, self.primary_direction),
            (self.fallback_field, self.fallback_direction),
        ]


class ListingSortStrategyFactory:
    @staticmethod
    def build(sort_by: str = "created_at", sort_order: str = "desc") -> ListingSortStrategy:
        direction = ASCENDING if sort_order == "asc" else DESCENDING
        primary_field = "price" if sort_by == "price" else "created_at"
        return ListingSortStrategy(primary_field=primary_field, primary_direction=direction)
