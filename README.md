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
- [x] MongoDB storage layer (raw scraped payloads, unique index on source+external_id)
- [x] Ingestion script: hh.ru API → MongoDB (raw) — see note below on running it
- [ ] Normalization job: MongoDB (raw) → PostgreSQL (structured)
- [ ] Redis caching layer for expensive analytics queries
- [ ] Analytics endpoints powered by pandas/polars
- [x] docker-compose for local Postgres/MongoDB/Redis (not yet smoke-tested — no Docker on the dev machine used so far)
- [ ] Dockerfile for the app itself
- [x] Test suite (pytest), 6 tests passing
- [x] `.gitlab-ci.yml`: lint + test stages, test job runs against real Postgres/MongoDB/Redis service containers (⚠️ not yet actually running anywhere — repo lives on GitHub, see note below)
- [ ] Terraform-provisioned AWS environment

> **Note on GitLab CI:** the repo is currently hosted on GitHub. The
> `.gitlab-ci.yml` file is correct but inert until this project is
> either mirrored to GitLab or connected via GitLab's "CI/CD for
> external repositories" — otherwise no pipeline actually runs, and
> there's nothing to point to as evidence in an interview.

> **Note on running the ingestion script:** hh.ru sits behind
> DDoS-Guard, which returns `403 Forbidden` for requests coming from
> datacenter/cloud IP ranges — confirmed with a full browser
> `User-Agent`, so it's IP-reputation-based, not a missing-header
> issue. This means `python -m scripts.ingest_vacancies` will not
> work from most CI runners or cloud VMs; it needs to run from an
> ordinary residential/office connection. The script itself is fully
> unit-tested (`tests/test_ingest_vacancies.py`) with a mocked HTTP
> transport and a fake MongoDB collection, so its correctness doesn't
> depend on hh.ru being reachable from wherever tests run.

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
`http://127.0.0.1:8000/vacancies` for the vacancies list (empty until
both ingestion and the Mongo → Postgres normalization job exist).

To pull raw vacancies into MongoDB (run from a normal, non-cloud IP —
see the hh.ru note above):

```bash
python -m scripts.ingest_vacancies --query python --pages 2
```

Run the test suite and checks with:

```bash
pytest
ruff check .
black --check .
mypy app
```

## License

MIT
