"""Issue a one-time agent enrollment secret to an authorized local operator."""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from metrics.enrollment import EnrollmentError, issue_agent_enrollment
from metrics.models import MonitoredSystem


class Command(BaseCommand):
    help = "Issue a bounded one-time enrollment secret for a registered system."

    def add_arguments(self, parser):
        parser.add_argument("system_id")
        parser.add_argument("--ttl-minutes", type=int, default=15)

    def handle(self, *args, **options):
        try:
            system = MonitoredSystem.objects.get(pk=options["system_id"])
        except (MonitoredSystem.DoesNotExist, ValidationError, ValueError):
            raise CommandError("Unknown monitored system.") from None

        try:
            issued = issue_agent_enrollment(
                system,
                ttl=timedelta(minutes=options["ttl_minutes"]),
            )
        except EnrollmentError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(f"Enrollment ID: {issued.enrollment_id}")
        self.stdout.write(f"Expires: {issued.expires_at.isoformat()}")
        self.stdout.write("Secret (shown once; store only in an approved secure channel):")
        self.stdout.write(issued.secret)
