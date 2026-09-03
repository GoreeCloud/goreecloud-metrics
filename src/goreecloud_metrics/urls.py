"""URL configuration for GoreeCloud Metrics."""

from django.urls import include, path

urlpatterns = [
    path("", include("metrics.urls")),
]
