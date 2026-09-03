"""Narrow service health and Metrics Agent protocol endpoints."""

from __future__ import annotations

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .enrollment import EnrollmentError, consume_agent_enrollment
from .protocol import (
    ENROLLMENT_BODY_LIMIT,
    TELEMETRY_BODY_LIMIT,
    ProtocolError,
    read_agent_authorization,
    read_json_object,
)
from .telemetry import TelemetryError, ingest_agent_telemetry
from .version import current_version


def _no_store(response: JsonResponse) -> JsonResponse:
    response.headers["Cache-Control"] = "no-store"
    return response


@require_GET
def livez(_request):
    """Process liveness only; intentionally does not disclose system details."""
    return JsonResponse({"status": "alive"})


@require_GET
def readyz(_request):
    """Database-aware readiness without returning dependency details."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "not_ready"}, status=503)
    return JsonResponse({"status": "ready"})


@require_GET
def service_status(_request):
    """Bounded source identity for development and integration diagnostics."""
    return JsonResponse(
        {
            "service": "goreecloud-metrics",
            "product": "GoreeCloud Metrics",
            "version": current_version(),
            "lifecycle": "development",
            "api_version": "v1",
        }
    )


@csrf_exempt
@require_POST
def agent_enroll(request):
    """Consume one issued enrollment secret and return the initial agent credential once."""
    if settings.CONFIG.production and not request.is_secure():
        return _no_store(JsonResponse({"error": "enrollment_failed"}, status=400))

    try:
        payload = read_json_object(request, max_bytes=ENROLLMENT_BODY_LIMIT)
        if set(payload) != {"enrollment_id", "enrollment_secret", "agent_version"}:
            raise ProtocolError("Enrollment request could not be accepted.")
        enrolled = consume_agent_enrollment(
            payload["enrollment_id"],
            payload["enrollment_secret"],
            agent_version=payload["agent_version"],
        )
    except (ProtocolError, EnrollmentError, KeyError, TypeError):
        return _no_store(JsonResponse({"error": "enrollment_failed"}, status=400))

    return _no_store(
        JsonResponse(
            {
                "agent_id": str(enrolled.agent_id),
                "credential_id": str(enrolled.credential_id),
                "credential_secret": enrolled.credential_secret,
            },
            status=201,
        )
    )


@csrf_exempt
@require_POST
def agent_telemetry(request):
    """Accept one bounded telemetry sample from an authenticated Metrics Agent."""
    if settings.CONFIG.production and not request.is_secure():
        response = JsonResponse({"error": "authentication_failed"}, status=401)
        response.headers["WWW-Authenticate"] = "Bearer"
        return _no_store(response)

    try:
        credential_id, secret = read_agent_authorization(request)
    except ProtocolError:
        response = JsonResponse({"error": "authentication_failed"}, status=401)
        response.headers["WWW-Authenticate"] = "Bearer"
        return _no_store(response)

    try:
        payload = read_json_object(request, max_bytes=TELEMETRY_BODY_LIMIT)
        accepted = ingest_agent_telemetry(credential_id, secret, payload)
    except (ProtocolError, TelemetryError):
        return _no_store(JsonResponse({"error": "telemetry_rejected"}, status=400))

    return _no_store(
        JsonResponse({"status": "accepted", "sample_id": str(accepted.sample_id)}, status=202)
    )
