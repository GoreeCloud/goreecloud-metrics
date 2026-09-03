# GoreeCloud Metrics — User Manual

## Current status

GoreeCloud Metrics `0.1.0-dev.2` is a **Development source implementation**. It is not a production-ready monitoring service and has no user-facing dashboard yet.

The current source can register monitored systems, issue one-time enrollment credentials, enroll the Development Metrics Agent over the server API, collect a small Linux core resource sample, authenticate telemetry submissions, persist snapshots in the Development database, and prune expired snapshots.

## Server setup

Use Python 3.14 in an isolated environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export PYTHONPATH=src
export METRICS_ENV=development
export METRICS_SECRET_KEY='development-only-change-me'
export METRICS_ALLOWED_HOSTS='localhost,127.0.0.1,[::1]'
export METRICS_TELEMETRY_RETENTION_HOURS=168
python manage.py migrate
python manage.py runserver
```

Do not reuse the example secret in production. SQLite is Development/test storage only.

## Register a monitored system

```bash
python manage.py register_system metrics-node-01 \
  --role infrastructure \
  --environment development \
  --location local
```

The command prints the monitored-system UUID.

Optional metadata is local Metrics metadata and must not be treated as authoritative GoreeCloud Inventory or Mesh integration.

## Issue a one-time enrollment

```bash
python manage.py issue_agent_enrollment <system-uuid> --ttl-minutes 15
```

The command prints the enrollment UUID, expiry, and one-time secret. Copy the secret only through an appropriate secure channel. The server stores a password hash rather than the plaintext secret.

Enrollment lifetime is limited to 24 hours, and issuing a replacement revokes earlier unused enrollment records for the same system.

## Enroll the Development Metrics Agent

The current agent is source-run and Linux-focused; it is not yet an installed production service.

From a checkout containing the same Metrics source:

```bash
export PYTHONPATH=src
export METRICS_ENROLLMENT_SECRET='<one-time-secret>'
python -m metrics_agent enroll \
  --server-url http://127.0.0.1:8000 \
  --enrollment-id <enrollment-uuid>
unset METRICS_ENROLLMENT_SECRET
```

If `METRICS_ENROLLMENT_SECRET` is unset, the agent prompts for it without echoing the secret. The CLI deliberately does not accept the enrollment secret as a command-line argument.

The agent accepts loopback HTTP only for local Development use. A non-loopback server URL must use HTTPS.

Successful enrollment creates:

- a Metrics-local agent identity on the server;
- a per-agent credential whose server-side representation is a password hash;
- local agent state at `~/.local/state/goreecloud/metrics-agent/state.json` by default.

The local state file contains the reusable agent credential and must remain mode `0600`. The agent refuses to load it if group or other permission bits are present. This file-based mechanism is Development-only and is not the final production secret-storage design.

Use `--state-file <path>` to select a different state path. `--replace-state` is required to overwrite an existing state file during enrollment.

## Submit telemetry

Submit one sample:

```bash
python -m metrics_agent once
```

Run the Development collection loop:

```bash
python -m metrics_agent run --interval-seconds 30
```

The collection interval must be between 10 and 3600 seconds. Communication failures use bounded exponential backoff up to five minutes.

The first collector sends:

- logical processor count;
- 1-, 5-, and 15-minute load averages;
- aggregate CPU tick counters;
- total/available memory;
- total/free swap;
- root (`/`) filesystem total/available capacity;
- aggregate non-loopback network received/transmitted bytes;
- sample timestamp, random sample UUID, and agent source version.

It does not collect hostname, IP address, hardware serial number, username, processes, environment variables, command lines, logs, packet contents, or file contents.

A successful sample updates the agent's last-seen/version state and changes a pending system to active. Paused, retired, or revoked agents are rejected.

## Telemetry retention

`METRICS_TELEMETRY_RETENTION_HOURS` defaults to 168 hours and must be between 1 and 2160 hours.

Expired snapshots are pruned when authenticated telemetry is successfully ingested. For an idle Development server, prune explicitly:

```bash
python manage.py prune_telemetry
```

This is not the final historical storage/aggregation policy and is not an Everkeep backup or deletion guarantee.

## Current API endpoints

- `GET /livez/`
- `GET /readyz/`
- `GET /api/v1/status/`
- `POST /api/v1/agents/enroll/`
- `POST /api/v1/agents/telemetry/`

There is intentionally no human telemetry read endpoint yet. GoreeCloud Identity-backed user/admin authorization and a Glaze UI surface have not been implemented.

## Important limitations

- No production deployment or target-host acceptance.
- No accepted production Metrics Agent package or service unit.
- No GoreeCloud Identity, Wardveil Security, Privacy Shield, Everkeep, Mesh, or Manager integration.
- No approved production TLS/reverse-proxy configuration.
- No credential rotation or lost-agent-state recovery workflow.
- No telemetry dashboard or authorized human read API.
- No production metrics database, historical aggregation, or charting.
- No alerts, GoreeCloud Notify publishing, capacity forecasting, container telemetry, GPU telemetry, or advanced hardware/storage-health collectors.
- No backup/restore acceptance.

Do not deploy this Development source as though it were a completed GoreeCloud monitoring platform.
