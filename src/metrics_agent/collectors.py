"""Minimal Linux host resource collectors for the development Metrics Agent."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import uuid

from .version import current_version


class CollectorError(RuntimeError):
    """Raised when a required core resource sample cannot be collected safely."""


def _read_cpu(proc_root: Path) -> dict:
    try:
        first_line = (proc_root / "stat").read_text(encoding="utf-8").splitlines()[0]
        parts = first_line.split()
        if not parts or parts[0] != "cpu" or len(parts) < 9:
            raise CollectorError("CPU telemetry is unavailable.")
        values = [int(value) for value in parts[1:9]]
    except (OSError, UnicodeDecodeError, ValueError, IndexError):
        raise CollectorError("CPU telemetry is unavailable.") from None

    names = ("user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal")
    ticks = dict(zip(names, values, strict=True))
    try:
        loads = os.getloadavg()
    except OSError:
        raise CollectorError("CPU telemetry is unavailable.") from None
    logical_processors = os.cpu_count() or 1
    return {
        "logical_processors": logical_processors,
        "load_1": loads[0],
        "load_5": loads[1],
        "load_15": loads[2],
        **{f"{name}_ticks": ticks[name] for name in names},
    }


def _read_memory(proc_root: Path) -> dict:
    try:
        rows = {}
        for line in (proc_root / "meminfo").read_text(encoding="utf-8").splitlines():
            key, _, remainder = line.partition(":")
            pieces = remainder.strip().split()
            if pieces and pieces[0].isdigit():
                rows[key] = int(pieces[0]) * 1024
        required = ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree")
        if any(key not in rows for key in required):
            raise CollectorError("Memory telemetry is unavailable.")
    except (OSError, UnicodeDecodeError, ValueError):
        raise CollectorError("Memory telemetry is unavailable.") from None
    return {
        "total_bytes": rows["MemTotal"],
        "available_bytes": rows["MemAvailable"],
        "swap_total_bytes": rows["SwapTotal"],
        "swap_free_bytes": rows["SwapFree"],
    }


def _read_filesystem() -> dict:
    try:
        status = os.statvfs("/")
    except OSError:
        raise CollectorError("Filesystem telemetry is unavailable.") from None
    return {
        "mount": "/",
        "total_bytes": status.f_blocks * status.f_frsize,
        "available_bytes": status.f_bavail * status.f_frsize,
    }


def _read_network(proc_root: Path) -> dict:
    rx = 0
    tx = 0
    try:
        lines = (proc_root / "net" / "dev").read_text(encoding="utf-8").splitlines()[2:]
        for line in lines:
            interface, separator, values = line.partition(":")
            if not separator:
                raise CollectorError("Network telemetry is unavailable.")
            name = interface.strip()
            fields = values.split()
            if len(fields) < 16:
                raise CollectorError("Network telemetry is unavailable.")
            if name == "lo":
                continue
            rx += int(fields[0])
            tx += int(fields[8])
    except (OSError, UnicodeDecodeError, ValueError):
        raise CollectorError("Network telemetry is unavailable.") from None
    return {"rx_bytes": rx, "tx_bytes": tx}


def collect_snapshot(*, proc_root: Path = Path("/proc")) -> dict:
    """Collect only the first approved core resource fields for one host sample."""
    return {
        "schema_version": 1,
        "sample_id": str(uuid.uuid4()),
        "sampled_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "agent_version": current_version(),
        "cpu": _read_cpu(proc_root),
        "memory": _read_memory(proc_root),
        "filesystem": _read_filesystem(),
        "network": _read_network(proc_root),
    }
