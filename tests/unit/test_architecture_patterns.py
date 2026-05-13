from pymongo import ASCENDING, DESCENDING

from src.db.client_factory import DatabaseClientFactory
from src.utils.listing_sort_strategy import ListingSortStrategyFactory


def test_listing_sort_strategy_defaults_to_created_at_desc():
    strategy = ListingSortStrategyFactory.build()
    assert strategy.to_mongo_sort() == [("created_at", DESCENDING), ("id", DESCENDING)]


def test_listing_sort_strategy_supports_price_ascending():
    strategy = ListingSortStrategyFactory.build(sort_by="price", sort_order="asc")
    assert strategy.to_mongo_sort() == [("price", ASCENDING), ("id", DESCENDING)]


def test_listing_sort_strategy_falls_back_for_unknown_field():
    strategy = ListingSortStrategyFactory.build(sort_by="unknown", sort_order="asc")
    assert strategy.to_mongo_sort() == [("created_at", ASCENDING), ("id", DESCENDING)]


def test_database_client_factory_supports_mongomock_urls():
    client = DatabaseClientFactory.create("mongomock://localhost/test_db")
    assert client is not None
    assert client["test_db"] is not None
