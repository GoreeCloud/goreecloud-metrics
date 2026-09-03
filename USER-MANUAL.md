# GoreeCloud Metrics — User Manual

## Current status

GoreeCloud Metrics is currently a Development foundation, not a usable infrastructure-monitoring product. This manual documents only the source behavior that exists now.

## What you can use today

The current server exposes three read-only diagnostic endpoints:

- `GET /livez/` — returns `{"status":"alive"}` when the application process is serving requests.
- `GET /readyz/` — verifies the configured development/test database can answer a simple query and returns `{"status":"ready"}` or HTTP 503 with `{"status":"not_ready"}`.
- `GET /api/v1/status/` — returns bounded product, source version, Development lifecycle, and API-version identity.

The current development source also includes local operator primitives to register monitored-system records and issue one-time agent enrollment secrets. There is still no dashboard, network system enrollment, deployed host agent, telemetry collection, alerting, or administrative web interface.

## Running the development server

Use Python 3.14 in an isolated virtual environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export PYTHONPATH=src
export METRICS_ENV=development
export METRICS_SECRET_KEY='development-only-change-me'
export METRICS_ALLOWED_HOSTS='localhost,127.0.0.1,[::1]'
python manage.py migrate
python manage.py runserver
```

Do not reuse the example development secret for a production environment.

## Registering a development monitored system

Run:

```bash
python manage.py register_system metrics-node-01 \
  --role infrastructure \
  --environment development \
  --location local
```

The command prints the new system UUID. System names are unique in the current Metrics database.

Optional fields include `--description`, `--role`, `--environment`, `--location`, and `--platform-identity`. The platform-identity field is only a future relationship reference and is not proof of Mesh or Inventory integration.

## Issuing a one-time enrollment secret

After registering a system, run:

```bash
python manage.py issue_agent_enrollment <system-uuid> --ttl-minutes 15
```

The command prints an enrollment UUID, expiry timestamp, and one-time secret. The secret is displayed only to the caller; Metrics persists a password hash rather than the plaintext value. Enrollment lifetime cannot exceed 24 hours, and issuing a replacement revokes earlier unused enrollment records for that system.

Treat the displayed secret as sensitive. Do not paste it into source control, ordinary logs, screenshots, issue trackers, or documentation. Use only an approved secure transfer channel.

There is no network agent-enrollment endpoint or deployable Metrics Agent yet. The command therefore establishes development/operator state only; it does not complete a production enrollment workflow.

## Configuration

Current variables:

- `METRICS_ENV` — required: `development`, `test`, or `production`.
- `METRICS_SECRET_KEY` — required secret key; production requires at least 50 characters.
- `METRICS_ALLOWED_HOSTS` — required in production.
- `METRICS_SQLITE_PATH` — optional SQLite path for current development/test use.

Active `.env` files are intentionally ignored by source control. `.env.example` contains only safe placeholder values.

## Important limitations

- Metrics is not production-ready.
- SQLite is not a selected production metrics store.
- GoreeCloud Identity authentication and authorization are not implemented.
- Metrics-local agent identity/enrollment records are not GoreeCloud Identity integration.
- Wardveil Security, Privacy Shield, Everkeep, and Mesh integrations are not implemented.
- Glaze UI 2.2.0 is the required future UI target, but no user-facing Metrics UI exists yet.
- Backup/restore, telemetry retention, secure network agent transport, and monitoring behavior do not exist yet.

Do not deploy this development foundation as though it were the planned GoreeCloud Metrics monitoring service.
