# API Reference

The backend exposes a versioned REST API under `/api/v1`, plus interactive
OpenAPI docs at `/docs` (Swagger UI) and `/redoc` when running locally.

> This document will grow with each phase. Phase 1 only ships the health
> check endpoint below; subsequent phases add `/connections`, `/schema`,
> `/query`, `/execute`, `/explain`, and `/chart` endpoints as they land.

## Base URL

| Environment | URL |
|---|---|
| Local | `http://localhost:8000` |
| Production | set via `NEXT_PUBLIC_API_BASE_URL` |

## Conventions

- All request/response bodies are JSON.
- **Every successful response uses a standard envelope**
  (`backend/app/models/api_response.py`):
  ```json
  { "success": true, "data": { "...": "..." }, "metadata": {}, "timestamp": "2026-01-01T00:00:00+00:00" }
  ```
- **Every error response** (raised via `app/core/exceptions.py`'s domain
  exceptions, or an unhandled error) uses a matching but distinct envelope,
  rendered by the global handlers in `app/middleware/exceptions.py`:
  ```json
  { "success": false, "error": { "code": "...", "message": "...", "details": [] }, "timestamp": "..." }
  ```
  `error.code` is a stable machine-readable string (e.g. `validation_error`,
  `ai_provider_error`, `internal_error`) — see `app/core/exceptions.py` for
  the full set.
- Endpoints that stream agent progress (schema discovery, text-to-SQL) will
  use WebSocket or Server-Sent Events — documented per-endpoint once
  implemented.

## Endpoints (Phase 1)

### `GET /health`

Liveness/readiness check used by CI, Railway/Render health checks, and local
smoke tests.

**Response `200 OK`**

```json
{
  "success": true,
  "data": { "status": "ok", "service": "dbpilot-ai-backend", "version": "0.1.0" },
  "metadata": {},
  "timestamp": "2026-01-01T00:00:00+00:00"
}
```

## Endpoints — AI Gateway

Backed by `AIGatewayService` (see [docs/agents.md](agents.md#ai-gateway-llm-connectivity-layer)). All wrapped in the standard envelope above — examples below show only the `data` field's shape.

### `GET /api/v1/ai/health`

Per-provider status (`UP` | `DOWN` | `NOT_CONFIGURED`) plus `primary`.

```json
{ "deepseek": "UP", "gemini": "NOT_CONFIGURED", "groq": "UP", "qwen": "NOT_CONFIGURED", "openrouter": "NOT_CONFIGURED", "primary": "deepseek" }
```

### `GET /api/v1/ai/providers`

Per-provider status in failover order: `name`, `displayName`, `configured`, `status`, `circuitState`, `health`.

### `GET /api/v1/ai/stats`

In-memory call metrics per provider (calls/successes/failures/rate limits/timeouts/circuit opens/avg latency) plus a global fallback counter.

### `POST /api/v1/ai/chat`

Manual verification endpoint — sends a single message through the gateway's
failover chain. Returns `503` with the standard error envelope
(`error.code: "ai_provider_error"`, `error.details: [{"providerAttempts": [...]}]`)
if every configured provider fails or none are configured.

```json
// Request
{ "message": "hello", "system": null }
// Response data
{ "response": "...", "provider": "deepseek" }
```

## Planned Endpoints

| Phase | Endpoint | Purpose |
|---|---|---|
| 2 | `POST /api/v1/connections` | Register a target database connection |
| 2 | `GET /api/v1/connections/{id}/schema` | Fetch discovered schema |
| 3 | `POST /api/v1/query` | Natural language question → generated SQL |
| 4 | (internal) | SQL validation is applied before execution, not user-invoked |
| 5 | `POST /api/v1/execute` | Execute a validated SQL statement |
| 6 | `POST /api/v1/explain` | Get a plain-English explanation of a SQL statement |
| 7 | `POST /api/v1/voice/transcribe` | Optional server-side voice fallback |
| 8 | `POST /api/v1/chart` | Suggest/generate a chart spec for a result set |

This table will be replaced by generated OpenAPI reference links as each
endpoint ships.
