# GoreeCloud Metrics — Features

This file distinguishes verified source capabilities from planned product capabilities. A roadmap item is not a current feature.

## Current source features

At source version `0.1.0-dev.2`:

- bounded liveness, readiness, and service-status endpoints;
- explicit runtime configuration and production host allowlist validation;
- baseline HTTP hardening and bounded request-body memory;
- durable monitored-system and Metrics-local agent identity records;
- one-time expiring enrollment credentials and hashed agent credential records;
- network one-time agent enrollment endpoint;
- authenticated agent telemetry endpoint;
- native Development Linux Metrics Agent with outbound-only communication;
- CPU/load, memory/swap, root-filesystem capacity, and aggregate non-loopback network collection;
- strict telemetry schema, timestamp, counter, relationship, payload-size, credential, revocation, and monitoring-state validation;
- duplicate sample rejection;
- agent last-seen/version updates and pending-to-active system transition on accepted telemetry;
- owner-only local agent state validation;
- non-loopback HTTPS enforcement by the agent;
- bounded Development snapshot retention and telemetry pruning;
- source tests, migrations, repository validation, and CI.

## Partial Development capabilities

**Agent enrollment:** usable at the Development source level, but not yet integrated with GoreeCloud Identity or accepted Wardveil service/device identity and transport contracts. No production packaging or deployment evidence exists.

**Metrics Agent:** can collect and continuously submit the first minimized Linux core resource sample, but it has no production service unit, packaging, update/rollback, privilege-hardening evidence, capability negotiation, offline queue, credential rotation, or hardware/container collectors.

**Multi-system telemetry:** the server can associate accepted snapshots with multiple registered monitored systems and their agents. There is no authorized human telemetry read API, dashboard, historical charting engine, aggregation, or alerting yet.

**Privacy behavior:** the current source minimizes the first telemetry payload and applies bounded snapshot retention. This is not a claim of approved Privacy Shield integration.

## Planned features

The canonical GoreeCloud Metrics project specification defines the larger planned scope, including advanced host and hardware collectors, containers, historical analysis, alerting, capacity planning, Glaze UI experiences, API consumers, export/import, recovery, and all required GoreeCloud platform integrations.

Those capabilities remain planned unless separate implementation and evidence verify them.
