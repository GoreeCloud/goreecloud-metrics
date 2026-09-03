# GoreeCloud Metrics — Features

This file distinguishes verified source capabilities from planned product capabilities. A roadmap item is not a current feature.

## Current features

At source version `0.1.0-dev.0`:

- narrow process liveness endpoint at `/livez/`;
- database-aware readiness endpoint at `/readyz/`;
- bounded service identity/status endpoint at `/api/v1/status/`;
- explicit runtime environment and secret configuration requirements;
- production host allowlist validation;
- baseline HTTP hardening configuration;
- automated tests for configuration and current HTTP behavior;
- repository validation for mandatory GoreeCloud documentation and environment-file boundaries.

These capabilities form a development foundation; they do not constitute infrastructure monitoring.

## Experimental or partial features

None are currently represented as an experimental user capability.

## Planned features

The canonical GoreeCloud Metrics project specification defines the planned product scope, including host agents, secure enrollment, multi-system monitoring, CPU/memory/storage/network/container/GPU/hardware telemetry, history, alerting, capacity analysis, platform integrations, portability, and recovery.

Those planned capabilities remain unimplemented unless and until repository source, tests, integration evidence, and applicable deployment/production evidence verify them.
