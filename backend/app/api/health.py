from fastapi import APIRouter

from app.core.config import get_settings
from app.models.api_response import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[dict[str, str]])
def health_check() -> ApiResponse[dict[str, str]]:
    settings = get_settings()
    data = {
        "status": "ok",
        "service": "dbpilot-ai-backend",
        "version": settings.app_version,
    }
    return ApiResponse(data=data)
