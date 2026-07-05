# AGENTS.md

Full agent roster. Each spec follows the same shape so a new implementer can build any agent to contract without re-deriving the pattern. **Tier** (from [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)) determines whether the deterministic validation gate is mandatory.

---

## 1. Connection Agent
**Tier:** Advisory | **Bounded context:** Connection

- **Responsibilities:** validate a new connection's reachability/credentials, detect engine type/version, surface actionable errors (wrong port vs. wrong password vs. firewall).
- **Inputs:** connection string/credential ref, engine hint (optional).
- **Outputs:** `ConnectionHealthChanged` event, structured diagnostic (`{reachable, auth_ok, engine, version, latency_ms}`).
- **Tools:** `test_connection(connection_id)` (engine-specific driver ping — no schema access).
- **Memory:** none required (stateless check).
- **Prompting strategy:** none for the check itself; LLM only used to turn a raw driver error into a human-readable diagnosis ("looks like the password is wrong" vs. dumping a stack trace).
- **Failure handling:** never retries with different credentials; a failed auth attempt is reported once, not brute-forced.
- **Observability:** `connection_health_check` event with outcome + latency.
- **KPIs:** time-to-diagnose (p50/p95), false-positive rate on "reachable" (connection reported healthy but later failed).

## 2. Schema Discovery Agent
**Tier:** Advisory | **Bounded context:** Metadata

