# Generated for GoreeCloud Metrics 0.1.0-dev.2.

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("metrics", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelemetrySnapshot",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sample_id", models.UUIDField(unique=True)),
                ("schema_version", models.PositiveSmallIntegerField(default=1)),
                ("sampled_at", models.DateTimeField()),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("agent_version", models.CharField(max_length=64)),
                ("logical_processors", models.PositiveSmallIntegerField()),
                ("load_1", models.FloatField()),
                ("load_5", models.FloatField()),
                ("load_15", models.FloatField()),
                ("cpu_user_ticks", models.PositiveBigIntegerField()),
                ("cpu_nice_ticks", models.PositiveBigIntegerField()),
                ("cpu_system_ticks", models.PositiveBigIntegerField()),
                ("cpu_idle_ticks", models.PositiveBigIntegerField()),
                ("cpu_iowait_ticks", models.PositiveBigIntegerField()),
                ("cpu_irq_ticks", models.PositiveBigIntegerField()),
                ("cpu_softirq_ticks", models.PositiveBigIntegerField()),
                ("cpu_steal_ticks", models.PositiveBigIntegerField()),
                ("memory_total_bytes", models.PositiveBigIntegerField()),
                ("memory_available_bytes", models.PositiveBigIntegerField()),
                ("swap_total_bytes", models.PositiveBigIntegerField()),
                ("swap_free_bytes", models.PositiveBigIntegerField()),
                ("root_filesystem_total_bytes", models.PositiveBigIntegerField()),
                ("root_filesystem_available_bytes", models.PositiveBigIntegerField()),
                ("network_rx_bytes", models.PositiveBigIntegerField()),
                ("network_tx_bytes", models.PositiveBigIntegerField()),
                ("agent", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="telemetry_snapshots", to="metrics.agentidentity")),
            ],
            options={"ordering": ("-sampled_at",)},
        ),
        migrations.AddIndex(
            model_name="telemetrysnapshot",
            index=models.Index(fields=["agent", "-sampled_at"], name="metrics_agent_sample_idx"),
        ),
    ]
