# GoreeCloud Metrics

GoreeCloud Metrics is the in-development first-party GoreeCloud application for infrastructure resource telemetry, hardware health, workload metrics, historical analysis, and capacity visibility.

## Current status

**Development foundation — not Stable, not production-ready, and not yet a monitoring replacement.**

The repository currently implements only the initial native server/API foundation:

- Django 5.2 application skeleton;
- bounded `GET /livez/` liveness endpoint;
- database-aware `GET /readyz/` readiness endpoint;
- bounded `GET /api/v1/status/` source/lifecycle identity endpoint;
- fail-closed runtime configuration validation;
- baseline HTTP hardening;
- source-level tests and CI repository checks.

No host agent, telemetry ingestion, dashboards, historical metrics, alerts, container monitoring, hardware collectors, or production integrations are implemented yet.

## Development setup

Requirements:

- Python 3.14

Create an isolated environment, install the exact development dependency, and run the server with explicit development configuration:

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

The process intentionally refuses to start when `METRICS_ENV` or `METRICS_SECRET_KEY` is not explicitly configured.

Run source validation with:

```bash
export PYTHONPATH=src
export METRICS_ENV=test
export METRICS_SECRET_KEY='test-only-key'
python scripts/validate_repository.py
python manage.py check
python manage.py test tests
```

## Documentation

- [Specifications](SPECIFICATIONS.md)
- [Features](FEATURES.md)
- [Benefits](BENEFITS.md)
- [Competitive objectives](COMPETITIVE-OBJECTIVES.md)
- [Branding](BRANDING.md)
- [User manual](USER-MANUAL.md)
- [Architecture](docs/architecture.md)
- [Platform integration status](docs/platform-integration-status.md)
- [Security status](docs/security.md)
- [Recovery status](docs/recovery.md)

## Platform status

GoreeCloud Metrics is required to integrate substantively with current GoreeCloud platform systems. Those integrations are **not** implied by this repository foundation. Glaze UI 2.2.0 is the required current Stable UI target, but no user-facing Metrics UI exists yet. Wardveil Security, Privacy Shield, Everkeep, GoreeCloud Identity, and GoreeCloud Mesh integration remain unimplemented and therefore block any platform-conformance or production-readiness claim.

The shared machine-readable GoreeCloud platform manifest/schema is not yet treated as an approved contract, so this repository does not invent a local `goreecloud.platform.yaml` format.

## License

GoreeCloud Metrics is licensed under the [GNU Affero General Public License v3.0](LICENSE).
