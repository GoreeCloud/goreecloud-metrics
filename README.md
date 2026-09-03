# GoreeCloud Metrics

GoreeCloud Metrics is the in-development first-party GoreeCloud application for infrastructure resource telemetry, hardware health, workload metrics, historical analysis, and capacity visibility.

## Current status

**Development foundation — not Stable, not production-ready, and not yet a monitoring replacement.**

The repository currently implements a native server/API foundation plus the first Metrics-owned system and agent identity primitives:

- Django 5.2 application skeleton;
- bounded `GET /livez/` liveness endpoint;
- database-aware `GET /readyz/` readiness endpoint;
- bounded `GET /api/v1/status/` source/lifecycle identity endpoint;
- fail-closed runtime configuration validation;
- baseline HTTP hardening;
- durable development models for monitored systems, agent identities, one-time enrollment records, and agent credential metadata;
- one-time enrollment issuance/consumption primitives that persist only password hashes, never returned plaintext secrets;
- agent revocation that preserves history and revokes active credential records;
- local management commands for registering systems and issuing one-time enrollment secrets;
- source-level tests, migrations, and CI repository checks.

There is still **no network agent-enrollment endpoint, deployed Metrics Agent, telemetry ingestion, dashboard, historical metrics engine, resource alerts, container monitoring, hardware collectors, or production platform integration**.

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
python manage.py migrate
python manage.py runserver
```

The process intentionally refuses to start when `METRICS_ENV` or `METRICS_SECRET_KEY` is not explicitly configured.

Run source validation with:

```bash
export PYTHONPATH=src
export METRICS_ENV=test
export METRICS_SECRET_KEY='test-only-key'
python scripts/validate_repository.py
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py test tests
```

## Development-only system and enrollment flow

Register a system record locally:

```bash
python manage.py register_system metrics-node-01 --role infrastructure --environment development
```

Issue a bounded one-time enrollment secret for that system UUID:

```bash
python manage.py issue_agent_enrollment <system-uuid> --ttl-minutes 15
```

The enrollment secret is displayed once. The database stores only a password hash. Treat the displayed value as sensitive and transmit it only through an approved secure channel. No network enrollment transport exists yet, so these commands are development/operator primitives rather than a complete deployable enrollment workflow.

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

GoreeCloud Metrics is required to integrate substantively with current GoreeCloud platform systems. Those integrations are **not** implied by the local system/agent domain foundation. Glaze UI 2.2.0 is the required current Stable UI target, but no user-facing Metrics UI exists yet. Wardveil Security, Privacy Shield, Everkeep, GoreeCloud Identity, and GoreeCloud Mesh integration remain unimplemented and therefore block any platform-conformance or production-readiness claim.

The shared machine-readable GoreeCloud platform manifest/schema is not yet treated as an approved contract, so this repository does not invent a local `goreecloud.platform.yaml` format.

## License

GoreeCloud Metrics is licensed under the [GNU Affero General Public License v3.0](LICENSE).
