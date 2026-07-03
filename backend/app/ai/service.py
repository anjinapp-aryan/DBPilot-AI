import time
from collections.abc import AsyncIterator, Awaitable, Callable

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.ai.chat_message import ChatMessage
from app.ai.circuit_breaker import CircuitBreaker, CircuitState
from app.ai.exceptions import AIGatewayError, QuotaExceededError
from app.ai.health import ProviderHealthTracker
from app.ai.metrics import AIMetrics
from app.ai.providers.base import LlmProvider
from app.core.config import Settings
from app.core.logging import get_logger

log = get_logger(__name__)

_RETRYABLE_EXCEPTIONS = (httpx.TransportError, httpx.TimeoutException)


def _is_quota(error: Exception) -> bool:
    return isinstance(error, QuotaExceededError) or "429" in str(error)


def _is_timeout(error: Exception) -> bool:
    return isinstance(error, httpx.TimeoutException) or "timeout" in str(error).lower()


class AIGatewayService:
    """Single entry point for all LLM calls in DBPilot AI.

    Business services depend on this — never on a concrete provider. Routes
    every call through the configured provider order (``AI_PROVIDER_ORDER``)
    with automatic failover, per-provider retry + circuit breaking, health
    tracking, and call metrics. As long as one configured provider succeeds,
    the caller gets a response instead of a raw provider exception.
    """

    def __init__(
        self,
        providers: dict[str, LlmProvider],
        settings: Settings,
        health_tracker: ProviderHealthTracker | None = None,
        metrics: AIMetrics | None = None,
    ) -> None:
        self._providers = providers
        self._settings = settings
        self._health = health_tracker or ProviderHealthTracker()
        self._metrics = metrics or AIMetrics()
        self._breakers: dict[str, CircuitBreaker] = {key: CircuitBreaker() for key in providers}
        self._last_used_provider: str | None = None
        log.info(
            "ai_gateway_initialized",
            order=settings.ai_provider_order_list,
            configured=self._configured_keys(),
            primary=settings.primary_provider,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: list[ChatMessage],
        system: str | None = None,
        temperature: float | None = None,
        preferred_providers: list[str] | None = None,
    ) -> str:
        chain = self._ordered_configured(preferred_providers)
        temp = self._resolve_temperature(temperature)
        result = await self._execute("chat", chain, lambda p: p.chat(messages, system, temp))
        return result

    def stream_chat(
        self,
        messages: list[ChatMessage],
        system: str | None = None,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        chain = self._ordered_configured(None)
        temp = self._resolve_temperature(temperature)
        return self._stream_from(chain, 0, messages, system, temp)

    @property
    def last_used_provider(self) -> str | None:
        return self._last_used_provider

    def _resolve_temperature(self, temperature: float | None) -> float:
        if temperature is not None:
            return temperature
        return self._settings.ai_gateway_default_temperature

    # ------------------------------------------------------------------
    # Blocking (non-streaming) failover core
    # ------------------------------------------------------------------

    async def _execute(
        self,
        op: str,
        chain: list[LlmProvider],
        call: Callable[[LlmProvider], Awaitable[str]],
    ) -> str:
        if not chain:
            raise AIGatewayError("No AI provider is configured", [])

        last_error: Exception | None = None
        for i, provider in enumerate(chain):
            has_next = i < len(chain) - 1
            breaker = self._breakers[provider.name]

            if not breaker.allow_request():
                self._metrics.record_circuit_open(provider.name)
                log.warning(
                    "ai_gateway_provider_skipped",
                    provider=provider.display_name,
                    reason="CIRCUIT_OPEN",
                    depth=i,
                )
                if has_next:
                    self._metrics.record_fallback()
                continue

            try:
                log.info(
                    "ai_gateway_provider_attempt", op=op, provider=provider.display_name, depth=i
                )
                self._metrics.record_call(provider.name)
                start = time.monotonic()
                result = await self._call_with_retry(call, provider)
                elapsed_ms = int((time.monotonic() - start) * 1000)

                if not result.strip():
                    last_error = AIGatewayError(
                        f"{provider.display_name} returned an empty response"
                    )
                    self._metrics.record_failure(provider.name)
                    self._health.record_failure(provider.name, "empty response")
                    breaker.record_failure()
                    log.warning(
                        "ai_gateway_provider_failed",
                        provider=provider.display_name,
                        reason="EMPTY_RESPONSE",
                        depth=i,
                    )
                    if has_next:
                        self._metrics.record_fallback()
                    continue

                self._last_used_provider = provider.name
                self._metrics.record_success(provider.name)
                self._metrics.record_latency(provider.name, elapsed_ms)
                self._health.record_success(provider.name)
                breaker.record_success()
                log.info(
                    "ai_gateway_provider_success",
                    provider=provider.display_name,
                    latency_ms=elapsed_ms,
                    depth=i,
                )
                return result
            except Exception as e:  # noqa: BLE001 - any provider failure triggers failover
                last_error = e
                reason = self._record_failure(provider, e)
                breaker.record_failure()
                if has_next:
                    self._metrics.record_fallback()
                    log.warning(
                        "ai_gateway_provider_failed",
                        provider=provider.display_name,
                        reason=reason,
                        fallback=chain[i + 1].display_name,
                        depth=i,
                    )
                else:
                    log.error(
                        "ai_gateway_provider_failed",
                        provider=provider.display_name,
                        reason=reason,
                        fallback=None,
                        depth=i,
                        chain_length=len(chain),
                        op=op,
                    )

        raise AIGatewayError(
            "All AI providers are unavailable",
            [p.display_name for p in chain],
        ) from last_error

    async def _call_with_retry(
        self, call: Callable[[LlmProvider], Awaitable[str]], provider: LlmProvider
    ) -> str:
        @retry(
            reraise=True,
            stop=stop_after_attempt(2),
            wait=wait_fixed(0.5),
            retry=retry_if_exception_type(_RETRYABLE_EXCEPTIONS),
        )
        async def _attempt() -> str:
            return await call(provider)

        return await _attempt()

    def _record_failure(self, provider: LlmProvider, error: Exception) -> str:
        self._metrics.record_failure(provider.name)
        if _is_quota(error):
            self._metrics.record_rate_limit(provider.name)
            self._health.record_quota_exceeded(provider.name)
            return "RATE_LIMIT"
        if _is_timeout(error):
            self._metrics.record_timeout(provider.name)
            self._health.record_failure(provider.name, "timeout")
            return "TIMEOUT"
        self._health.record_failure(provider.name, str(error))
        return "ERROR"

    # ------------------------------------------------------------------
    # Streaming failover core (fails over only before the first token)
    # ------------------------------------------------------------------

    async def _stream_from(
        self,
        chain: list[LlmProvider],
        idx: int,
        messages: list[ChatMessage],
        system: str | None,
        temperature: float,
    ) -> AsyncIterator[str]:
        if not chain:
            raise AIGatewayError("No AI provider is configured", [])
        if idx >= len(chain):
            raise AIGatewayError(
                "All AI providers are unavailable", [p.display_name for p in chain]
            )

        provider = chain[idx]
        has_next = idx < len(chain) - 1
        breaker = self._breakers[provider.name]

        if not breaker.allow_request():
            self._metrics.record_circuit_open(provider.name)
            log.warning(
                "ai_gateway_provider_skipped",
                provider=provider.display_name,
                reason="CIRCUIT_OPEN",
                depth=idx,
                stream=True,
            )
            if has_next:
                self._metrics.record_fallback()
            async for token in self._stream_from(chain, idx + 1, messages, system, temperature):
                yield token
            return

        self._metrics.record_call(provider.name)
        start = time.monotonic()
        emitted = False
        try:
            async for token in provider.stream_chat(messages, system, temperature):
                emitted = True
                yield token
        except Exception as e:  # noqa: BLE001 - any provider failure triggers failover
            reason = self._record_failure(provider, e)
            breaker.record_failure()
            if emitted:
                # Tokens already streamed to the client — cannot transparently fail over.
                log.error(
                    "ai_gateway_provider_failed",
                    provider=provider.display_name,
                    reason=reason,
                    fallback="NONE_MID_STREAM",
                    depth=idx,
                    stream=True,
                )
                raise
            if has_next:
                self._metrics.record_fallback()
                log.warning(
                    "ai_gateway_provider_failed",
                    provider=provider.display_name,
                    reason=reason,
                    fallback=chain[idx + 1].display_name,
                    depth=idx,
                    stream=True,
                )
            else:
                log.error(
                    "ai_gateway_provider_failed",
                    provider=provider.display_name,
                    reason=reason,
                    fallback=None,
                    depth=idx,
                    chain_length=len(chain),
                    stream=True,
                )
            async for token in self._stream_from(chain, idx + 1, messages, system, temperature):
                yield token
            return

        elapsed_ms = int((time.monotonic() - start) * 1000)
        self._last_used_provider = provider.name
        self._metrics.record_success(provider.name)
        self._metrics.record_latency(provider.name, elapsed_ms)
        self._health.record_success(provider.name)
        breaker.record_success()
        log.info(
            "ai_gateway_provider_success",
            provider=provider.display_name,
            latency_ms=elapsed_ms,
            depth=idx,
            stream=True,
        )

    # ------------------------------------------------------------------
    # Health / stats
    # ------------------------------------------------------------------

    def health(self) -> dict[str, str]:
        """Provider status keyed by name: UP | DOWN | NOT_CONFIGURED, plus "primary"."""
        out: dict[str, str] = {}
        for key in self._settings.ai_provider_order_list:
            provider = self._providers.get(key)
            if provider is None or not provider.is_configured():
                out[key] = "NOT_CONFIGURED"
            else:
                state = self._breakers[key].state
                out[key] = "DOWN" if state == CircuitState.OPEN else "UP"
        out["primary"] = self._settings.primary_provider
        return out

    def stats(self) -> dict[str, object]:
        return self._metrics.snapshot(self._settings.ai_provider_order_list)

    def provider_statuses(self) -> list[dict[str, object]]:
        """Per-provider status in failover order — backs GET /api/v1/ai/providers."""
        out: list[dict[str, object]] = []
        for key in self._settings.ai_provider_order_list:
            provider = self._providers.get(key)
            configured = provider is not None and provider.is_configured()
            state = self._breakers[key].state if key in self._breakers else CircuitState.CLOSED
            status = (
                "NOT_CONFIGURED"
                if not configured
                else ("DOWN" if state == CircuitState.OPEN else "UP")
            )
            out.append(
                {
                    "name": key,
                    "displayName": provider.display_name if provider else key,
                    "configured": configured,
                    "status": status,
                    "circuitState": state.value,
                    "health": self._health.get_status(key).value,
                }
            )
        return out

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _default_chain(self) -> list[LlmProvider]:
        chain = []
        for key in self._settings.ai_provider_order_list:
            provider = self._providers.get(key)
            if provider is not None and provider.is_configured():
                chain.append(provider)
        return chain

    def _ordered_configured(self, preferred: list[str] | None) -> list[LlmProvider]:
        """Configured providers with ``preferred`` pulled to the front, then the
        rest of the default chain appended for failover. Unknown/unconfigured
        preferences are skipped; a falsy preference yields the default order.
        """
        if not preferred:
            return self._default_chain()
        chain: list[LlmProvider] = []
        for key in preferred:
            provider = self._providers.get(key)
            if provider is not None and provider.is_configured() and provider not in chain:
                chain.append(provider)
        for provider in self._default_chain():
            if provider not in chain:
                chain.append(provider)
        return chain

    def _configured_keys(self) -> list[str]:
        return [p.name for p in self._default_chain()]
