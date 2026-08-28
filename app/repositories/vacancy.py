from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vacancy import Vacancy


def list_vacancies(db: Session, *, skip: int = 0, limit: int = 20) -> list[Vacancy]:
    stmt = select(Vacancy).order_by(Vacancy.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_vacancy(db: Session, vacancy_id: int) -> Vacancy | None:
    return db.get(Vacancy, vacancy_id)


def list_for_analytics(db: Session) -> list[dict[str, Any]]:
    """Bare columns needed for salary analytics -- a full ORM load would
    pull description/url/etc. that pandas never touches."""
    stmt = select(
        Vacancy.id,
        Vacancy.location,
        Vacancy.employment_type,
        Vacancy.company,
        Vacancy.currency,
        Vacancy.salary_min,
        Vacancy.salary_max,
    )
    return [dict(row) for row in db.execute(stmt).mappings()]
