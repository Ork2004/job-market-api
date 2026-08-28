from pydantic import BaseModel


class SalaryStatsItem(BaseModel):
    group: str
    currency: str
    vacancy_count: int
    avg_salary: float
    min_salary: float | None
    max_salary: float | None
