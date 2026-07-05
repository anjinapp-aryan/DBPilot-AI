# DECISIONS.md

Architecture Decision Record framework + the log itself.

## ADR Template

```markdown
## ADR-NNN: <title>
**Status:** Proposed | Accepted | Superseded by ADR-XXX | Deprecated
**Date:** YYYY-MM-DD
**Owner:** <role/team>

### Context
What problem/tension forced this decision.

### Decision
What we're doing.

### Consequences
What this makes easier, what it makes harder, what it forecloses.

### Alternatives Considered
What else was on the table and why it lost.
```

## Decision Categories

`STACK` (language/framework choices), `ARCH` (structural architecture), `AI` (agent/LLM design), `DATA` (database/storage), `SEC` (security), `OPS` (deployment/infra), `PRODUCT` (scope/sequencing).

## Decision Ownership

`STACK`/`ARCH`/`AI` decisions require sign-off from whoever holds the Staff/Principal Engineer role for the affected area; `SEC` decisions additionally require security review; `PRODUCT` decisions require product owner sign-off. All decisions are recorded here regardless of who approved them — an undocumented decision is treated as not yet decided.

## Review Process

New ADRs are proposed via PR (the ADR entry itself is the PR's primary content), reviewed by the relevant owner above, merged as `Accepted` once approved. A later decision that changes course adds a **new** ADR marking the old one `Superseded by ADR-XXX` — existing ADRs are never edited to silently change their recorded decision (see [CLAUDE.md](CLAUDE.md) — this file is itself the source of truth for "why," and truth shouldn't be rewritten after the fact).

---

## The Log (Top 25)

### ADR-001: Backend on Python/FastAPI, not Java/Spring
**Status:** Accepted | **Category:** STACK
Context: initial enterprise architecture template assumed Java/Spring Boot. Decision: Python/FastAPI — matches the existing AI-heavy ecosystem (LLM SDKs, data tooling), matches what's already built (`app/ai/`), avoids a costly rewrite. Consequences: loses some of Spring's batteries-included enterprise tooling (Spring Security, Spring Data) — those get custom-built or use Python equivalents (Authlib, SQLAlchemy).

### ADR-002: React/Next.js frontend, unchanged
**Status:** Accepted | **Category:** STACK
Already built, no reason to reconsider absent a concrete driver.

### ADR-003: Custom multi-provider AI Gateway instead of a single hard-coded LLM SDK
**Status:** Accepted | **Category:** AI
Context: single-provider dependency is a reliability and cost-negotiation risk. Decision: provider-abstraction with failover (`app/ai/`), already implemented. Consequences: more code to maintain than "just call OpenAI," but no single point of failure and can shop providers on cost/latency.

### ADR-004: Extend the AI Gateway pattern into Agent Orchestration rather than adopt LangChain/LangGraph
**Status:** Accepted | **Category:** AI
Context: could adopt an existing agent framework. Decision: extend the already-proven, already-tested resilience pattern (circuit breaker, retry, typed failures, DI) rather than introduce a second paradigm and a large external dependency surface. Consequences: more upfront build cost, less "free" ecosystem tooling; full control over failure semantics and cost budgeting, which off-the-shelf frameworks don't enforce as strictly as this platform needs.

### ADR-005: Hexagonal/Clean Architecture, applied incrementally, not a big-bang rewrite
**Status:** Accepted | **Category:** ARCH
New domains built this way from day one; existing bootstrap code migrated opportunistically, not in a dedicated rewrite PR.

### ADR-006: Three bounded contexts (Connection/Metadata/Execution), not one "database" concept
**Status:** Accepted | **Category:** ARCH
See [DOMAIN.md](DOMAIN.md) — collapsing them was identified as the most tempting, most damaging shortcut in the initial analysis.

### ADR-007: SQL Validator is deterministic, never LLM-trusting
**Status:** Accepted | **Category:** SEC
Non-negotiable: an LLM's self-assessment of query safety is never the sole gate. See [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md), [AGENTS.md](AGENTS.md).

### ADR-008: Row-level tenant isolation (RLS) over schema-per-tenant
**Status:** Accepted | **Category:** DATA
See [MULTITENANCY.md](MULTITENANCY.md) for full rationale (operational scalability past low-hundreds of tenants).

