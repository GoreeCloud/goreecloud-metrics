from django.urls import path

from . import views

urlpatterns = [
    path("livez/", views.livez, name="livez"),
    path("readyz/", views.readyz, name="readyz"),
    path("api/v1/status/", views.service_status, name="service-status"),
]
