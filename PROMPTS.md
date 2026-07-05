# PROMPTS.md

Reusable prompts for working on DBPilotAI with Claude/Cursor/Copilot. These are meta-prompts for **building the platform**, distinct from `prompts/` at repo root (which holds runtime LLM prompt templates the platform itself sends to end-user-facing agents, e.g. `prompts/text-to-sql.md`).

## Architecture

```
Review [proposed change] against DBPilotAI's target architecture (ARCHITECTURE.md,
DOMAIN.md). Specifically check: does it respect the Connection/Metadata/Execution
bounded-context boundaries, does it introduce a new Kafka topic without meeting
the criteria in EVENTS.md, does it add tenant-scoped data without a tenant_id
column from the start. Flag violations before proposing implementation.
```

## Backend

```
Implement [feature] in backend/app/ following the existing pattern: domain logic
framework-free, FastAPI routes thin and delegating via Depends() (see
app/core/dependencies.py), structured logging with event-name + kwargs (see
app/core/logging.py), and a test in the same PR. Do not call an LLM provider
directly — go through AIGatewayService/AgentOrchestrator.
```

## AI Agents

```
Implement the [Agent Name] per its spec in AGENTS.md: same responsibilities,
inputs, outputs, tools, and failure-handling — don't diverge from the spec
silently. If the spec looks wrong given what you're learning during
implementation, stop and propose a spec update (new ADR in DECISIONS.md)
rather than quietly building something different.
```

## Security Review

```
Review [change] against SECURITY_ARCHITECTURE.md and CLAUDE.md's Security Rules.
Specifically: does any credential ever touch a log line, trace span, or LLM
prompt; is tenant_id enforced at the query layer (not just assumed from
context); if this touches SQL execution, is there a non-LLM-trusting
validation gate before it.
```

## Code Review

```
Review this PR for: (1) does it match an existing pattern in the codebase
(AI Gateway's failover/circuit-breaker/DI shape) rather than inventing a new
one for the same problem, (2) test coverage for the failure paths, not just
the happy path, (3) any Forbidden Pattern from CLAUDE.md.
```

## Refactoring

```
Refactor [module] toward Hexagonal/Clean Architecture (domain -> application ->
adapters, see CLAUDE.md's Engineering Principles) without changing external
behavior. Confirm existing tests still pass before and after; add tests first
if coverage is missing for the code being moved.
```

## Performance

```
Profile [path] against the SLOs in OBSERVABILITY.md. Check for the two most
common regressions in this codebase: re-running schema discovery/re-embedding
unchanged metadata instead of hitting cache (MEMORY.md), and synchronous
blocking where a streaming response (SSE/WebSocket) should be used.
```

## Testing

```
Write tests for [module] covering: the happy path, the failure path (what
happens when a dependency errors), and — if this is agent/LLM-adjacent — the
case where the model returns malformed/unexpected output. Mirror the existing
test style in backend/tests/ai/ (fixture-based FakeProvider pattern, or
httpx.MockTransport for real transport-layer tests).
```

## Deployment

```
Prepare [service] for deployment per ARCHITECTURE.md's HA/scalability strategy:
stateless, horizontally scalable, health checks distinguish liveness from
readiness, and no assumption that it runs on the same host/process as any
other service.
```
