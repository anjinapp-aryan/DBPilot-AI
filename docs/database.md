# Database

DBPilot AI deals with two distinct categories of database. Keeping this
distinction clear is important for security and architecture decisions.

## 1. Application Database (DBPilot's own storage)

Stores DBPilot AI's own state: users, saved connections (encrypted
credentials), conversation history, query audit logs.

- **Engine:** PostgreSQL, hosted on [Neon](https://neon.tech) (free tier)
- **Access:** SQLAlchemy (async) from the FastAPI backend
- **Migrations:** managed via Alembic, stored under `database/migrations/`

Planned core tables (introduced incrementally, not all in Phase 1):

| Table | Purpose |
|---|---|
| `users` | Account records |
| `connections` | Encrypted target-database connection strings + metadata |
| `conversations` | Chat sessions |
| `messages` | Individual turns (question, generated SQL, result summary) |
| `query_audit_log` | Every SQL statement proposed/executed, for traceability |

## 2. Target Database (the database the user connects DBPilot to)

This is **not** owned by DBPilot AI — it's the user's own PostgreSQL
database that they want to query in natural language.

- DBPilot only ever connects with credentials the user explicitly provides.
- Connections are encrypted at rest in the application database.
- The **Schema Discovery Agent** (Phase 2) introspects:
  - Tables and views
  - Columns, types, nullability
  - Primary/foreign keys
  - Indexes
  - Row-count estimates (for query planning hints)
- Discovered schema is cached and used as grounding context for the
  Text-to-SQL agent — the LLM never has direct database access.

## Local Development

For local development, run both the app DB and a sample target DB via
[deployment/docker-compose.yml](../deployment/docker-compose.yml), or point
`DATABASE_URL` at a free [Neon](https://neon.tech) branch.

## Related Documents

- [docs/architecture.md](architecture.md)
- [docs/security.md](security.md) — credential handling & query safety
