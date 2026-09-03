"""Narrow, non-sensitive service health and development status endpoints."""

from __future__ import annotations

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .version import current_version


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
