# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DBPilot AI — an open-source AI copilot for databases (Next.js frontend + FastAPI backend). Currently in early development: Phase 1 (project bootstrap) is on `main`; a substantial AI Gateway subsystem and backend hardening pass are on `feature/ai-gateway` (PR open, not yet merged). See [docs/roadmap.md](docs/roadmap.md) for the full 10-phase plan and [docs/architecture.md](docs/architecture.md) / [docs/agents.md](docs/agents.md) for design rationale.

## Commands

### Backend (`backend/`)

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows Git Bash; PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

uvicorn app.main:app --reload --port 8000   # run locally — http://localhost:8000, docs at /docs

pytest --cov=app --cov-report=term-missing  # full suite with coverage
pytest tests/ai/test_gateway_service.py     # single file
pytest tests/ai/test_gateway_service.py::test_chat_skips_provider_with_open_circuit  # single test

ruff check .          # lint
black .               # format (line-length 100)
mypy app              # type check
```

CI (`.github/workflows/backend-tests.yml`, `lint.yml`) runs the same four checks on Python 3.11 and 3.12 — run all four locally before considering backend work done.

**Backend `.env` location:** `Settings` (`app/core/config.py`) resolves `.env` relative to the **process's working directory**, i.e. `backend/.env` — not the repo-root `.env.example`. Copy/adapt `.env.example` into `backend/.env`, not into the repo root.

### Frontend (`frontend/`)

```bash
npm install
npm run dev            # http://localhost:3000
npm run build
npm run test            # vitest
npm run lint            # eslint (flat config, eslint.config.mjs)
npm run format:check    # prettier
npm run type-check      # tsc --noEmit
```

Note: Next.js 16 removed the `next lint` subcommand — linting runs via `eslint .` directly, not `next lint`.

### Local full stack

```bash
docker compose -f deployment/docker-compose.yml up --build
```

## Architecture

### AI Gateway (`backend/app/ai/`) — the core non-obvious subsystem

Every LLM call in the app goes through `AIGatewayService` (`app/ai/service.py`) — never call a provider directly. It implements automatic failover across a configurable provider chain:

```
DeepSeek (NVIDIA-hosted) → Gemini → Groq → Qwen (NVIDIA-hosted) → OpenRouter
```

configured via `AI_PROVIDER_ORDER` (comma-separated provider keys; `PRIMARY_PROVIDER` names the preferred one). A provider is skipped automatically unless *both* its API key and model env vars are set (`ProviderConfig.api_key`/`model` become `None` otherwise) — see `app/ai/settings.py::build_provider_configs`.

Per-provider resilience, independent of the failover logic itself:
- **Retry** (`app/ai/service.py::_call_with_retry`, via `tenacity`): only for transient `httpx.TransportError`/`TimeoutException`. Quota errors (`QuotaExceededError`, or any "429" in the error string) skip retry and fail over immediately — no wasted retry budget on a rate-limited provider.
- **Circuit breaker** (`app/ai/circuit_breaker.py`): opens after repeated failures, half-opens after a cooldown. Checked *before* a provider is attempted (`breaker.allow_request()`), independent of retry.
- **Health tracking** (`app/ai/health.py`) and **metrics** (`app/ai/metrics.py`): both are updated on every call outcome and back `GET /api/v1/ai/{health,providers,stats}`. An empty string response also counts as a failure — treated the same as a thrown exception.

Two provider transport shapes exist (`app/ai/providers/`):
- `OpenAICompatibleProvider` (base.py's `LlmProvider` subclass) — shared by DeepSeek, Groq, Qwen, OpenRouter (all speak the OpenAI `/chat/completions` protocol). Adding one of these providers is a near-empty subclass (see `groq.py`, `qwen.py`, `openrouter.py`).
- `GeminiProvider` — implements Gemini's native v1beta REST API directly (different request/response shape, different streaming format). `ChatMessage.role` already uses Gemini's own vocabulary (`"user"`/`"model"`), so `GeminiProvider` needs no role remapping, unlike `OpenAICompatibleProvider` which maps `"model"` → `"assistant"`.

Adding a new provider: implement one class in `app/ai/providers/`, add its env vars to `app/core/config.py` + `build_provider_configs`, register it in `app/ai/factory.py::get_ai_gateway` — no other call site changes.

**Env var naming quirk:** `DEEP_SHEEK_NVIDIA_API_KEY` (note the spelling) intentionally matches an upstream sibling project's naming so a `.env` from that project can be reused unmodified. It's aliased in `Settings` via `Field(validation_alias="DEEP_SHEEK_NVIDIA_API_KEY")` — `populate_by_name=True` is required in `model_config` for the plain field name to also work.

### Backend cross-cutting layers (`backend/app/core/`, `backend/app/middleware/`)

- **Structured logging** (`app/core/logging.py`): `configure_logging(settings)` runs once at import time in `main.py`, before the `FastAPI()` app is constructed. Get a logger via `get_logger(__name__)` and log with **short event names + kwargs**, never %-style messages — e.g. `log.info("ai_gateway_provider_success", provider=..., depth=...)` — so fields stay queryable in the JSON output structlog produces outside `development` env. Console-rendered (readable) output only in `development`.
- **Request/trace ID correlation** (`app/middleware/request_id.py`): `RequestIDMiddleware` generates-or-echoes `X-Request-ID`/`X-Trace-ID`, binds both into `structlog.contextvars` for the life of the request (auto-attached to every log line at any call depth, no threading through function signatures), and is added to the app **last** so it's the outermost middleware.
- **Dependency injection** (`app/core/dependencies.py`): routes take `Depends(get_llm_gateway)` etc. rather than importing and calling a singleton factory directly — this is what makes `app.dependency_overrides` usable in tests (see `test_dependency_override_swaps_the_gateway_used_by_routes` in `tests/ai/test_ai_api.py` for the pattern). Each provider still wraps a process-wide singleton underneath (e.g. `get_llm_gateway()` → `get_ai_gateway()`, itself `@lru_cache`d), so injecting it costs nothing extra.
- **Exception handling** (`app/core/exceptions.py` + `app/middleware/exceptions.py`): domain exceptions (`ValidationException`, `DatabaseException`, `AIProviderException`, etc., all subclassing `AppException`) are mapped to a single JSON envelope by handlers registered via FastAPI's `exception_handler` mechanism — deliberately *not* a raw ASGI `BaseHTTPMiddleware`, because that doesn't reliably observe exceptions FastAPI's own routing/validation layer raises internally (e.g. `RequestValidationError`). `AIGatewayError` (from `app.ai.exceptions`, which has no FastAPI dependency) is mapped to `AIProviderException`'s shape at the handler layer rather than making `app.ai` depend on `app.core.exceptions` — keeps the gateway usable outside a web-framework context. Routes should let domain exceptions propagate rather than catching them locally (see `app/api/ai.py`'s `/chat` route, which used to hand-roll its own `HTTPException` and no longer does).
- **Cache / DB / schema-service** (`app/core/cache.py`, `app/core/db.py`, `app/services/schema_service.py`): all intentionally thin. `InMemoryCache` sits behind a `CacheProvider` protocol so a Redis-backed swap later doesn't touch call sites. `app/core/db.py` is just enough async SQLAlchemy plumbing (engine/session/connectivity probe) for DI/health checks to have something concrete — the actual ORM models, Alembic migrations, and repository layer are Phase 2 (Schema Discovery) scope, not yet started. `SchemaService.discover()` is a deliberate `NotImplementedError` stub reserving its DI slot.

### Monorepo layout

```
backend/app/
├── ai/            # AI Gateway: providers, failover service, circuit breaker, health, metrics
├── api/           # HTTP route handlers (thin — delegate to services via DI)
├── core/          # config, logging, exceptions, DI container, db, cache
├── middleware/    # request_id, exceptions (FastAPI exception_handler registrations)
├── agents/        # reserved for Phase 2+ agent implementations (currently empty)
└── services/      # business-logic services (currently just the schema_service stub)
```

Top-level `agents/` and `prompts/` (repo root, distinct from `backend/app/agents/`) hold agent *specs* and LLM *prompt templates* respectively — human-reviewable design docs, separate from the Python implementation.

## Conventions

- Branching: `main` (deployable) / `develop` (integration) / `feature/*`, `bugfix/*`, `hotfix/*`. Commits follow Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `ci:`, `build:`, `chore:`) — see [CONTRIBUTING.md](CONTRIBUTING.md).
- Docs live in `docs/` (architecture, api, database, agents, deployment, security, roadmap, contributing) and are expected to be updated alongside the code change that motivates them, not after.
- Gitleaks scans full git history on every push (`lint.yml`); `gitleaks.toml` at the repo root (note: **no** leading dot — `gitleaks-action` auto-discovers exactly that filename, and it's also set explicitly via `GITLEAKS_CONFIG` in `lint.yml` so config loading doesn't depend on undocumented auto-discovery) allowlists known-safe placeholder credential-shaped test fixtures in `backend/tests/ai/`.
