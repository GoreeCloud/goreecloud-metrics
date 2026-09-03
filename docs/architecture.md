# GoreeCloud Metrics — Initial Architecture

## Status

Development foundation. This document describes only architecture that exists in this repository or an explicitly identified next boundary. It is not a claim that the planned Metrics product is complete.

## Current implemented foundation

The first server/API slice is a GoreeCloud-owned Django 5.2 application. It currently provides only narrow liveness, readiness, and bounded service-status endpoints. SQLite is used for development and test readiness validation only; a production metrics-storage engine has not been selected.

Current source layout:

- `src/goreecloud_metrics/` — project configuration and runtime entry points.
- `src/metrics/` — Metrics-owned service endpoints and application logic.
- `tests/` — source-level behavior and configuration validation.
- `scripts/` — repository validation.

## Native ownership boundary

GoreeCloud owns the product architecture, API contract, data model, security/privacy decisions, UI integration, telemetry semantics, collection model, retention model, alerting behavior, recovery model, and release direction. Django is a narrow framework dependency, not the product architecture.

## Next architecture boundaries

The following remain unimplemented and require separate design, code, validation, and evidence:

- authenticated administration and authorization;
- system and agent identity/enrollment;
- Metrics Agent implementation and telemetry transport;
- current/historical metrics ingestion and storage;
- alert evaluation;
- Glaze UI 2.2.0 user interface;
- Wardveil Security, Privacy Shield, Everkeep, Identity, Mesh, Notify, Inventory, Monitor, and Manager integrations;
- backup/restore and production deployment architecture.

No complete monitoring product is embedded as the permanent Metrics engine.
