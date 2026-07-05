# SECURITY_ARCHITECTURE.md

Enterprise security architecture for DBPilotAI. For vulnerability disclosure (how to report a bug), see [SECURITY.md](SECURITY.md) — that file is GitHub's special convention file and stays focused on disclosure process only. For the current, smaller Phase-1-scoped threat model, see `docs/security.md`.

## Authentication

OAuth2/OIDC against an external Identity Provider (Auth0, Okta, or AWS Cognito — not a hand-rolled password store) for human users. Service-to-service (API Gateway → internal services) uses short-lived signed JWTs, not shared static API keys.

## Authorization (RBAC)

Roles: `tenant_admin`, `db_admin` (can manage connections), `analyst` (read/query only, no connection management), `viewer` (dashboards only). Role checks happen at the **service layer**, not just the route decorator — see [CLAUDE.md](CLAUDE.md)'s Security Rules. A permission check missing from one route must not be the only thing standing between a request and unauthorized data.

## JWT

Access tokens short-lived (≤15 min), refresh tokens rotated on use, both tenant-scoped (`tenant_id` claim checked on every request against the resource's actual `tenant_id` — never trust the claim alone without a DB-level check, defense in depth against a forged/stale token).

## OAuth2

Authorization Code + PKCE flow for the web app; Client Credentials flow for service-to-service and any future public API/SDK access.

## Encryption

- **At rest:** Postgres transparent encryption (managed provider default) plus **application-level envelope encryption specifically for connection credentials** — a second layer, because credentials are the platform's highest-liability data. Each tenant has its own Data Encryption Key (DEK), itself encrypted by a platform Key Encryption Key (KEK) held in a managed KMS (AWS KMS). A compromised DEK exposes one tenant's credentials, never all tenants'.
- **In transit:** TLS everywhere, including internal service-to-service traffic (not just the public edge).
- **In use:** decrypted credentials exist only for the duration of a single `Execution Service` connection attempt — never cached decrypted, never logged, never included in an LLM prompt (see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)'s Agent Security).

## Secrets Management

Platform's own secrets (KMS key refs, LLM provider API keys, Kafka credentials) live in a managed secrets store (AWS Secrets Manager), injected as environment variables at deploy time — never committed (the existing Gitleaks full-history scan, [CLAUDE.md](CLAUDE.md), stays as a backstop, not the primary control).

## Audit Logging

Every connection access, every SQL execution attempt (approved or rejected), every credential decrypt operation is written to the append-only `execution_audit_log` ([DATABASE.md](DATABASE.md)) — immutable at the DB-grant level, not just by application convention.

## Compliance

Design decisions map to SOC 2 (access control, audit logging, encryption) and GDPR (data minimization — RAG never touches raw customer row data, see [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md); right-to-erasure — tenant offboarding purges connections/metadata/vectors, not just a soft-delete flag) from day one, not retrofitted before a first enterprise customer's security review.

## Zero Trust Architecture

No implicit trust between internal services because they're "inside the network": every internal call carries a verifiable identity (service JWT), every data access is tenant-scoped and checked at the query layer (not just assumed safe because the caller is another internal service), and the Execution Service is architecturally isolated (see [ARCHITECTURE.md](ARCHITECTURE.md)) so a compromise there can't laterally reach the app database's credential store.
