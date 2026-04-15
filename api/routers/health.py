"""Health / liveness probe endpoint."""

from fastapi import APIRouter

from api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> dict[str, str]:
    """Liveness probe — returns 200 if the service is up."""
    return {"status": "ok"}
