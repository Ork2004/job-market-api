from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.vacancy import Vacancy


def _seed_vacancy(db_session: Session, **overrides: object) -> Vacancy:
    defaults: dict[str, object] = {
        "external_id": "1",
        "source": "hh.ru",
        "title": "Backend Developer",
        "company": "Acme",
        "url": "https://example.com/1",
    }
    defaults.update(overrides)
    vacancy = Vacancy(**defaults)
    db_session.add(vacancy)
    db_session.commit()
    db_session.refresh(vacancy)
    return vacancy


def test_list_vacancies_returns_seeded_data(client: TestClient, db_session: Session) -> None:
    _seed_vacancy(db_session)

    response = client.get("/vacancies")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Backend Developer"
    assert body[0]["skills"] == []


def test_list_vacancies_respects_limit(client: TestClient, db_session: Session) -> None:
    for i in range(3):
        _seed_vacancy(db_session, external_id=str(i), url=f"https://example.com/{i}")

    response = client.get("/vacancies", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_vacancy_returns_single_record(client: TestClient, db_session: Session) -> None:
    vacancy = _seed_vacancy(db_session, title="Data Engineer")

    response = client.get(f"/vacancies/{vacancy.id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Data Engineer"


def test_get_vacancy_404_when_missing(client: TestClient) -> None:
    response = client.get("/vacancies/999")

    assert response.status_code == 404
