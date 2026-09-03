"""Delete telemetry snapshots older than the configured development retention window."""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from metrics.models import TelemetrySnapshot


class Command(BaseCommand):
    help = "Prune telemetry snapshots older than METRICS_TELEMETRY_RETENTION_HOURS."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=settings.CONFIG.telemetry_retention_hours)
        deleted, _details = TelemetrySnapshot.objects.filter(received_at__lt=cutoff).delete()
        self.stdout.write(f"Pruned {deleted} expired telemetry record(s).")
