from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SkillOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class VacancyOut(BaseModel):
    id: int
    external_id: str
    source: str
    title: str
    company: str
    location: str | None
    salary_min: int | None
    salary_max: int | None
    currency: str | None
    employment_type: str | None
    url: str
    published_at: datetime | None
    skills: list[SkillOut]

    model_config = ConfigDict(from_attributes=True)
