import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.ai.chat_message import ChatMessage
from app.ai.service import AIGatewayService
from app.core.dependencies import get_llm_gateway
from app.core.logging import get_logger
from app.models.api_response import ApiResponse

log = get_logger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

Gateway = Annotated[AIGatewayService, Depends(get_llm_gateway)]


class ChatRequest(BaseModel):
    message: str
    system: str | None = None


class ChatData(BaseModel):
    response: str
    provider: str | None


@router.get("/health", response_model=ApiResponse[dict[str, str]])
def ai_health(gateway: Gateway) -> ApiResponse[dict[str, str]]:
    return ApiResponse(data=gateway.health())


@router.get("/providers", response_model=ApiResponse[list[dict[str, Any]]])
def ai_providers(gateway: Gateway) -> ApiResponse[list[dict[str, Any]]]:
    return ApiResponse(data=gateway.provider_statuses())


@router.get("/stats", response_model=ApiResponse[dict[str, Any]])
def ai_stats(gateway: Gateway) -> ApiResponse[dict[str, Any]]:
    return ApiResponse(data=gateway.stats())


@router.post("/chat", response_model=ApiResponse[ChatData])
async def ai_chat(payload: ChatRequest, gateway: Gateway) -> ApiResponse[ChatData]:
    """Manual verification endpoint for the AI gateway.

    Lets you confirm at least one AI_PROVIDER_ORDER provider is wired up
    correctly end-to-end.
    Phase 3 (text-to-sql) introduces the real /query endpoint on top of the
    same AIGatewayService — this route stays as a general-purpose smoke test.

    AIGatewayError is intentionally not caught here — the global handler
    registered in app/middleware/exceptions.py renders it as a standard
    503 error envelope, so every route gets consistent error handling for
    free instead of repeating this try/except per endpoint.
    """
    response = await gateway.chat([ChatMessage.user(payload.message)], system=payload.system)
    return ApiResponse(data=ChatData(response=response, provider=gateway.last_used_provider))


@router.post("/chat/stream")
async def ai_chat_stream(payload: ChatRequest, gateway: Gateway) -> StreamingResponse:
    """SSE variant of /chat, reusing AIGatewayService.stream_chat as-is.

    Errors raised mid-stream happen after headers are already sent, so the
    normal exception-handler middleware can't render them — they're caught
    here and emitted as an `event: error` SSE frame instead.
    """

    async def event_source():
        messages = [ChatMessage.user(payload.message)]
        try:
            async for token in gateway.stream_chat(messages, system=payload.system):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:  # noqa: BLE001 - stream-safe error framing, not a swallow
            log.warning("ai_chat_stream_failed", error=str(exc))
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")
