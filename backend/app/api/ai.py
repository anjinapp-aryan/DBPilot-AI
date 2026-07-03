from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.ai.chat_message import ChatMessage
from app.ai.exceptions import AIGatewayError
from app.ai.service import AIGatewayService
from app.core.dependencies import get_llm_gateway

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

Gateway = Annotated[AIGatewayService, Depends(get_llm_gateway)]


class ChatRequest(BaseModel):
    message: str
    system: str | None = None


class ChatResponse(BaseModel):
    response: str
    provider: str | None


@router.get("/health")
def ai_health(gateway: Gateway) -> dict[str, str]:
    return gateway.health()


@router.get("/providers")
def ai_providers(gateway: Gateway) -> list[dict[str, Any]]:
    return gateway.provider_statuses()


@router.get("/stats")
def ai_stats(gateway: Gateway) -> dict[str, Any]:
    return gateway.stats()


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(payload: ChatRequest, gateway: Gateway) -> ChatResponse:
    """Manual verification endpoint for the AI gateway.

    Lets you confirm at least one AI_PROVIDER_ORDER provider is wired up
    correctly end-to-end.
    Phase 3 (text-to-sql) introduces the real /query endpoint on top of the
    same AIGatewayService — this route stays as a general-purpose smoke test.
    """
    try:
        response = await gateway.chat([ChatMessage.user(payload.message)], system=payload.system)
    except AIGatewayError as e:
        raise HTTPException(
            status_code=503,
            detail={"error": str(e), "providerAttempts": e.provider_attempts},
        ) from e
    return ChatResponse(response=response, provider=gateway.last_used_provider)
