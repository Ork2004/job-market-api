from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DbSession
from app.models.vacancy import Vacancy
from app.repositories import vacancy as vacancy_repo
from app.schemas.vacancy import VacancyOut

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=list[VacancyOut])
def list_vacancies(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[Vacancy]:
    return vacancy_repo.list_vacancies(db, skip=skip, limit=limit)


@router.get("/{vacancy_id}", response_model=VacancyOut)
def get_vacancy(vacancy_id: int, db: DbSession) -> Vacancy:
    vacancy = vacancy_repo.get_vacancy(db, vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy
