# AI_ARCHITECTURE.md

The agent framework's design. This extends the already-built `AIGatewayService` pattern (`backend/app/ai/`) rather than introducing a second resilience paradigm — see [CLAUDE.md](CLAUDE.md)'s Engineering Principles.

## Agent Framework

`AgentOrchestrator` (planned, `backend/app/agents/orchestrator.py`) sits one layer above `AIGatewayService`:

```
AgentOrchestrator
  └── WorkflowRun (budget-scoped)
        └── AgentStep (one agent, one turn)
              └── AIGatewayService.chat(...)   ← same failover/retry/circuit-breaker as today
              └── ToolCall(s)                   ← MCP-style tool contracts
```

Every agent implements one interface (mirrors `LlmProvider`'s shape):

```python
class Agent(Protocol):
    name: str
    async def run(self, input: AgentInput, context: AgentContext) -> AgentOutput: ...
    def tools(self) -> list[ToolSpec]: ...
```

## Agent Lifecycle

`PENDING → RUNNING → (AWAITING_TOOL | AWAITING_REFLECTION) → COMPLETED | FAILED | BUDGET_EXCEEDED`

- **PENDING**: WorkflowRun created, budget assigned from tenant Quota.
- **RUNNING**: agent generating/reasoning.
- **AWAITING_TOOL**: agent requested a tool call (e.g. "fetch schema for table X"); orchestrator executes it, result fed back.
- **AWAITING_REFLECTION**: for agents with a reflection step (see below), output is checked before being returned.
- **COMPLETED/FAILED/BUDGET_EXCEEDED**: terminal states, always logged with full step trace.

## Planning Engine

For multi-step tasks (e.g. Migration Agent), a lightweight plan-then-execute loop: the agent first produces an ordered step list (not free-form recursive tool calling), the orchestrator validates the plan's step count against budget *before* executing any step. This bounds cost predictably instead of discovering the workflow's cost after it's spent.

## Reflection Engine

A cheap, deterministic (non-LLM where possible) self-check before an agent's output is accepted:
- SQL Generation Agent → SQL Validator (deterministic, see [SECURITY.md](SECURITY.md)) — this is reflection, not a second LLM call.
- Documentation/Data Quality Agents → schema-conformance check (does the output reference tables/columns that actually exist in the current Schema aggregate).
Only fall back to an LLM-based reflection ("ask the model to critique its own output") when a deterministic check isn't possible — it's slower, costs money, and doesn't guarantee correctness.

## Tool Calling

Tools are exposed via MCP (Model Context Protocol) contracts so any agent can be given any subset of tools without bespoke integration per agent. Each tool has: name, JSON-schema input/output, an idempotency flag (does calling it twice with the same input cause side effects), and a cost estimate (used by the Planning Engine's budget check).

Example tool contracts: `get_schema(connection_id)`, `run_validated_query(connection_id, sql)` (only callable after `SqlValidationApproved`), `search_metadata(query, tenant_id)` (RAG retrieval).

## Agent Orchestration

`AgentOrchestrator` is the only thing that fans out to multiple agents. Agents never call each other directly — this keeps the call graph inspectable (every AgentStep is logged under one WorkflowRun) and lets `BudgetEnforcementService` (see [DOMAIN.md](DOMAIN.md)) check before every step, not just at the top.

## Agent Communication

Agents communicate only through the WorkflowRun's shared `AgentContext` (schema context, conversation history, prior steps' outputs) — never through ad-hoc direct calls or shared mutable global state. This is what makes a `WorkflowRun`'s full step trace sufficient to debug "why did the agent do that," per [OBSERVABILITY.md](OBSERVABILITY.md).

## Agent Governance

- Every agent has an explicit tier (see [AGENTS.md](AGENTS.md)): **advisory** (read-only, wrong output is a UX problem) or **action** (can reach Execution context, wrong output can be an incident).
- Action-tier agents require the deterministic validation gate; advisory-tier agents don't, but their output is always labeled as AI-generated in the UI (no silent authority).
- New agents or new tool grants to existing agents go through the [DECISIONS.md](DECISIONS.md) ADR process — not ad-hoc.

## Agent Security

- Tool calls are tenant-scoped by construction (`connection_id`/`tenant_id` are part of the tool's required input, validated server-side against the calling WorkflowRun's tenant — never trusted from agent-generated input).
- No tool exposes raw credential material; `run_validated_query` takes a `connection_id` and resolves credentials server-side.
- Prompt injection via schema/data content is assumed possible; schema names, column names, and row values are always treated as untrusted data in prompts, never as instructions (mirrors the existing threat-model language in `docs/security.md`).

## Agent Observability

Every `AgentStep` logs (via the existing structlog pattern, `event_name + kwargs`): agent name, input summary, tool calls made, tokens/cost, latency, and outcome. A `WorkflowRun`'s full trace answers "what did the agent see, what did it decide, why" without needing to reproduce the bug — see [OBSERVABILITY.md](OBSERVABILITY.md) for the full monitoring spec and [MEMORY.md](MEMORY.md) for how context is retained across steps/turns.
