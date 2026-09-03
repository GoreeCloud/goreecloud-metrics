"""Restricted local development state for one Metrics Agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import stat
import tempfile
import uuid


class StateError(RuntimeError):
    """Raised when local agent state cannot be safely used."""


@dataclass(frozen=True)
class AgentState:
    server_url: str
    agent_id: str
    credential_id: str
    credential_secret: str

    def validated(self) -> "AgentState":
        server = self.server_url.strip().rstrip("/")
        if not server or len(server) > 2048:
            raise StateError("Agent state is invalid.")
        try:
            uuid.UUID(self.agent_id)
            uuid.UUID(self.credential_id)
        except (ValueError, TypeError, AttributeError):
            raise StateError("Agent state is invalid.") from None
        if not self.credential_secret or len(self.credential_secret) > 256:
            raise StateError("Agent state is invalid.")
        return AgentState(
            server_url=server,
            agent_id=self.agent_id,
            credential_id=self.credential_id,
            credential_secret=self.credential_secret,
        )


def save_state(path: Path, state: AgentState, *, replace: bool = False) -> None:
    target = path.expanduser()
    state = state.validated()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not replace:
        raise StateError("Agent state already exists.")

    fd, temporary_name = tempfile.mkstemp(prefix=".metrics-agent-", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_state(path: Path) -> AgentState:
    target = path.expanduser()
    try:
        mode = target.stat().st_mode
    except FileNotFoundError:
        raise StateError("Agent state is unavailable.") from None
    if mode & 0o077:
        raise StateError("Agent state permissions are too broad.")

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise StateError("Agent state is invalid.") from None

    required = {"server_url", "agent_id", "credential_id", "credential_secret"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise StateError("Agent state is invalid.")
    try:
        state = AgentState(**payload)
    except TypeError:
        raise StateError("Agent state is invalid.") from None
    return state.validated()
