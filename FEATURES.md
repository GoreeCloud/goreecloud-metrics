# GoreeCloud Metrics — Features

This file distinguishes verified source capabilities from planned product capabilities. A roadmap item is not a current feature.

## Current features

At source version `0.1.0-dev.1`:

- narrow process liveness endpoint at `/livez/`;
- database-aware readiness endpoint at `/readyz/`;
- bounded service identity/status endpoint at `/api/v1/status/`;
- explicit runtime environment and secret configuration requirements;
- production host allowlist validation;
- baseline HTTP hardening configuration;
- durable development records for monitored systems;
- one Metrics-local agent identity per monitored system;
- one-time agent-enrollment records with bounded expiry, usage, and revocation state;
- enrollment and agent credential secrets stored only as password hashes, with plaintext values returned only at issuance boundaries;
- agent revocation that preserves history and revokes active credential records;
- local management commands to register a system and issue a one-time enrollment secret;
- automated tests for configuration, HTTP behavior, enrollment fail-closed behavior, secret non-persistence, one-time consumption, and revocation;
- repository validation for mandatory GoreeCloud documentation and environment-file boundaries.

These capabilities form a development foundation; they do not yet constitute infrastructure monitoring or a deployable agent-enrollment service.

## Experimental or partial features

Agent enrollment is **partial**: the domain model and internal cryptographic-secret lifecycle primitives exist, but there is no public/network enrollment endpoint, certificate flow, deployed Metrics Agent, production credential transport, GoreeCloud Identity integration, or Wardveil acceptance evidence.

Multi-system monitoring is **partial** only at the identity-record layer: multiple monitored-system records can exist, but no telemetry is collected from them yet.

## Planned features

The canonical GoreeCloud Metrics project specification defines the planned product scope, including host agents, secure network enrollment, multi-system monitoring, CPU/memory/storage/network/container/GPU/hardware telemetry, history, alerting, capacity analysis, platform integrations, portability, and recovery.

Those planned capabilities remain unimplemented unless and until repository source, tests, integration evidence, and applicable deployment/production evidence verify them.
