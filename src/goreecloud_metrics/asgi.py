"""ASGI entry point for GoreeCloud Metrics."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goreecloud_metrics.settings")

from django.core.asgi import get_asgi_application

application = get_asgi_application()
