from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.vacancy import Vacancy


def _seed(db_session: Session, **overrides: object) -> None:
    defaults: dict[str, object] = {
        "external_id": "1",
        "source": "hh.ru",
        "title": "Backend Developer",
        "company": "Acme",
        "location": "Moscow",
        "currency": "RUR",
        "salary_min": 100_000,
        "salary_max": 150_000,
        "url": "https://example.com/1",
    }
    defaults.update(overrides)
    db_session.add(Vacancy(**defaults))
    db_session.commit()


def test_salary_stats_groups_by_location(client: TestClient, db_session: Session) -> None:
    _seed(db_session, external_id="1", location="Moscow", salary_min=100_000, salary_max=150_000)
    _seed(
        db_session,
        external_id="2",
        location="Remote",
        currency="USD",
        salary_min=2_000,
        salary_max=3_000,
        url="https://example.com/2",
    )

    response = client.get("/analytics/salary-stats", params={"group_by": "location"})

    assert response.status_code == 200
    body = response.json()
    groups = {item["group"]: item for item in body}
    assert groups["Moscow"]["currency"] == "RUR"
    assert groups["Moscow"]["vacancy_count"] == 1
    assert groups["Remote"]["currency"] == "USD"


def test_salary_stats_defaults_to_location(client: TestClient, db_session: Session) -> None:
    _seed(db_session)

    response = client.get("/analytics/salary-stats")

    assert response.status_code == 200
    assert response.json()[0]["group"] == "Moscow"


def test_salary_stats_rejects_invalid_group_by(client: TestClient) -> None:
    response = client.get("/analytics/salary-stats", params={"group_by": "id"})

    assert response.status_code == 400


def test_salary_stats_empty_when_no_vacancies(client: TestClient) -> None:
    response = client.get("/analytics/salary-stats")

    assert response.status_code == 200
    assert response.json() == []
