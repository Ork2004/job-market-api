import httpx
import mongomock

from scripts.ingest_vacancies import ingest


def _mock_client(items: list[dict[str, object]], pages: int = 1) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": items, "pages": pages})

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_ingest_stores_raw_payload_per_vacancy() -> None:
    items = [
        {"id": "1", "name": "Backend Developer"},
        {"id": "2", "name": "Data Engineer"},
    ]
    collection = mongomock.MongoClient().db.raw_vacancies

    count = ingest("python", pages=1, collection=collection, client=_mock_client(items))

    assert count == 2
    stored = {doc["external_id"]: doc for doc in collection.find()}
    assert set(stored) == {"1", "2"}
    assert stored["1"]["source"] == "hh.ru"
    assert stored["1"]["payload"] == items[0]
    assert "fetched_at" in stored["1"]


def test_ingest_upserts_instead_of_duplicating() -> None:
    items = [{"id": "1", "name": "Backend Developer"}]
    collection = mongomock.MongoClient().db.raw_vacancies

    ingest("python", pages=1, collection=collection, client=_mock_client(items))
    ingest("python", pages=1, collection=collection, client=_mock_client(items))

    assert collection.count_documents({}) == 1


def test_ingest_returns_zero_when_no_results() -> None:
    collection = mongomock.MongoClient().db.raw_vacancies

    count = ingest("nonexistent-role-xyz", pages=1, collection=collection, client=_mock_client([]))

    assert count == 0
    assert collection.count_documents({}) == 0
