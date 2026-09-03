"""Bounded JSON and credential parsing for the Metrics Agent protocol."""

from __future__ import annotations

import json
import uuid

from django.http import HttpRequest

ENROLLMENT_BODY_LIMIT = 8 * 1024
TELEMETRY_BODY_LIMIT = 32 * 1024


class ProtocolError(RuntimeError):
    """Raised when a network request does not satisfy the bounded protocol contract."""


def read_json_object(request: HttpRequest, *, max_bytes: int) -> dict:
    content_type = request.headers.get("Content-Type", "").partition(";")[0].strip().lower()
    if content_type != "application/json":
        raise ProtocolError("Request body could not be accepted.")

    length_header = request.headers.get("Content-Length")
    if not length_header:
        raise ProtocolError("Request body could not be accepted.")
    try:
        declared_length = int(length_header)
    except ValueError:
        raise ProtocolError("Request body could not be accepted.") from None
    if declared_length <= 0 or declared_length > max_bytes:
        raise ProtocolError("Request body could not be accepted.")

    body = request.body
    if not body or len(body) > max_bytes:
        raise ProtocolError("Request body could not be accepted.")

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProtocolError("Request body could not be accepted.") from None

    if not isinstance(payload, dict):
        raise ProtocolError("Request body could not be accepted.")
    return payload


def read_agent_authorization(request: HttpRequest) -> tuple[uuid.UUID, str]:
    credential_header = request.headers.get("X-GoreeCloud-Metrics-Credential-ID", "").strip()
    authorization = request.headers.get("Authorization", "")
    if not credential_header or not authorization.startswith("Bearer "):
        raise ProtocolError("Agent authentication failed.")

    try:
        credential_id = uuid.UUID(credential_header)
    except (ValueError, TypeError, AttributeError):
        raise ProtocolError("Agent authentication failed.") from None

    secret = authorization[7:].strip()
    if not secret or len(secret) > 256:
        raise ProtocolError("Agent authentication failed.")
    return credential_id, secret
