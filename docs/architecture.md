# GoreeCloud Metrics — Initial Architecture

## Status

Development foundation. This document describes only architecture that exists in this repository or an explicitly identified next boundary. It is not a claim that the planned Metrics product is complete.

## Current implemented foundation

The server/API foundation is a GoreeCloud-owned Django 5.2 application. It provides narrow liveness, readiness, and bounded service-status endpoints plus the first durable Metrics-owned system and agent identity domain. SQLite is used for development and test persistence/readiness validation only; a production metrics-storage engine has not been selected.

Current source layout:

- `src/goreecloud_metrics/` — project configuration and runtime entry points.
- `src/metrics/` — Metrics-owned endpoints, system/agent persistence, and enrollment lifecycle logic.
- `src/metrics/migrations/` — durable schema history for current development state.
- `src/metrics/management/commands/` — local operator/development commands that avoid prematurely exposing an administrative HTTP surface.
- `tests/` — source-level behavior and configuration validation.
- `scripts/` — repository validation.

## System and agent domain

`MonitoredSystem` is the durable Metrics-local identity for an authorized target. It carries a human-readable name plus bounded descriptive/role/environment/location fields, an optional external platform-identity reference, and a monitoring lifecycle state.

`AgentIdentity` is one-to-one with a monitored system in the current design. This keeps initial ownership and revocation semantics simple while leaving the future collector/runtime implementation separate from the server domain model.

`AgentEnrollment` stores one-time enrollment lifecycle metadata and a password hash only. `AgentCredential` stores hashed ongoing credential metadata so future rotation/revocation can retain history instead of overwriting identity evidence.

The enrollment service locks the target system and enrollment rows transactionally, bounds enrollment lifetime to at most 24 hours, revokes superseded unused enrollments, fails closed on invalid/expired/revoked/used credentials, creates exactly one agent identity, and returns plaintext enrollment/agent secrets only at their one-time issuance boundaries.

No network enrollment endpoint is exposed. This is intentional until transport authentication, abuse resistance, Identity/Wardveil boundaries, and agent protocol requirements are specified and tested.

## Native ownership boundary

GoreeCloud owns the product architecture, API contract, data model, security/privacy decisions, UI integration, telemetry semantics, collection model, retention model, alerting behavior, recovery model, and release direction. Django is a narrow framework dependency, not the product architecture.

## Next architecture boundaries

The following remain unimplemented and require separate design, code, validation, and evidence:

- authenticated administrative API and authorization;
- secure network agent-enrollment transport and agent authentication;
- Metrics Agent implementation and telemetry transport;
- current/historical metrics ingestion and storage;
- alert evaluation;
- Glaze UI 2.2.0 user interface;
- Wardveil Security, Privacy Shield, Everkeep, Identity, Mesh, Notify, Inventory, Monitor, and Manager integrations;
- backup/restore and production deployment architecture.

No complete monitoring product is embedded as the permanent Metrics engine.
