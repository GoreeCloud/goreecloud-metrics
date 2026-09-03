"""Register a monitored system without exposing an administrative HTTP surface."""

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from metrics.models import MonitoredSystem


class Command(BaseCommand):
    help = "Register a GoreeCloud Metrics monitored-system record."

    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("--description", default="")
        parser.add_argument("--role", default="")
        parser.add_argument("--environment", default="")
        parser.add_argument("--location", default="")
        parser.add_argument("--platform-identity", default="")

    def handle(self, *args, **options):
        name = options["name"].strip()
        if not name:
            raise CommandError("System name must not be empty.")

        try:
            system = MonitoredSystem.objects.create(
                name=name,
                description=options["description"].strip(),
                role=options["role"].strip(),
                environment=options["environment"].strip(),
                location=options["location"].strip(),
                platform_identity=options["platform_identity"].strip(),
            )
        except IntegrityError as exc:
            raise CommandError("A monitored system with that name already exists.") from exc

        self.stdout.write(str(system.id))
