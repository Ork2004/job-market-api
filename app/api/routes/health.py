from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Liveness probe used by orchestrators and uptime checks."""
    return {"status": "ok"}
