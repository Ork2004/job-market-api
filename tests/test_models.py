from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.vacancy import Skill, Vacancy


def test_vacancy_can_be_created_with_skills() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        python_skill = Skill(name="python")
        sql_skill = Skill(name="sql")

        vacancy = Vacancy(
            external_id="123",
            source="hh.ru",
            title="Backend Developer",
            company="Acme",
            location="Remote",
            salary_min=1000,
            salary_max=2000,
            currency="USD",
            url="https://example.com/vacancy/123",
            skills=[python_skill, sql_skill],
        )
        session.add(vacancy)
        session.commit()

        stored = session.query(Vacancy).one()
        assert stored.title == "Backend Developer"
        assert {skill.name for skill in stored.skills} == {"python", "sql"}
