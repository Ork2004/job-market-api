from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.vacancies import router as vacancies_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(vacancies_router)