- **Responsibilities:** introspect tables/columns/types/keys/indexes/row-count estimates via the engine's native catalog (`information_schema` for Postgres).
- **Inputs:** `connection_id`.
- **Outputs:** `Schema` aggregate (see [DOMAIN.md](DOMAIN.md)), `SchemaDiscoveryCompleted` event.
- **Tools:** `introspect_schema(connection_id)` (read-only catalog queries only — never touches user tables' data).
- **Memory:** long-term — discovered Schema is cached (see [MEMORY.md](MEMORY.md)); re-discovery only on explicit refresh or detected drift.
- **Prompting strategy:** none for extraction (deterministic SQL against catalog views); LLM used only to draft glossary-term suggestions from table/column names.
- **Failure handling:** partial discovery (some tables inaccessible due to permissions) is reported per-table, not treated as total failure.
- **Observability:** tables/columns discovered count, duration, permission-denied count.
- **KPIs:** discovery completion rate, discovery latency vs. schema size, staleness (time since last successful discovery).

## 3. Metadata Agent
**Tier:** Advisory | **Bounded context:** Metadata

- **Responsibilities:** enrich raw Schema with statistics (row counts, cardinality, null ratios), maintain the glossary mapping.
- **Inputs:** `Schema` aggregate.
- **Outputs:** updated `Table`/`Column` statistics, `GlossaryTerm` entities.
- **Tools:** `sample_statistics(connection_id, table)` (bounded-row sampling, never full-table scan).
- **Memory:** same cache as Schema Discovery; statistics have a shorter TTL than structure (structure rarely changes, stats drift faster).
- **Prompting strategy:** glossary-term generation from column name + sampled value patterns (never full row content — see prompt injection note in [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)).
- **Failure handling:** a failed sample on one table doesn't block others; missing stats degrade gracefully (Query Analysis Agent treats "unknown cardinality" as a valid input, not an error).
- **Observability:** sampling duration, rows sampled, glossary terms generated/accepted-by-user ratio.
- **KPIs:** glossary acceptance rate (user keeps vs. edits/rejects suggested terms).

## 4. Knowledge Graph Agent
**Tier:** Advisory | **Bounded context:** Metadata

- **Responsibilities:** build `LineageEdge` relationships (FK-derived + inferred from naming/usage patterns) into a queryable graph.
- **Inputs:** `Schema` aggregate, historical `QueryExecution` logs (to infer join patterns beyond declared FKs).
- **Outputs:** knowledge graph nodes/edges (see [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md) for graph-vs-vector division of labor).
- **Tools:** `graph_upsert(nodes, edges)`.
- **Memory:** the graph itself is the persistent memory (semantic/long-term, [MEMORY.md](MEMORY.md)).
- **Prompting strategy:** LLM proposes inferred (non-FK) relationships from naming similarity; every inferred edge is flagged `confidence: inferred` vs. `confidence: declared`, never presented as equally certain.
- **Failure handling:** inferred-edge generation failures don't block declared-FK edges from being stored.
- **Observability:** nodes/edges created, inferred-vs-declared ratio.
- **KPIs:** graph query latency, inferred-edge precision (spot-checked against actual join usage).

## 5. SQL Generation Agent (Text-to-SQL)
**Tier:** Action (feeds Execution) | **Bounded context:** Metadata → Execution boundary

- **Responsibilities:** turn a natural-language question + schema context + conversation history into one candidate SQL statement.
- **Inputs:** question, relevant Schema subset (RAG-retrieved, not the whole schema), last N conversation turns.
- **Outputs:** candidate SQL (never executed directly by this agent).
- **Tools:** `search_metadata(query)` (RAG retrieval of relevant tables/columns) — no execution tool.
- **Memory:** short-term (conversation turns, [MEMORY.md](MEMORY.md)).
- **Prompting strategy:** see `prompts/text-to-sql.md` and [PROMPTS.md](PROMPTS.md) — explicit rules against destructive statements baked into the prompt as a first line of defense, but never the *only* defense (see Failure handling).
- **Failure handling:** this agent's output is **always** passed through `SqlValidationService` (deterministic, non-LLM) before anything downstream sees it — this agent's own claim of safety is never trusted (see [SECURITY.md](SECURITY.md)).
- **Observability:** generation latency, validator rejection rate (tracked per-reason: destructive statement, unauthorized table, syntax error).
- **KPIs:** validator-approval rate, user-correction rate (did the user have to rephrase), execution success rate of approved SQL.

## 6. Query Analysis Agent (Query Optimization)
**Tier:** Advisory

- **Responsibilities:** analyze query plans (`EXPLAIN ANALYZE` equivalent per engine), suggest indexes/rewrites.
- **Inputs:** SQL statement, query plan, Table statistics (cardinality/row counts from Metadata Agent).
- **Outputs:** optimization suggestions (never auto-applied).
- **Tools:** `explain_query(connection_id, sql)` (read-only plan retrieval — never runs the query being analyzed unless the user explicitly requests actual execution).
- **Memory:** none required beyond the current session.
- **Prompting strategy:** plan-to-plain-English explanation + suggestion generation, grounded in the actual plan output (never invents a plan).
- **Failure handling:** missing statistics degrades suggestion confidence, doesn't block the explanation.
- **Observability:** suggestions generated, suggestions applied by user (feedback loop).
- **KPIs:** suggestion-adoption rate, measured query-time improvement when a suggestion is applied.

## 7. Data Quality Agent
**Tier:** Advisory

- **Responsibilities:** detect null-rate anomalies, duplicate rates, referential-integrity violations, distribution drift over time.
- **Inputs:** Table statistics history (time series), sampled data.
- **Outputs:** data quality findings with severity.
- **Tools:** `sample_statistics` (shared with Metadata Agent), `compare_statistics_history(table)`.
- **Memory:** long-term (statistics time series, [MEMORY.md](MEMORY.md)).
- **Prompting strategy:** LLM used for finding-to-narrative summarization only; the anomaly detection itself is statistical, not LLM-judged.
- **Failure handling:** insufficient history (new table) reports "not enough data yet," not a false negative.
- **Observability:** findings generated per run, severity distribution.
- **KPIs:** finding precision (user-confirmed real issue vs. dismissed as noise).

## 8. Observability Agent
**Tier:** Advisory

- **Responsibilities:** surface database-level health signals (connection pool saturation, replication lag, long-running queries) to the user.
- **Inputs:** engine-native monitoring views (e.g. `pg_stat_activity`), platform's own [OBSERVABILITY.md](OBSERVABILITY.md) metrics for DBPilotAI's own execution against that connection.
- **Outputs:** health summary, alerts.
- **Tools:** `read_engine_metrics(connection_id)` (read-only).
- **Memory:** short-term rolling window for trend detection.
- **Prompting strategy:** narrative summary of metrics, always cites the actual numbers (never a vague "looks fine").
- **Failure handling:** metrics endpoint unavailable → reports "unable to check," not a fabricated "healthy."
- **Observability:** check frequency, alert-fired count.
- **KPIs:** alert precision (real incident vs. noise), mean time-to-surface an actual incident.

## 9. Troubleshooting Agent (Root Cause Analysis)
**Tier:** Advisory

- **Responsibilities:** given a reported symptom ("this query got slow"), correlate Query Analysis + Observability + Data Quality signals into a probable root cause.
- **Inputs:** symptom description, recent query history, Observability Agent's recent findings.
- **Outputs:** ranked hypothesis list with supporting evidence (never a single unqualified answer).
- **Tools:** read-only access to the other advisory agents' recent outputs (via `AgentContext`, not direct agent-to-agent calls — see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)'s Agent Communication rule).
- **Memory:** short-term (current investigation session).
- **Prompting strategy:** structured hypothesis-ranking prompt; every hypothesis must cite which tool/signal supports it.
- **Failure handling:** insufficient evidence → "need more data" is a valid, honest output.
- **Observability:** hypotheses generated, top-hypothesis-correct rate (user-confirmed).
- **KPIs:** time-to-root-cause vs. manual DBA investigation baseline.

