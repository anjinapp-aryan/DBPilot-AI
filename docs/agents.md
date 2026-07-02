# Agents

DBPilot AI's backend is organized as a small set of single-responsibility
agents, coordinated by an orchestrator. This document is the contract for
each agent — inputs, outputs, and failure modes — and will be filled in
further as each phase lands. Prompt templates live under
[prompts/](../prompts/); orchestration wiring lives under `backend/app/agents/`
and top-level [agents/](../agents/) specs.

## Agent Roster

| Agent | Phase | Input | Output |
|---|---|---|---|
| Schema Discovery | 2 | DB connection | Structured schema (tables, columns, keys) |
| Text-to-SQL | 3 | Question + schema + conversation history | Candidate SQL statement |
| SQL Validator | 4 | Candidate SQL | Approve / reject (+ reason) |
| SQL Executor | 5 | Approved SQL | Result rows / error |
| SQL Explainer | 6 | SQL statement | Plain-English explanation |
| Voice | 7 | Audio (browser) | Transcribed question |
| Chart | 8 | Result rows | Chart spec (type + config) |
| Orchestrator | 9 | User question | Coordinates all of the above |

## Design Principles

1. **Single responsibility.** Each agent does one thing and can be tested in
   isolation with fixed inputs.
2. **The validator is a hard gate, not a suggestion.** No SQL reaches the
   executor without passing validation — this boundary is enforced in code,
   not by prompting.
3. **Deterministic where possible.** Validation and execution are
   deterministic/rule-based; only generation and explanation call the LLM.
4. **Stateless agents, stateful orchestrator.** Agents receive everything
   they need as input; conversation state lives in the orchestrator/app DB.

## AI Gateway (LLM Connectivity Layer)

Implemented in `backend/app/ai/` — the single entry point every LLM-calling
agent (Text-to-SQL, SQL Explainer, ...) goes through. Never call a provider
SDK/API directly from agent code; go through `AIGatewayService`.

- **Automatic failover.** Providers are tried in `AI_PROVIDER_ORDER` order
  (default `deepseek,gemini,groq,qwen,openrouter`); if DeepSeek hits a rate
  or token limit, the gateway transparently retries the next configured
  provider instead of failing the request. A provider missing its API
  key/model is skipped automatically.
- **Per-provider resilience.** Each provider gets its own retry (transient
  network/timeout errors only — quota errors fail over immediately with no
  wasted retry budget) and circuit breaker (opens after repeated failures,
  half-opens after a cooldown).
- **Health tracking + metrics.** `ProviderHealthTracker` caches per-provider
  health for 5 minutes; `AIMetrics` tracks calls/successes/failures/latency
  per provider. Exposed via `GET /api/v1/ai/health`, `/providers`, `/stats`.
- **Providers today:** DeepSeek and Qwen (NVIDIA-hosted, OpenAI-compatible),
  Groq (OpenAI-compatible), Gemini (native REST), OpenRouter (OpenAI-compatible,
  final fallback). Adding another provider is one new class under
  `backend/app/ai/providers/` plus its env vars — no gateway changes.

## Text-to-SQL Agent (DeepSeek, via the AI Gateway)

- Model: configurable via `NVIDIA_DEEPSEEK_MODEL` (default
  `deepseek-ai/deepseek-v4-flash`). Falls over to Gemini/Groq/Qwen/OpenRouter
  automatically if DeepSeek is rate-limited or unavailable — see AI Gateway
  above.
- Context: relevant schema subset (not the entire database — see
  [docs/database.md](database.md)) + last N conversation turns.
- Prompt templates: [prompts/](../prompts/).

## SQL Validator Agent

Rule-based checks applied before any statement reaches the executor:

- Reject `DROP`, `TRUNCATE`, `ALTER`, `GRANT`/`REVOKE` outright.
- Reject `DELETE`/`UPDATE` without a `WHERE` clause.
- Reject statements referencing tables outside the user's authorized scope.
- Enforce a statement allow-list (`SELECT` by default; mutating statements
  require explicit opt-in per connection).

Full threat model: [docs/security.md](security.md).

## Related Documents

- [docs/architecture.md](architecture.md)
- [prompts/README.md](../prompts/README.md)
- [agents/README.md](../agents/README.md)
