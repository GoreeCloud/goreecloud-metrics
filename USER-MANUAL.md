# GoreeCloud Metrics — User Manual

## Current status

GoreeCloud Metrics is currently a Development foundation, not a usable infrastructure-monitoring product. This manual documents only the source behavior that exists now.

## What you can use today

The current server exposes three read-only diagnostic endpoints:

- `GET /livez/` — returns `{"status":"alive"}` when the application process is serving requests.
- `GET /readyz/` — verifies the configured development/test database can answer a simple query and returns `{"status":"ready"}` or HTTP 503 with `{"status":"not_ready"}`.
- `GET /api/v1/status/` — returns bounded product, source version, Development lifecycle, and API-version identity.

There is no dashboard, system enrollment, host agent, telemetry collection, alerting, or administrative interface yet.

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
python manage.py runserver
```

Do not reuse the example development secret for a production environment.

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
- Wardveil Security, Privacy Shield, Everkeep, and Mesh integrations are not implemented.
- Glaze UI 2.2.0 is the required future UI target, but no user-facing Metrics UI exists yet.
- Backup/restore, telemetry retention, agent enrollment, and monitoring behavior do not exist yet.

Do not deploy this development foundation as though it were the planned GoreeCloud Metrics monitoring service.
