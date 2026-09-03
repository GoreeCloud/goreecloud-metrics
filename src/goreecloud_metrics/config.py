"""Runtime configuration parsing and fail-closed validation."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

_ALLOWED_ENVIRONMENTS = {"development", "test", "production"}
_DEFAULT_RETENTION_HOURS = 168
_MAX_RETENTION_HOURS = 24 * 90


class ConfigurationError(RuntimeError):
    """Raised when runtime configuration is unsafe or incomplete."""


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _retention_hours(value: str) -> int:
    try:
        hours = int(value)
    except ValueError:
        raise ConfigurationError(
            "METRICS_TELEMETRY_RETENTION_HOURS must be an integer."
        ) from None
    if not 1 <= hours <= _MAX_RETENTION_HOURS:
        raise ConfigurationError(
            "METRICS_TELEMETRY_RETENTION_HOURS must be between 1 and 2160 hours."
        )
    return hours


@dataclass(frozen=True)
class RuntimeConfig:
    environment: str
    secret_key: str
    allowed_hosts: tuple[str, ...]
    sqlite_path: Path
    telemetry_retention_hours: int

    @property
    def debug(self) -> bool:
        return self.environment == "development"

    @property
    def production(self) -> bool:
        return self.environment == "production"


def load_runtime_config(base_dir: Path) -> RuntimeConfig:
    environment = os.getenv("METRICS_ENV", "").strip().lower()
    if environment not in _ALLOWED_ENVIRONMENTS:
        expected = ", ".join(sorted(_ALLOWED_ENVIRONMENTS))
        raise ConfigurationError(
            f"METRICS_ENV must be explicitly set to one of: {expected}."
        )

    secret_key = os.getenv("METRICS_SECRET_KEY", "").strip()
    if not secret_key:
        raise ConfigurationError("METRICS_SECRET_KEY must be explicitly configured.")
    if environment == "production" and len(secret_key) < 50:
        raise ConfigurationError(
            "Production METRICS_SECRET_KEY must contain at least 50 characters."
        )

    allowed_hosts = _csv(os.getenv("METRICS_ALLOWED_HOSTS", ""))
    if environment == "production" and not allowed_hosts:
        raise ConfigurationError(
            "METRICS_ALLOWED_HOSTS must be explicitly configured in production."
        )
    if environment != "production" and not allowed_hosts:
        allowed_hosts = ("localhost", "127.0.0.1", "[::1]", "testserver")

    raw_sqlite_path = os.getenv("METRICS_SQLITE_PATH", "metrics.sqlite3").strip()
    sqlite_path = Path(raw_sqlite_path)
    if not sqlite_path.is_absolute():
        sqlite_path = base_dir / sqlite_path

    retention = _retention_hours(
        os.getenv(
            "METRICS_TELEMETRY_RETENTION_HOURS",
            str(_DEFAULT_RETENTION_HOURS),
        ).strip()
    )

    return RuntimeConfig(
        environment=environment,
        secret_key=secret_key,
        allowed_hosts=allowed_hosts,
        sqlite_path=sqlite_path,
        telemetry_retention_hours=retention,
    )
