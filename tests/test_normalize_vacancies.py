import datetime as dt

import mongomock
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vacancy import Vacancy
from scripts.normalize_vacancies import normalize

SAMPLE_PAYLOAD = {
    "id": "12345",
    "name": "Python Developer",
    "employer": {"name": "Acme LLC"},
    "area": {"name": "Moscow"},
    "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
    "employment": {"name": "Full time"},
    "snippet": {
        "requirement": "Experience with Django and PostgreSQL.",
        "responsibility": "Develop and maintain backend services.",
    },
    "alternate_url": "https://hh.ru/vacancy/12345",
    "published_at": "2026-08-20T10:00:00+0300",
}


def _raw_doc(payload: dict[str, object], external_id: str = "12345") -> dict[str, object]:
    return {
        "source": "hh.ru",
        "external_id": external_id,
        "fetched_at": dt.datetime.now(dt.UTC),
        "payload": payload,
    }


def test_normalize_creates_vacancy_from_raw_document(db_session: Session) -> None:
    collection = mongomock.MongoClient().db.raw_vacancies
    collection.insert_one(_raw_doc(SAMPLE_PAYLOAD))

    count = normalize(raw_collection=collection, session=db_session)

    assert count == 1
    vacancy = db_session.scalars(select(Vacancy)).one()
    assert vacancy.title == "Python Developer"
    assert vacancy.company == "Acme LLC"
    assert vacancy.location == "Moscow"
    assert vacancy.salary_min == 150000
    assert vacancy.salary_max == 250000
    assert vacancy.currency == "RUR"
    assert vacancy.employment_type == "Full time"
    assert "Django" in (vacancy.description or "")
    assert vacancy.url == "https://hh.ru/vacancy/12345"
    # SQLite drops tzinfo on DateTime(timezone=True) columns on read-back
    # (a dialect limitation, not present on Postgres), so this only checks
    # the wall-clock value that was actually parsed from the payload.
    assert vacancy.published_at is not None
    assert vacancy.published_at.replace(tzinfo=None) == dt.datetime(2026, 8, 20, 10, 0, 0)


def test_normalize_updates_existing_vacancy_instead_of_duplicating(db_session: Session) -> None:
    collection = mongomock.MongoClient().db.raw_vacancies
    collection.insert_one(_raw_doc(SAMPLE_PAYLOAD))
    normalize(raw_collection=collection, session=db_session)

    updated_payload = {**SAMPLE_PAYLOAD, "name": "Senior Python Developer"}
    collection.delete_many({})
    collection.insert_one(_raw_doc(updated_payload))
    count = normalize(raw_collection=collection, session=db_session)

    assert count == 1
    vacancies = db_session.scalars(select(Vacancy)).all()
    assert len(vacancies) == 1
    assert vacancies[0].title == "Senior Python Developer"


def test_normalize_handles_missing_optional_fields(db_session: Session) -> None:
    minimal_payload = {
        "id": "999",
        "name": "Mystery Role",
        "alternate_url": "https://hh.ru/vacancy/999",
    }
    collection = mongomock.MongoClient().db.raw_vacancies
    collection.insert_one(_raw_doc(minimal_payload, external_id="999"))

    count = normalize(raw_collection=collection, session=db_session)

    assert count == 1
    vacancy = db_session.scalars(select(Vacancy)).one()
    assert vacancy.company == "Unknown"
    assert vacancy.location is None
    assert vacancy.salary_min is None
    assert vacancy.salary_max is None
    assert vacancy.currency is None
    assert vacancy.employment_type is None
    assert vacancy.description is None
    assert vacancy.published_at is None
