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

## Text-to-SQL Agent (DeepSeek)

- Model: configurable via `DEEPSEEK_MODEL` (default `deepseek-chat`).
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
