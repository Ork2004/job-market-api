"""Read raw hh.ru vacancy payloads from MongoDB and upsert them as
structured rows into PostgreSQL.

Skill extraction is intentionally left out: hh.ru's search endpoint
(what the ingestion script calls) doesn't return `key_skills` -- only
the per-vacancy detail endpoint does, and fetching that per posting
would multiply the request count against an API that already blocks
datacenter IPs. The vacancy_skills table is ready for whenever that
detail fetch gets added.

Usage:
    python -m scripts.normalize_vacancies
"""

from __future__ import annotations

import datetime as dt
import sys
from typing import Any

from pymongo.collection import Collection
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.mongo import get_raw_vacancies_collection
from app.db.session import SessionLocal
from app.models.vacancy import Vacancy


def _parse_published_at(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")


def _to_vacancy_fields(document: dict[str, Any]) -> dict[str, Any]:
    payload = document["payload"]
    employer = payload.get("employer") or {}
    area = payload.get("area") or {}
    salary = payload.get("salary") or {}
    employment = payload.get("employment") or {}
    snippet = payload.get("snippet") or {}

    description = (
        "\n\n".join(
            part for part in (snippet.get("requirement"), snippet.get("responsibility")) if part
        )
        or None
    )

    return {
        "external_id": document["external_id"],
        "source": document["source"],
        "title": payload["name"],
        "company": employer.get("name") or "Unknown",
        "location": area.get("name"),
        "salary_min": salary.get("from"),
        "salary_max": salary.get("to"),
        "currency": salary.get("currency"),
        "employment_type": employment.get("name"),
        "description": description,
        "url": payload["alternate_url"],
        "published_at": _parse_published_at(payload.get("published_at")),
    }


def normalize(
    *,
    raw_collection: Collection | None = None,
    session: Session | None = None,
) -> int:
    """Upsert every raw MongoDB document into the vacancies table."""
    collection = raw_collection if raw_collection is not None else get_raw_vacancies_collection()
    owns_session = session is None
    db = session or SessionLocal()

    count = 0
    try:
        for document in collection.find():
            fields = _to_vacancy_fields(document)
            stmt = select(Vacancy).where(
                Vacancy.source == fields["source"],
                Vacancy.external_id == fields["external_id"],
            )
            existing = db.scalars(stmt).one_or_none()
            if existing is None:
                db.add(Vacancy(**fields))
            else:
                for key, value in fields.items():
                    setattr(existing, key, value)
            count += 1
        db.commit()
    finally:
        if owns_session:
            db.close()
    return count


def main() -> None:
    count = normalize()
    print(f"Normalized {count} vacancies into PostgreSQL", file=sys.stderr)


if __name__ == "__main__":
    main()
