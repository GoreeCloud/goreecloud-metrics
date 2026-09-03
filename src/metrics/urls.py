from django.urls import path

from . import views

urlpatterns = [
    path("livez/", views.livez, name="livez"),
    path("readyz/", views.readyz, name="readyz"),
    path("api/v1/status/", views.service_status, name="service-status"),
    path("api/v1/agents/enroll/", views.agent_enroll, name="agent-enroll"),
    path("api/v1/agents/telemetry/", views.agent_telemetry, name="agent-telemetry"),
]
