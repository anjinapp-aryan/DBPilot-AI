# Security

DBPilot AI generates and executes SQL against real databases using an LLM.
This document is the threat model and the concrete mitigations in place or
planned per phase.

## Threat Model

| Threat | Mitigation | Phase |
|---|---|---|
| LLM generates a destructive statement (`DROP`, `DELETE` without `WHERE`, etc.) | Rule-based SQL Validator Agent acts as a hard gate before execution; statement allow-list defaults to `SELECT`-only | 4 |
| Prompt injection via schema/data (e.g. a malicious table/column name or row value instructs the model to ignore instructions) | Schema and result data are treated as untrusted content, never as instructions; validator does not trust LLM-asserted intent | 2, 4 |
| Excessive data exposure to the LLM provider | Only relevant schema subsets and minimal row samples are sent to DeepSeek — never full table dumps or credentials | 2, 3 |
| Long-running / runaway queries | Executor enforces statement timeouts and row limits | 5 |
| Credential leakage | Target DB credentials encrypted at rest in the app database; never logged; never sent to the LLM | 2 |
| Unauthorized access to a connection/schema | Per-user authorization checks on every connection and query | 2+ |
| Cross-origin abuse of the API | `ALLOWED_ORIGINS` CORS allow-list, auth-required endpoints | 1+ |
| Dependency vulnerabilities | Automated security scanning in CI (`lint.yml` / Dependabot) | 1 |

## Secret Scanning

CI runs [Gitleaks](https://github.com/gitleaks/gitleaks) against full git
history on every push/PR (`lint.yml` → `security-scan`). `.gitleaks.toml` at
the repo root extends the default rule set with a narrow allowlist for
placeholder credential-shaped values used in `backend/tests/ai/` fixtures
(e.g. `test-nvidia-key`) — these intentionally resemble real provider key
prefixes to exercise config-parsing logic, but hold no real secret. Real
credentials only ever live in a gitignored `.env`, never committed. Any new
allowlist entry must be scoped to a specific known-safe literal, never a
broad pattern, to avoid masking a genuine future leak.

## SQL Execution Safety Rules (Validator Agent)

Applied deterministically, not left to the LLM:

1. Default mode is **read-only**: only `SELECT` statements are permitted
   unless a connection is explicitly configured to allow mutations.
2. `DROP`, `TRUNCATE`, `ALTER`, `GRANT`, `REVOKE` are always blocked.
3. `DELETE` / `UPDATE` without a `WHERE` clause are always blocked.
4. Statements referencing tables outside the discovered/authorized schema
   are blocked.
5. All executed statements are recorded in `query_audit_log` (see
   [docs/database.md](database.md)).

## Secrets Handling

- Local secrets live in `.env` files (git-ignored — see [.gitignore](../.gitignore)).
- Production secrets are set as environment variables in Vercel/Railway/Render,
  never committed.
- `.env.example` documents required variables with placeholder values only.

## Reporting a Vulnerability

See [SECURITY.md](../SECURITY.md) at the repo root for the disclosure process.

## Related Documents

- [docs/agents.md](agents.md) — validator agent rules
- [docs/architecture.md](architecture.md) — trust boundaries