## 10. Documentation Agent
**Tier:** Advisory

- **Responsibilities:** generate/maintain human-readable schema documentation from Schema + Metadata + Knowledge Graph.
- **Inputs:** Schema, glossary, lineage.
- **Outputs:** Markdown/HTML documentation artifacts.
- **Tools:** none beyond metadata read access.
- **Memory:** long-term (documentation versions).
- **Prompting strategy:** grounded strictly in actual schema elements — a documented table/column must exist in the current Schema, checked deterministically (reflection step from [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)).
- **Failure handling:** schema drift since last doc generation is flagged, not silently papered over.
- **Observability:** docs generated, drift-detected count.
- **KPIs:** doc freshness (time since schema change vs. doc regeneration), user edit rate post-generation.

## 11. Migration Agent
**Tier:** Action (highest blast radius alongside SQL Generation)

- **Responsibilities:** assist planning schema migrations (e.g. adding a column, changing a type) — plan generation only, execution requires explicit human approval per step.
- **Inputs:** desired end-state schema change, current Schema.
- **Outputs:** ordered migration plan (Alembic-style up/down steps), risk annotations (locking behavior, estimated duration on current table size).
- **Tools:** `explain_query` (to estimate lock/duration impact), no direct DDL execution tool — DDL execution is always a separate, human-confirmed step outside this agent.
- **Memory:** short-term (current migration planning session).
- **Prompting strategy:** plan-then-execute (see Planning Engine, [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)) — the full plan is shown before any step runs.
- **Failure handling:** any step failing mid-migration halts the remaining plan; never auto-continues past an error.
- **Observability:** plans generated, plans approved-as-is vs. edited, steps executed vs. halted.
- **KPIs:** plan-approval rate, zero-incident migration rate.

## 12. Security Agent
**Tier:** Advisory (governance, not enforcement — enforcement is `SqlValidationService`/`CredentialEncryptionService`, which are deterministic services, not agents)

- **Responsibilities:** surface access-pattern anomalies (unusual table access, off-hours bulk exports), review connection permission scope for over-privilege.
- **Inputs:** `ExecutionAuditEntry` history, `Connection` grant scope.
- **Outputs:** security findings/recommendations.
- **Tools:** read-only access to audit log and connection metadata (never credentials).
- **Memory:** long-term (audit history).
- **Prompting strategy:** anomaly narrative grounded in actual audit entries, always cites the specific entries.
- **Failure handling:** ambiguous pattern → flagged for human review, never auto-revokes access.
- **Observability:** findings generated, findings escalated.
- **KPIs:** true-positive rate on flagged anomalies (confirmed by security review).

## 13. Workflow Agent
**Tier:** Advisory (meta-agent: recommends workflows, doesn't execute them directly — `AgentOrchestrator` executes)

- **Responsibilities:** given a high-level user goal ("help me understand why revenue reporting is slow"), decompose into a proposed sequence of other agents' invocations.
- **Inputs:** user goal (natural language).
- **Outputs:** proposed `WorkflowRun` plan (which agents, what order, estimated budget).
- **Tools:** none (pure planning — actual invocation goes through `AgentOrchestrator`).
- **Memory:** short-term.
- **Prompting strategy:** plan generation constrained to the actual agent roster in this file — never invents an agent that doesn't exist.
- **Failure handling:** a goal that doesn't map to any known agent combination returns "not supported yet," not a fabricated plan.
- **Observability:** plans proposed, plans accepted-as-is vs. user-modified.
- **KPIs:** plan-acceptance rate, workflow-completion rate for accepted plans.
