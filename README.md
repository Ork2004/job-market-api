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
- [ ] FastAPI service with health check
- [ ] PostgreSQL storage layer (normalized vacancy data) + migrations
- [ ] MongoDB storage layer (raw scraped payloads)
- [ ] Ingestion script (public job board API → Mongo → Postgres)
- [ ] Redis caching layer for expensive analytics queries
- [ ] Analytics endpoints powered by pandas/polars
- [ ] Dockerfile + docker-compose for one-command local run
- [ ] Test suite (pytest) with CI enforcement
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

Setup instructions will be added as the corresponding pieces land
(dependencies are introduced in the next commit).

## License

MIT
