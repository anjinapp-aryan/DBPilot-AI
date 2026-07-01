# Security Policy

DBPilot AI executes AI-generated SQL against user-connected databases, so
security is a first-class concern. See [docs/security.md](docs/security.md)
for the full threat model (prompt injection, SQL injection, destructive query
prevention, credential handling).

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities. Instead,
report them privately via GitHub's
["Report a vulnerability"](https://github.com/anjinapp-aryan/DBPilot-AI/security/advisories/new)
flow, or email the maintainers listed in the repository.

We aim to acknowledge reports within 72 hours and to ship a fix or mitigation
plan within 14 days for critical issues.

## Supported Versions

DBPilot AI is pre-1.0 and under active development. Only the `main` branch is
currently supported with security fixes.
