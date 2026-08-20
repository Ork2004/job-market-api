# Job Market Insights API

A backend service that collects job vacancy data, stores it across
purpose-fit databases, and exposes it through a REST API with
analytics endpoints (salary trends, in-demand skills, etc.).

Built as a portfolio project to demonstrate a realistic backend/data
stack end to end: ingestion → storage → API → analytics → deployment.

## Status

This project is being built incrementally and in the open. Check the
roadmap below for current progress.

- [x] Project scaffolding, tooling, CI-ready structure
- [x] FastAPI service with health check
- [x] PostgreSQL storage layer (`vacancies`, `skills`, many-to-many) + Alembic migrations
- [x] `GET /vacancies` and `GET /vacancies/{id}` endpoints
- [ ] MongoDB storage layer (raw scraped payloads)
- [ ] Ingestion script (public job board API → Mongo → Postgres)
- [ ] Redis caching layer for expensive analytics queries
- [ ] Analytics endpoints powered by pandas/polars
- [x] docker-compose for local Postgres/MongoDB/Redis (not yet smoke-tested — no Docker on the dev machine used so far)
- [ ] Dockerfile for the app itself
- [x] Test suite (pytest), 6 tests passing — CI enforcement still pending
- [ ] GitLab CI/CD pipeline (lint, test, build, deploy)
- [ ] Terraform-provisioned AWS environment

## Tech stack

| Layer          | Choice                          |
|----------------|----------------------------------|
| Language       | Python 3.13                     |
| API            | FastAPI                         |
| Relational DB  | PostgreSQL (normalized data)    |
| Document DB    | MongoDB (raw ingested payloads) |
| Cache          | Redis                           |
| Data analysis  | pandas / polars                 |
| Containers     | Docker, docker-compose          |
| Infrastructure | Terraform (AWS)                 |
| CI/CD          | GitLab CI                       |
| Testing        | pytest                          |
| Linting/typing | ruff, black, mypy               |

## Architecture (target)

```
external job board API
        │
        ▼
  ingestion script ──► MongoDB (raw payloads)
        │
        ▼
  normalization job ──► PostgreSQL (structured vacancies)
        │
        ▼
   FastAPI service ◄── Redis (cache for analytics queries)
        │
        ▼
   REST API consumers
```

## Local development

```bash
python -m venv .venv
.venv/Scripts/activate        # on Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements-dev.txt

cp .env.example .env
docker compose up -d          # starts Postgres, MongoDB and Redis
alembic upgrade head          # creates the vacancies/skills tables

uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for the interactive API docs,
`http://127.0.0.1:8000/health` for the liveness check, or
`http://127.0.0.1:8000/vacancies` for the (empty, until ingestion
exists) vacancies list.

Run the test suite and checks with:

```bash
pytest
ruff check .
black --check .
mypy app
```

## License

MIT
