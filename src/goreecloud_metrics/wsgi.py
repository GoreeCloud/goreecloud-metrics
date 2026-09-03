"""WSGI entry point for GoreeCloud Metrics."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goreecloud_metrics.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
