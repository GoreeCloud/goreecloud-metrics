"""Validation and persistence for the authenticated Metrics Agent telemetry protocol."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone as datetime_timezone
import math
import uuid

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import AgentCredential, AgentIdentity, MonitoredSystem, TelemetrySnapshot

_MAX_SAMPLE_AGE = timedelta(days=1)
_MAX_FUTURE_SKEW = timedelta(minutes=5)
_MAX_COUNTER = (1 << 63) - 1
_MAX_LOAD = 1_000_000.0


class TelemetryError(RuntimeError):
    """Raised when telemetry cannot be safely authenticated, validated, or stored."""


@dataclass(frozen=True)
class AcceptedTelemetry:
    sample_id: uuid.UUID


def _exact_keys(value: object, keys: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise TelemetryError("Telemetry could not be accepted.")
    return value


def _bounded_int(value: object, *, minimum: int = 0, maximum: int = _MAX_COUNTER) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise TelemetryError("Telemetry could not be accepted.")
    return value


def _bounded_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TelemetryError("Telemetry could not be accepted.")
    result = float(value)
    if not math.isfinite(result) or result < 0 or result > _MAX_LOAD:
        raise TelemetryError("Telemetry could not be accepted.")
    return result


def _parse_sampled_at(value: object, *, now: datetime) -> datetime:
    if not isinstance(value, str) or not value or len(value) > 64:
        raise TelemetryError("Telemetry could not be accepted.")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        raise TelemetryError("Telemetry could not be accepted.") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TelemetryError("Telemetry could not be accepted.")
    normalized = parsed.astimezone(datetime_timezone.utc)
    if normalized < now - _MAX_SAMPLE_AGE or normalized > now + _MAX_FUTURE_SKEW:
        raise TelemetryError("Telemetry could not be accepted.")
    return normalized


def _validate_payload(payload: object) -> dict:
    root = _exact_keys(
        payload,
        {
            "schema_version",
            "sample_id",
            "sampled_at",
            "agent_version",
            "cpu",
            "memory",
            "filesystem",
            "network",
        },
    )
    if _bounded_int(root["schema_version"], minimum=1, maximum=1) != 1:
        raise TelemetryError("Telemetry could not be accepted.")

    try:
        sample_id = uuid.UUID(str(root["sample_id"]))
    except (ValueError, TypeError, AttributeError):
        raise TelemetryError("Telemetry could not be accepted.") from None

    agent_version = root["agent_version"]
    if not isinstance(agent_version, str):
        raise TelemetryError("Telemetry could not be accepted.")
    agent_version = agent_version.strip()
    if not agent_version or len(agent_version) > 64:
        raise TelemetryError("Telemetry could not be accepted.")

    now = timezone.now()
    sampled_at = _parse_sampled_at(root["sampled_at"], now=now)

    cpu = _exact_keys(
        root["cpu"],
        {
            "logical_processors",
            "load_1",
            "load_5",
            "load_15",
            "user_ticks",
            "nice_ticks",
            "system_ticks",
            "idle_ticks",
            "iowait_ticks",
            "irq_ticks",
            "softirq_ticks",
            "steal_ticks",
        },
    )
    memory = _exact_keys(
        root["memory"],
        {"total_bytes", "available_bytes", "swap_total_bytes", "swap_free_bytes"},
    )
    filesystem = _exact_keys(root["filesystem"], {"mount", "total_bytes", "available_bytes"})
    network = _exact_keys(root["network"], {"rx_bytes", "tx_bytes"})

    logical_processors = _bounded_int(cpu["logical_processors"], minimum=1, maximum=65535)
    memory_total = _bounded_int(memory["total_bytes"])
    memory_available = _bounded_int(memory["available_bytes"])
    swap_total = _bounded_int(memory["swap_total_bytes"])
    swap_free = _bounded_int(memory["swap_free_bytes"])
    filesystem_total = _bounded_int(filesystem["total_bytes"])
    filesystem_available = _bounded_int(filesystem["available_bytes"])

    if memory_available > memory_total or swap_free > swap_total or filesystem_available > filesystem_total:
        raise TelemetryError("Telemetry could not be accepted.")
    if filesystem["mount"] != "/":
        raise TelemetryError("Telemetry could not be accepted.")

    return {
        "sample_id": sample_id,
        "schema_version": 1,
        "sampled_at": sampled_at,
        "agent_version": agent_version,
        "logical_processors": logical_processors,
        "load_1": _bounded_float(cpu["load_1"]),
        "load_5": _bounded_float(cpu["load_5"]),
        "load_15": _bounded_float(cpu["load_15"]),
        "cpu_user_ticks": _bounded_int(cpu["user_ticks"]),
        "cpu_nice_ticks": _bounded_int(cpu["nice_ticks"]),
        "cpu_system_ticks": _bounded_int(cpu["system_ticks"]),
        "cpu_idle_ticks": _bounded_int(cpu["idle_ticks"]),
        "cpu_iowait_ticks": _bounded_int(cpu["iowait_ticks"]),
        "cpu_irq_ticks": _bounded_int(cpu["irq_ticks"]),
        "cpu_softirq_ticks": _bounded_int(cpu["softirq_ticks"]),
        "cpu_steal_ticks": _bounded_int(cpu["steal_ticks"]),
        "memory_total_bytes": memory_total,
        "memory_available_bytes": memory_available,
        "swap_total_bytes": swap_total,
        "swap_free_bytes": swap_free,
        "root_filesystem_total_bytes": filesystem_total,
        "root_filesystem_available_bytes": filesystem_available,
        "network_rx_bytes": _bounded_int(network["rx_bytes"]),
        "network_tx_bytes": _bounded_int(network["tx_bytes"]),
    }


@transaction.atomic
def ingest_agent_telemetry(
    credential_id: uuid.UUID | str,
    secret: str,
    payload: object,
) -> AcceptedTelemetry:
    values = _validate_payload(payload)
    try:
        credential = (
            AgentCredential.objects.select_for_update()
            .select_related("agent", "agent__system")
            .get(pk=credential_id)
        )
    except (AgentCredential.DoesNotExist, ValidationError, ValueError, TypeError):
        raise TelemetryError("Telemetry could not be accepted.") from None

    now = timezone.now()
    agent = credential.agent
    system = agent.system
    invalid_credential = (
        not secret
        or credential.revoked_at is not None
        or (credential.expires_at is not None and credential.expires_at <= now)
        or agent.state != AgentIdentity.State.ACTIVE
        or agent.revoked_at is not None
        or system.monitoring_state in {
            MonitoredSystem.MonitoringState.PAUSED,
            MonitoredSystem.MonitoringState.RETIRED,
        }
        or not check_password(secret, credential.secret_hash)
    )
    if invalid_credential:
        raise TelemetryError("Telemetry could not be accepted.")

    retention_cutoff = now - timedelta(hours=settings.CONFIG.telemetry_retention_hours)
    TelemetrySnapshot.objects.filter(received_at__lt=retention_cutoff).delete()

    try:
        TelemetrySnapshot.objects.create(agent=agent, **values)
    except IntegrityError:
        raise TelemetryError("Telemetry could not be accepted.") from None

    credential.last_used_at = now
    credential.save(update_fields=("last_used_at",))

    agent.last_seen_at = now
    agent.version = values["agent_version"]
    agent.save(update_fields=("last_seen_at", "version"))

    if system.monitoring_state == MonitoredSystem.MonitoringState.PENDING:
        system.monitoring_state = MonitoredSystem.MonitoringState.ACTIVE
        system.save(update_fields=("monitoring_state", "updated_at"))

    return AcceptedTelemetry(sample_id=values["sample_id"])
