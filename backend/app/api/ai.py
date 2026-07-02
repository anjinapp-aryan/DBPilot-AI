from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import AIGatewayError
from app.ai.factory import get_ai_gateway

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str
    system: str | None = None


class ChatResponse(BaseModel):
    response: str
    provider: str | None


@router.get("/health")
def ai_health() -> dict[str, str]:
    return get_ai_gateway().health()


@router.get("/providers")
def ai_providers() -> list[dict[str, Any]]:
    return get_ai_gateway().provider_statuses()


@router.get("/stats")
def ai_stats() -> dict[str, Any]:
    return get_ai_gateway().stats()


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(payload: ChatRequest) -> ChatResponse:
    """Manual verification endpoint for the AI gateway.

    Lets you confirm at least one AI_PROVIDER_ORDER provider is wired up
    correctly end-to-end.
    Phase 3 (text-to-sql) introduces the real /query endpoint on top of the
    same AIGatewayService — this route stays as a general-purpose smoke test.
    """
    gateway = get_ai_gateway()
    try:
        response = await gateway.chat([ChatMessage.user(payload.message)], system=payload.system)
    except AIGatewayError as e:
        raise HTTPException(
            status_code=503,
            detail={"error": str(e), "providerAttempts": e.provider_attempts},
        ) from e
    return ChatResponse(response=response, provider=gateway.last_used_provider)
