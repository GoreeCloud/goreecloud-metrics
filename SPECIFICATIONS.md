# GoreeCloud Metrics — Repository Specifications

## Status and authority

This repository is the canonical source-code authority for GoreeCloud Metrics. The product is in active development. The broader planned capability set is maintained in the canonical GoreeCloud project specification and is not automatically implemented by appearing in that plan.

Current source version: `0.1.0-dev.0`.

## Current implementation scope

The first source slice is intentionally narrow:

- Python/Django server and API foundation;
- liveness and database-aware readiness endpoints;
- bounded service-status endpoint;
- explicit runtime configuration validation;
- baseline HTTP hardening;
- automated source tests and repository-structure validation.

SQLite is currently a development/test dependency only. No production metrics-storage engine has been selected.

## Architecture decision

The server/API foundation uses Django `5.2.17`, an exact-pinned mature framework already used by current native GoreeCloud applications. Django is used as a narrow foundation for HTTP routing, configuration, testing, and future first-party application capabilities. GoreeCloud Metrics owns the application architecture, data contracts, telemetry model, product behavior, security/privacy decisions, integration contracts, UI composition, and release direction.

The Metrics Agent architecture and implementation language are not selected by this foundation. That decision requires its own resource-efficiency, security, privilege, enrollment, portability, and update/rollback evaluation.

## API surface currently implemented

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/livez/` | Process liveness only |
| GET | `/readyz/` | Database-aware readiness without dependency detail disclosure |
| GET | `/api/v1/status/` | Bounded product/source/lifecycle/API-version identity |

No telemetry ingestion or administrative API is implemented.

## Runtime configuration currently implemented

- `METRICS_ENV` — required; `development`, `test`, or `production`.
- `METRICS_SECRET_KEY` — required; production requires at least 50 characters.
- `METRICS_ALLOWED_HOSTS` — required in production; optional safe loopback/test default outside production.
- `METRICS_SQLITE_PATH` — optional development/test SQLite path; defaults to `metrics.sqlite3` relative to the repository root.

Reusable production secret values must not be stored in repository configuration or example files.

## GoreeCloud platform requirements

The following are mandatory product requirements but are not yet implemented in Metrics:

- GoreeCloud Manager read-only integration where approved;
- Privacy Shield;
- Wardveil Security;
- Everkeep;
- Glaze UI current Stable `2.2.0` for future user-facing UI;
- GoreeCloud Mesh;
- GoreeCloud Identity.

GoreeCloud Notify, Inventory, and Monitor contextual integration are also planned product integrations where applicable.

See [`docs/platform-integration-status.md`](docs/platform-integration-status.md) for the current fail-closed status ledger.

## Platform declaration

A shared machine-readable GoreeCloud platform declaration/schema remains a platform-level planned capability. Metrics will adopt the approved schema once canonicalized; this repository does not define a competing local format.

## Release boundary

This source version is Development only. It has no Stable, deployment, production, backup/restore, platform-conformance, or application-level Glaze UI acceptance evidence. Those gates must be satisfied separately and against exact source revisions.
