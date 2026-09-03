# GoreeCloud Metrics — Repository Specifications

## Status and authority

This repository is the canonical source-code authority for GoreeCloud Metrics. The broader planned product scope remains in the canonical GoreeCloud Project Specification — Metrics and is not implemented merely because it is documented there.

Current source version: `0.1.0-dev.2`.

Acceptance state: **source implementation under Development validation only**. No production or Stable claim is made.

## Current implementation scope

The current source implements:

- Python 3.14 / Django `5.2.17` server and API foundation;
- bounded liveness, database-aware readiness, and service-status endpoints;
- explicit runtime configuration validation and baseline HTTP hardening;
- monitored-system, Metrics-local agent identity, one-time enrollment, agent credential, and telemetry snapshot models;
- local system registration and one-time enrollment issuance;
- network consumption of one-time enrollment credentials;
- authenticated telemetry intake using a per-agent credential;
- a lightweight first-party Python Metrics Agent for Linux-style `/proc` environments;
- core CPU/load, memory/swap, root-filesystem capacity, and aggregate non-loopback network counters;
- strict telemetry schema, timestamp, numeric, relationship, and body-size validation;
- duplicate sample rejection and monitoring-state/revocation enforcement;
- configurable Development telemetry retention from 1 to 2160 hours, default 168 hours;
- pruning on successful authenticated ingestion and the `prune_telemetry` maintenance command;
- source tests, migrations, documentation validation, and exact-revision CI.

SQLite remains a development/test dependency only. No production metrics-storage engine has been selected.

## Native architecture decision

GoreeCloud Metrics owns its application architecture, agent protocol, telemetry schema, data model, validation, security/privacy decisions, integration boundaries, UI direction, and release lifecycle. Django is a narrow server/persistence framework dependency rather than the product architecture.

The Development Metrics Agent is first-party GoreeCloud source implemented with the Python standard library. It initiates outbound requests to the Metrics server and does not expose an administrative or telemetry listener on the monitored host.

The current collector scope is deliberately small so resource collection can be validated before privileged hardware, container, storage-health, GPU, or vendor-specific collectors are introduced.

## Enrollment and credential boundary

Current source invariants include:

- enrollment secrets come from a cryptographically secure random source;
- server persistence contains password hashes rather than plaintext enrollment or agent credential secrets;
- enrollment credentials are one-time, expiring, and revocable;
- enrollment lifetime is greater than zero and at most 24 hours;
- issuing a new unused enrollment revokes earlier unused enrollment records for that system;
- successful enrollment creates one Metrics-local agent identity and its initial credential;
- agent revocation preserves identity/history and revokes active credentials;
- malformed, expired, revoked, used, missing, or secret-invalid enrollment attempts fail closed;
- plaintext credential material is returned only at issuance/consumption boundaries and must not be logged or committed.

The Metrics-local identity model is not GoreeCloud Identity integration. The current credential scheme is not an accepted Wardveil service/device identity contract and is not represented as one.

## Agent transport boundary

