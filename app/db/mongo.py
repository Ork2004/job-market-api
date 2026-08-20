from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection

from app.core.config import settings


@lru_cache
def get_mongo_client() -> MongoClient:
    # pymongo connects lazily, so constructing the client here doesn't
    # require a reachable MongoDB instance until an operation runs.
    return MongoClient(settings.mongo_uri)


def get_raw_vacancies_collection() -> Collection:
    return get_mongo_client()[settings.mongo_db]["raw_vacancies"]


def ensure_indexes(collection: Collection) -> None:
    collection.create_index([("source", 1), ("external_id", 1)], unique=True)
