# GoreeCloud Metrics

GoreeCloud Metrics is the in-development first-party GoreeCloud application for infrastructure resource telemetry, hardware health, workload metrics, historical analysis, and capacity visibility.

## Current status

**Development source — not Stable, not production-ready, and not yet a monitoring replacement.**

Source version `0.1.0-dev.2` adds the first end-to-end Metrics-owned host telemetry path:

- Django 5.2 server/API foundation with bounded liveness, readiness, and source-status endpoints;
- durable monitored-system, Metrics-local agent identity, one-time enrollment, credential, and telemetry snapshot records;
- `POST /api/v1/agents/enroll/` for one-time development agent enrollment;
- `POST /api/v1/agents/telemetry/` for authenticated, strictly validated telemetry intake;
- a native Python development Metrics Agent that initiates outbound communication and collects a minimized Linux core sample from `/proc`, `statvfs`, and load-average interfaces;
- core CPU/load, memory/swap, root-filesystem capacity, and aggregate non-loopback network counters;
- one-time enrollment and agent credential material stored server-side only as password hashes;
- owner-only (`0600`) local agent state, with HTTPS required by the agent for non-loopback servers;
- strict request/body/schema limits, sample timestamp bounds, duplicate sample rejection, revocation enforcement, and paused/retired-system enforcement;
- development telemetry retention bounded to 1–2160 hours, defaulting to 168 hours, with pruning during ingestion and an explicit prune command;
- migrations, negative-path tests, and CI validation.

This source does **not** yet provide a production deployment, accepted Metrics Agent package/service, user-facing dashboard, authorized telemetry read API, container/GPU/storage-health collectors, alerting, production metrics database, GoreeCloud Identity integration, Wardveil Security acceptance, Privacy Shield adapter acceptance, Everkeep recovery, Mesh integration, or Glaze UI surface.

## Development setup

Requirements:

- Python 3.14

Create an isolated environment and run the server with explicit development configuration:

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

SQLite remains a development/test persistence dependency only.

## Development agent flow

Register a system and issue a short-lived one-time enrollment secret:

```bash
python manage.py register_system metrics-node-01 --role infrastructure --environment development
python manage.py issue_agent_enrollment <system-uuid> --ttl-minutes 15
```

On the monitored Linux system, use the one-time secret through the environment or interactive prompt rather than a command-line argument:

```bash
export PYTHONPATH=src
export METRICS_ENROLLMENT_SECRET='<one-time-secret>'
python -m metrics_agent enroll \
  --server-url http://127.0.0.1:8000 \
  --enrollment-id <enrollment-uuid>
unset METRICS_ENROLLMENT_SECRET
```

Loopback HTTP is permitted only for development. The agent refuses non-loopback HTTP and requires HTTPS for remote servers.

Submit one sample:

```bash
python -m metrics_agent once
```

Or run the development collection loop:

```bash
python -m metrics_agent run --interval-seconds 30
```

The agent state file defaults to `~/.local/state/goreecloud/metrics-agent/state.json` and is required to remain owner-only. The current file-based credential storage is a Development mechanism, not an accepted production secret-management design.

Prune snapshots older than the configured retention window, including during idle development periods:

```bash
python manage.py prune_telemetry
```

## Validation

```bash
export PYTHONPATH=src
export METRICS_ENV=test
export METRICS_SECRET_KEY='test-only-key'
python scripts/validate_repository.py
python -m compileall -q manage.py src tests scripts
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py check
python manage.py test tests -v 2
```

GitHub Actions also runs production-oriented Django deployment checks. Passing source CI does not establish deployment, security-integration, recovery, or production acceptance.

## Documentation

- [Specifications](SPECIFICATIONS.md)
- [Features](FEATURES.md)
- [Benefits](BENEFITS.md)
- [Competitive objectives](COMPETITIVE-OBJECTIVES.md)
- [Branding](BRANDING.md)
- [User manual](USER-MANUAL.md)
- [Architecture](docs/architecture.md)
- [Agent protocol](docs/agent-protocol.md)
- [Platform integration status](docs/platform-integration-status.md)
- [Security status](docs/security.md)
- [Recovery status](docs/recovery.md)

## Platform Contract

The central GoreeCloud Platform Contract is now defined at schema version `0.2`. This repository carries a root `goreecloud.platform.yaml` declaration and an immutable-pinned reusable validation workflow for that shared contract.

The manifest records Metrics as Development and `nonconformant`; it preserves blocked or migration-required Integral Platform System relationships and contains no fabricated acceptance-test or release evidence. Manifest adoption therefore does not establish Stable qualification, production deployment, platform-system acceptance, or production readiness.

## License

GoreeCloud Metrics is licensed under the [GNU Affero General Public License v3.0](LICENSE).