The first source protocol exposes:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/livez/` | Process liveness only |
| GET | `/readyz/` | Database-aware readiness without dependency detail disclosure |
| GET | `/api/v1/status/` | Bounded product/source/lifecycle/API-version identity |
| POST | `/api/v1/agents/enroll/` | Consume one issued enrollment secret and return the initial agent credential once |
| POST | `/api/v1/agents/telemetry/` | Accept one authenticated, bounded telemetry sample |

Agent enrollment and telemetry responses are marked `Cache-Control: no-store`. The server source rejects insecure enrollment and telemetry requests when configured as production, while the Development agent itself refuses non-loopback HTTP URLs. No target-environment TLS/reverse-proxy deployment has been accepted, so this is source behavior rather than production transport evidence.

The machine endpoints use token authentication rather than browser sessions and are CSRF-exempt by design. This does not create a human administrative API.

## Telemetry schema version 1

Each accepted snapshot contains only:

- schema version, random sample UUID, sample timestamp, and agent source version;
- logical processor count and 1/5/15-minute load averages;
- aggregate CPU tick counters for user, nice, system, idle, I/O wait, IRQ, soft IRQ, and steal;
- total/available memory and total/free swap;
- total/available capacity for `/`;
- aggregate received/transmitted byte counters excluding loopback.

The initial agent does not collect or transmit hostname, IP address, hardware serial numbers, usernames, process lists, environment variables, command lines, file contents, logs, packet contents, or container metadata.

Telemetry is accepted only for active agent identities attached to systems that are not paused or retired. The first accepted sample transitions a pending monitored-system record to active.

## Retention

`METRICS_TELEMETRY_RETENTION_HOURS` controls the current Development snapshot retention boundary:

- default: 168 hours;
- minimum: 1 hour;
- maximum: 2160 hours (90 days).

Successful telemetry ingestion removes expired snapshots globally. `python manage.py prune_telemetry` provides an explicit cleanup path for periods where no new telemetry arrives.

This is an initial Development retention mechanism, not a final historical aggregation, deletion, export, backup, or production storage policy.

## Runtime configuration

- `METRICS_ENV` — required: `development`, `test`, or `production`.
- `METRICS_SECRET_KEY` — required; production requires at least 50 characters.
- `METRICS_ALLOWED_HOSTS` — required in production.
- `METRICS_SQLITE_PATH` — optional development/test SQLite path.
- `METRICS_TELEMETRY_RETENTION_HOURS` — optional bounded snapshot-retention window; default 168.

Active `.env` files and reusable secrets must not be committed.

## Platform-system status

All seven Integral Platform Systems have been evaluated for this slice:

- **GoreeCloud Manager:** applicable later for approved read-only operational summaries; not implemented.
- **Privacy Shield:** telemetry minimization and bounded retention concerns apply. Metrics source implements application-local minimization/retention behavior, but no approved Privacy Shield adapter/contract validation or acceptance exists.
- **Wardveil Security:** authentication, credential protection, transport, validation, auditing, and exposure controls apply. Application-local controls exist, but current Wardveil integration/acceptance is not implemented.
- **Everkeep:** configuration, system/agent records, required telemetry history, and secret-recovery procedures require a recovery model; not implemented or accepted.
- **Glaze UI:** applicable to future user/admin surfaces; no Metrics UI exists yet.
- **GoreeCloud Mesh:** applicable to platform identity, discovery, relationships, capabilities, and events; not implemented.
- **GoreeCloud Identity:** applicable to human, service, device/agent, authentication, and authorization boundaries; not implemented. Metrics-local credentials remain a temporary application authority for this Development protocol.

Notify, Inventory, and Monitor integration also remain planned where applicable.

## Platform declaration discrepancy

The current Application and Service Production Readiness standard refers to a repository-owned `goreecloud.platform.yaml` as the common machine-readable record. The current GoreeCloud Platform Improvement Task List still records definition of that standard Platform Contract and manifest schema as unfinished. Metrics does not invent an application-local schema while those authoritative records disagree. This discrepancy remains a platform governance blocker to machine-readable Metrics conformance declaration.

## Explicit limitations and blockers

Not implemented or accepted in this revision:

- production deployment and target-environment transport;
- reverse-proxy/TLS acceptance;
- production agent package/service lifecycle, sandbox, least-privilege unit, update, rollback, or resource-use evidence;
- credential rotation/recovery and production secret storage;
- GoreeCloud Identity;
- Wardveil Security;
- Privacy Shield adapter acceptance;
- Everkeep backup/restore;
- GoreeCloud Mesh;
- GoreeCloud Manager;
- Glaze UI;
- authorized human/admin telemetry read APIs;
- rate limiting and complete audit-event integration;
- production metrics storage;
- historical aggregation/downsampling;
- CPU utilization derivation from successive counters;
- container, GPU, SMART/NVMe/ZFS/RAID, temperature, fan, battery, UPS, or other advanced collectors;
- alerts, Notify publishing, capacity analysis, export/import, and portability.

## Release boundary

`0.1.0-dev.2` may become source-validated after exact-head CI passes. Source validation does not establish integration validation, target-environment validation, security acceptance, recovery acceptance, production deployment, or Stable qualification.
