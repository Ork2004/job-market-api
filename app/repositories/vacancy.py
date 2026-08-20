from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vacancy import Vacancy


def list_vacancies(db: Session, *, skip: int = 0, limit: int = 20) -> list[Vacancy]:
    stmt = select(Vacancy).order_by(Vacancy.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_vacancy(db: Session, vacancy_id: int) -> Vacancy | None:
    return db.get(Vacancy, vacancy_id)
