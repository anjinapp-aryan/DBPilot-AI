# Database

Reference material and migrations for DBPilot AI's **application database**
(not the user's target databases — see [../docs/database.md](../docs/database.md)
for the distinction).

- `migrations/` — Alembic migration scripts (populated starting Phase 2,
  when the first application tables — `users`, `connections` — are added).

## Local Setup

Point `DATABASE_URL` (see [../.env.example](../.env.example)) at a free
[Neon](https://neon.tech) branch, or use the local Postgres container in
[../deployment/docker-compose.yml](../deployment/docker-compose.yml).

Once Alembic is wired up (Phase 2):

```bash
cd backend
alembic upgrade head
```
