from fastapi import APIRouter, HTTPException, Query

from app.analytics.salary import ALLOWED_GROUP_BY_FIELDS, InvalidGroupByField, salary_stats_by
from app.api.deps import DbSession
from app.repositories import vacancy as vacancy_repo
from app.schemas.analytics import SalaryStatsItem

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/salary-stats", response_model=list[SalaryStatsItem])
def salary_stats(
    db: DbSession,
    group_by: str = Query("location", description="location, employment_type, or company"),
) -> list[dict[str, object]]:
    rows = vacancy_repo.list_for_analytics(db)
    try:
        return salary_stats_by(rows, group_by)
    except InvalidGroupByField as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid group_by '{exc}'. Allowed: {sorted(ALLOWED_GROUP_BY_FIELDS)}",
        ) from exc