### ADR-009: tenant_id included in every table from the first migration
**Status:** Accepted | **Category:** DATA
Retrofitting is far more expensive than including it upfront — explicit rule in [CLAUDE.md](CLAUDE.md)'s Forbidden Patterns.

### ADR-010: Per-tenant envelope encryption for connection credentials
**Status:** Accepted | **Category:** SEC
A single platform-wide key is a forbidden pattern — see [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md).

### ADR-011: Kafka only where async decoupling/fan-out is genuinely needed
**Status:** Accepted | **Category:** ARCH
Explicit criteria in [EVENTS.md](EVENTS.md) — avoids the "everything is an event" complexity tax identified as a risk.

### ADR-012: Hybrid RAG (vector + knowledge graph), not vector-only
**Status:** Accepted | **Category:** AI
Vector-only misses declared FK relationships not semantically similar in name; graph-only misses semantically-relevant-but-unlinked tables. See [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md).

### ADR-013: RAG never retrieves raw customer row data, only metadata
**Status:** Accepted | **Category:** SEC/AI
Hard data-boundary rule — see [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md).

### ADR-014: Agent tiering (advisory vs. action) determines validation-gate requirements
**Status:** Accepted | **Category:** AI
See [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md), [AGENTS.md](AGENTS.md).

### ADR-015: Agents never call each other directly — orchestrator-mediated only
**Status:** Accepted | **Category:** ARCH
Keeps the call graph inspectable and lets budget enforcement check before every step, not just at the top. See [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md).

### ADR-016: Plan-then-execute for multi-step agent tasks, not free-form recursive tool calling
**Status:** Accepted | **Category:** AI
Bounds cost predictably. See [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)'s Planning Engine.

### ADR-017: PostgreSQL-only for MVP; other engines (Oracle, MySQL, ...) deferred
**Status:** Accepted | **Category:** PRODUCT
See [ROADMAP.md](ROADMAP.md) — supporting 9 engines from day one dilutes focus before the core metadata/agent primitive is proven on one engine.

### ADR-018: Usage-metered billing, not flat-seat pricing
**Status:** Accepted | **Category:** PRODUCT
Cost driver is LLM token spend + compute, not per-seat — see [MULTITENANCY.md](MULTITENANCY.md).

### ADR-019: Control-plane and data-plane scaled independently
**Status:** Accepted | **Category:** ARCH
Different scaling axes (tenant-count-driven vs. schema-size-and-burstiness-driven) — see [ARCHITECTURE.md](ARCHITECTURE.md).

### ADR-020: Execution Service architecturally isolated from other services
**Status:** Accepted | **Category:** SEC/ARCH
Limits blast radius of a compromise — see [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md).

### ADR-021: OpenTelemetry adopted once a second service exists, not before
**Status:** Accepted | **Category:** OPS
Full distributed tracing has limited value with one service; the existing request/trace-ID propagation (`app/middleware/request_id.py`) suffices until then and becomes OTel's carrier, not a discarded system. See [OBSERVABILITY.md](OBSERVABILITY.md).

### ADR-022: Kubernetes/EKS deferred until genuine multi-service scale
**Status:** Accepted | **Category:** OPS
Docker Compose/Railway-Render sufficient for MVP and early phases — see [ROADMAP.md](ROADMAP.md) "Scale phase" for the trigger condition.

### ADR-023: JSON Schema for event contracts, not Avro
**Status:** Accepted | **Category:** DATA
Lower tooling overhead for a Python-first stack without sacrificing validation. See [EVENTS.md](EVENTS.md).

### ADR-024: `docs/` (near-term) and root-level docs (target architecture) coexist rather than one replacing the other outright
**Status:** Accepted | **Category:** PRODUCT
See [CLAUDE.md](CLAUDE.md) — avoids destroying already-accurate near-term detail while still recording the long-term vision.

### ADR-025: This ADR log itself is the arbiter of "why" — decisions aren't re-litigated informally
**Status:** Accepted | **Category:** PRODUCT
A proposal to change a settled decision requires a new ADR, not a Slack thread or an unrecorded PR comment.
