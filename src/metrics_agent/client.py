"""Bounded outbound protocol client for the development Metrics Agent."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import uuid

from .state import AgentState

_RESPONSE_LIMIT = 16 * 1024
_DEFAULT_TIMEOUT = 10.0
_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


class ClientError(RuntimeError):
    """Raised when agent-server communication cannot safely complete."""


def validate_server_url(value: str) -> str:
    server = value.strip().rstrip("/")
    if not server or len(server) > 2048:
        raise ClientError("Metrics server URL is invalid.")
    parsed = urlsplit(server)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ClientError("Metrics server URL is invalid.")
    if parsed.scheme != "https" and parsed.hostname not in _LOOPBACK_HOSTS:
        raise ClientError("HTTPS is required for non-loopback Metrics servers.")
    return server


def _post_json(
    server_url: str,
    path: str,
    payload: dict,
    *,
    headers: dict[str, str] | None = None,
    expected_status: int,
    timeout: float = _DEFAULT_TIMEOUT,
) -> dict:
    server = validate_server_url(server_url)
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "GoreeCloud-Metrics-Agent",
    }
    if headers:
        request_headers.update(headers)
    request = Request(server + path, data=body, headers=request_headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != expected_status:
                raise ClientError("Metrics server rejected the request.")
            raw = response.read(_RESPONSE_LIMIT + 1)
            if len(raw) > _RESPONSE_LIMIT:
                raise ClientError("Metrics server response was too large.")
            content_type = response.headers.get_content_type()
    except (HTTPError, URLError, TimeoutError, OSError):
        raise ClientError("Metrics server request failed.") from None

    if content_type != "application/json":
        raise ClientError("Metrics server response was invalid.")
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ClientError("Metrics server response was invalid.") from None
    if not isinstance(decoded, dict):
        raise ClientError("Metrics server response was invalid.")
    return decoded


def enroll(
    server_url: str,
    enrollment_id: str,
    enrollment_secret: str,
    *,
    agent_version: str,
) -> AgentState:
    if not enrollment_secret or len(enrollment_secret) > 256:
        raise ClientError("Enrollment secret is invalid.")
    try:
        enrollment_uuid = str(uuid.UUID(enrollment_id))
    except (ValueError, TypeError, AttributeError):
        raise ClientError("Enrollment identifier is invalid.") from None

    response = _post_json(
        server_url,
        "/api/v1/agents/enroll/",
        {
            "enrollment_id": enrollment_uuid,
            "enrollment_secret": enrollment_secret,
            "agent_version": agent_version,
        },
        expected_status=201,
    )
    if set(response) != {"agent_id", "credential_id", "credential_secret"}:
        raise ClientError("Metrics server response was invalid.")
    return AgentState(
        server_url=validate_server_url(server_url),
        agent_id=response["agent_id"],
        credential_id=response["credential_id"],
        credential_secret=response["credential_secret"],
    ).validated()


def submit_telemetry(state: AgentState, snapshot: dict) -> str:
    state = state.validated()
    response = _post_json(
        state.server_url,
        "/api/v1/agents/telemetry/",
        snapshot,
        headers={
            "Authorization": f"Bearer {state.credential_secret}",
            "X-GoreeCloud-Metrics-Credential-ID": state.credential_id,
        },
        expected_status=202,
    )
    if set(response) != {"status", "sample_id"} or response["status"] != "accepted":
        raise ClientError("Metrics server response was invalid.")
    try:
        return str(uuid.UUID(response["sample_id"]))
    except (ValueError, TypeError, AttributeError):
        raise ClientError("Metrics server response was invalid.") from None
