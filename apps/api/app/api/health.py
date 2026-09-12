from fastapi import APIRouter
from app.schemas.models import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="ngx-research-api", version="0.1.0")