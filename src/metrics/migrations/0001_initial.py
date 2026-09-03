# Generated for GoreeCloud Metrics 0.1.0-dev.1.

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MonitoredSystem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("role", models.CharField(blank=True, max_length=64)),
                ("environment", models.CharField(blank=True, max_length=64)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("platform_identity", models.CharField(blank=True, max_length=255)),
                ("monitoring_state", models.CharField(choices=[("pending", "Pending"), ("active", "Active"), ("paused", "Paused"), ("retired", "Retired")], default="pending", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="AgentIdentity",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("version", models.CharField(max_length=64)),
                ("state", models.CharField(choices=[("active", "Active"), ("revoked", "Revoked")], default="active", max_length=16)),
                ("last_seen_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("system", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="agent", to="metrics.monitoredsystem")),
            ],
        ),
        migrations.CreateModel(
            name="AgentEnrollment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("secret_hash", models.CharField(max_length=256)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("system", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="metrics.monitoredsystem")),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="AgentCredential",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("secret_hash", models.CharField(max_length=256)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("agent", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="credentials", to="metrics.agentidentity")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
