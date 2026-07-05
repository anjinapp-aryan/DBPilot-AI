# MEMORY.md

Memory taxonomy across agents and workflows. Every memory type below is tenant-scoped and connection-scoped where applicable — see [MULTITENANCY.md](MULTITENANCY.md).

## Short-Term Memory

Scope: one conversation or one `WorkflowRun`. Storage: Redis (fast, ephemeral, TTL'd). Contents: recent conversation turns, current `AgentContext` (see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)). Summarized (not truncated blindly) after N turns to preserve intent while staying within token budget ([RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)'s Context Management).

## Long-Term Memory

Scope: persists across sessions, per tenant/connection. Storage: PostgreSQL (`metadata` schema tables, [DATABASE.md](DATABASE.md)). Contents: discovered Schema, glossary terms, statistics history, prior workflow outcomes worth remembering (e.g. "this migration plan was approved and ran cleanly last time").

## Vector Memory

Scope: metadata embeddings for RAG retrieval ([RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)). Storage: pgvector or Qdrant. Never stores raw row data — metadata only.

## Semantic Memory

The Knowledge Graph itself ([RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md), [AGENTS.md](AGENTS.md)'s Knowledge Graph Agent) — durable facts about relationships between schema elements, distinct from vector similarity.

## Episodic Memory

Scope: "what happened" — specific past `WorkflowRun`s, their steps, outcomes, and user feedback (approved/edited/rejected). Storage: `orchestration` schema tables ([DATABASE.md](DATABASE.md)). Used by the Workflow Agent and Migration Agent to recall "was a similar plan tried before, what happened."

## Agent Memory (per-agent working memory)

Each `AgentStep` receives only the slice of memory relevant to its tier and task — an advisory agent (e.g. Data Quality) gets statistics history; an action agent (SQL Generation) gets schema context + conversation history, never the full episodic log of other tenants' workflows. Memory access is scoped the same way tool access is scoped ([AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)'s Agent Security).

## Memory Lifecycle

| Memory type | Write trigger | Read pattern | Expiry/Eviction |
|---|---|---|---|
| Short-term | Every conversation turn | Every step in the active WorkflowRun | TTL (e.g. 24h idle) or workflow completion |
| Long-term (metadata) | Schema discovery/re-discovery | Every RAG retrieval, every agent needing schema context | Superseded by next `schemas.version`, old versions retained for audit, not served live |
| Vector | Schema-version change | RAG retrieval | Re-embedded (old vectors orphaned/GC'd) on version change |
| Semantic (graph) | Knowledge Graph Agent run | Retrieval, lineage/impact queries | Updated incrementally; inferred edges re-scored periodically |
| Episodic | Workflow completion | Workflow Agent/Migration Agent planning, analytics | Retained per tenant's audit-retention policy ([DATABASE.md](DATABASE.md) partitioning) |

**Invariant:** no memory type is ever queried without a `tenant_id` filter applied at the storage layer (not just the application layer) — see [MULTITENANCY.md](MULTITENANCY.md) for why this is enforced as defense-in-depth (RLS/index-level), not just a WHERE clause an engineer might forget to add.
