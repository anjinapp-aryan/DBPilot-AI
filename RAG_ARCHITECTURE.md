# RAG_ARCHITECTURE.md

RAG over database metadata — never over raw customer row data (see Hallucination Prevention / data-boundary note below).

## Chunking Strategy

Metadata is chunked at the **table level**, not column-level or whole-schema-level:
- One chunk = one table's `{name, columns[with types], glossary terms, sample of declared FK relationships}`.
- Rationale: column-level chunks lose the relational context an agent needs ("which table is this column even in"); whole-schema chunks blow past context windows for any real schema and dilute retrieval relevance.
- Large tables (>50 columns) split into a "core columns" chunk (PK/FK/most-queried, from `query_executions` history) + an "extended columns" chunk, so retrieval can surface the core chunk first.

## Embedding Strategy

- Embed the chunk's natural-language rendering (`"Table 'orders' has columns: id (uuid, pk), customer_id (uuid, fk->customers.id), ..."`), not raw JSON — embedding models perform better on natural-language-shaped text.
- Re-embed only on schema-version change ([DATABASE.md](DATABASE.md)'s `schemas.version`) — never on a fixed schedule regardless of change.
- Provider: same [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) gateway pattern applies conceptually (embedding-provider abstraction, not a single hard-coded vendor) even though embeddings are a different call shape than chat completion.

## Retrieval Strategy

- Hybrid: vector similarity (semantic — "which tables are about revenue") **plus** knowledge-graph traversal (explicit — "what's directly joined to `orders`") for the SQL Generation Agent's schema-context step. Vector search alone misses declared FK relationships that aren't semantically similar in name; graph alone misses semantically-relevant-but-unlinked tables.
- Retrieval is always scoped by `tenant_id` and `connection_id` at the query layer (a vector DB filter, not a post-retrieval filter) — see [MULTITENANCY.md](MULTITENANCY.md)'s data-bleed risk.

## Ranking

Two-stage: vector similarity produces a candidate set (top ~20), then a lightweight re-rank boosts tables that (a) appear in the current conversation's recent turns, (b) are graph-adjacent to an already-retrieved table, (c) have higher historical query frequency (from `query_executions`). Final context passed to the SQL Generation Agent is the top ~5 re-ranked tables, not the raw top-20 similarity set.

## Context Management

- The agent's prompt never receives the *entire* retrieved chunk set unfiltered — token budget is enforced (truncate to top-N re-ranked chunks) before prompt construction, matching the Agent Orchestration budget philosophy in [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md).
- Conversation history (short-term memory, [MEMORY.md](MEMORY.md)) is summarized after N turns rather than grown unbounded, to keep the retrieval+history context within budget.

## Knowledge Graph Integration

Division of labor (resolves the "two systems both answering relatedness" risk from the analysis that produced this doc):
- **Vector store** answers: "what's semantically similar to this question/table."
- **Knowledge graph** answers: "what's explicitly/structurally related to this table" (FK joins, inferred lineage from the Knowledge Graph Agent).
Both are consulted for SQL Generation's schema-context retrieval; only the graph is consulted for lineage/impact-analysis questions ("what breaks if I drop this column").

## Hallucination Prevention

- **Data boundary (hard rule):** RAG retrieves metadata (schema/glossary/lineage) — never raw row content. An agent never has actual customer data in its prompt context unless the user explicitly pastes a result back in.
- Every SQL Generation Agent output is checked against the **live** schema (not just the retrieved chunk) by `SqlValidationService` before execution — a stale or incompletely-retrieved chunk can't cause an invalid-table reference to slip through, because validation re-checks against ground truth, not against what was retrieved.
- Documentation Agent's reflection step (from [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)) similarly checks generated docs against the actual current Schema aggregate before publishing.
