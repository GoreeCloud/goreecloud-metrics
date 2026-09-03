# GoreeCloud Metrics — Initial Architecture

## Status

Development source architecture for `0.1.0-dev.2`. This document describes implemented source behavior and explicit next boundaries. It is not a production-acceptance record.

## Implemented components

### Metrics server

The GoreeCloud-owned Django 5.2 application provides:

- liveness, database-aware readiness, and bounded source status;
- monitored-system and Metrics-local agent identity persistence;
- one-time enrollment and agent credential persistence using password hashes;
- one-time network enrollment;
- authenticated telemetry intake;
- strict telemetry validation and bounded Development retention.

SQLite is used only for Development/test persistence. Production storage remains undecided.

### Development Metrics Agent

`src/metrics_agent/` is a first-party outbound-only Python agent. It currently:

- enrolls with a one-time credential;
- stores the resulting per-agent credential in an owner-only Development state file;
- requires HTTPS for non-loopback server connections;
- collects the first Linux core resource sample;
- submits once or continuously with a bounded configurable interval;
- backs off on collection or network failures;
- exposes no remote shell, administration port, or monitored-host listener.

### Telemetry protocol

The version-1 payload is an intentionally strict fixed JSON contract. Unknown root or nested fields are rejected. Requests and responses are bounded, credentials are carried only in the machine authentication boundary, and sample UUIDs prevent duplicate persistence.

See [`agent-protocol.md`](agent-protocol.md).

## Data relationships

```text
MonitoredSystem
  ├── AgentEnrollment (history)
  └── AgentIdentity (one current Metrics-local identity)
        ├── AgentCredential (history)
        └── TelemetrySnapshot (bounded core samples)
```

Deletion uses protective relationships for identity/history-bearing records. Agent revocation is represented as state rather than deleting history.

## Trust and authority boundaries

- A one-time enrollment secret authorizes only the bounded enrollment operation.
- An agent credential authenticates the Metrics-local agent to the telemetry endpoint; it is not a human/admin credential.
- Metrics-local identity is not GoreeCloud Identity.
- Source-level hashing, validation, TLS requirements, and revocation are application controls, not Wardveil acceptance.
- Telemetry minimization and current retention logic are application-local privacy behavior, not approved Privacy Shield integration.
- `platform_identity` is a future relationship reference and is not Mesh or Inventory authority.
- No human telemetry read API is exposed until an appropriate authorization model exists.

## Privacy-minimized first collector

The initial sample is limited to resource measurements required for the first monitoring purpose. It excludes stable host/network identifiers and private workload/content data.

This keeps the first telemetry path useful enough to validate collection and transport while avoiding premature collection of process, command, log, filesystem-content, packet-content, or detailed identity data.

## Retention architecture

The current source limits snapshot retention to 1–2160 hours with a 168-hour default. Successful ingestion prunes globally expired snapshots. `prune_telemetry` provides an explicit idle-period cleanup path.

Historical aggregation, downsampling, backup classification, deletion guarantees, export, and production storage lifecycle remain unimplemented.

## Network boundary

The monitored host initiates communication. No inbound Metrics Agent listener is required.

Development loopback HTTP is allowed. The agent rejects non-loopback HTTP, and server endpoints reject insecure requests when the server is configured as production. No target deployment, reverse proxy, certificate, firewall, or Wardveil transport acceptance is claimed.

## Next architecture boundaries

Major unimplemented boundaries include:

- GoreeCloud Identity-backed human/service/device authentication and authorization;
- accepted Wardveil, Privacy Shield, Everkeep, Mesh, Manager, and Glaze UI integration;
- production Metrics Agent packaging, service sandbox, permissions, update/rollback, credential rotation, and recovery;
- production metrics storage and retention jobs;
- authorized telemetry query/read models and historical aggregation;
- derived utilization calculations and additional collectors;
- alert evaluation and Notify publishing;
- backup, restore, export/import, portability, deployment, and production acceptance.

## Platform-manifest governance discrepancy

The current production-readiness standard references a repository-owned `goreecloud.platform.yaml`, while the current platform improvement task list still records the standard contract/schema definition as unfinished. Metrics does not create a competing schema until the authoritative platform contract is reconciled.
