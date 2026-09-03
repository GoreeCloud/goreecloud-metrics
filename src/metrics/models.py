"""Core GoreeCloud Metrics system, agent, and telemetry records."""

from __future__ import annotations

import uuid

from django.db import models


class MonitoredSystem(models.Model):
    """Durable Metrics-owned identity for one authorized monitored system."""

    class MonitoringState(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        RETIRED = "retired", "Retired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=64, blank=True)
    environment = models.CharField(max_length=64, blank=True)
    location = models.CharField(max_length=120, blank=True)
    platform_identity = models.CharField(max_length=255, blank=True)
    monitoring_state = models.CharField(
        max_length=16,
        choices=MonitoringState.choices,
        default=MonitoringState.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class AgentIdentity(models.Model):
    """Metrics-local identity record for the agent assigned to a system."""

    class State(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    system = models.OneToOneField(
        MonitoredSystem,
        on_delete=models.PROTECT,
        related_name="agent",
    )
    version = models.CharField(max_length=64)
    state = models.CharField(max_length=16, choices=State.choices, default=State.ACTIVE)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.system.name} agent"


class AgentEnrollment(models.Model):
    """One-time enrollment record; the reusable plaintext secret is never persisted."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    system = models.ForeignKey(
        MonitoredSystem,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    secret_hash = models.CharField(max_length=256)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class AgentCredential(models.Model):
    """Hashed agent credential metadata supporting rotation and revocation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        AgentIdentity,
        on_delete=models.PROTECT,
        related_name="credentials",
    )
    secret_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class TelemetrySnapshot(models.Model):
    """One bounded host resource sample accepted from an authenticated Metrics Agent."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample_id = models.UUIDField(unique=True)
    agent = models.ForeignKey(
        AgentIdentity,
        on_delete=models.PROTECT,
        related_name="telemetry_snapshots",
    )
    schema_version = models.PositiveSmallIntegerField(default=1)
    sampled_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    agent_version = models.CharField(max_length=64)

    logical_processors = models.PositiveSmallIntegerField()
    load_1 = models.FloatField()
    load_5 = models.FloatField()
    load_15 = models.FloatField()
    cpu_user_ticks = models.PositiveBigIntegerField()
    cpu_nice_ticks = models.PositiveBigIntegerField()
    cpu_system_ticks = models.PositiveBigIntegerField()
    cpu_idle_ticks = models.PositiveBigIntegerField()
    cpu_iowait_ticks = models.PositiveBigIntegerField()
    cpu_irq_ticks = models.PositiveBigIntegerField()
    cpu_softirq_ticks = models.PositiveBigIntegerField()
    cpu_steal_ticks = models.PositiveBigIntegerField()

    memory_total_bytes = models.PositiveBigIntegerField()
    memory_available_bytes = models.PositiveBigIntegerField()
    swap_total_bytes = models.PositiveBigIntegerField()
    swap_free_bytes = models.PositiveBigIntegerField()

    root_filesystem_total_bytes = models.PositiveBigIntegerField()
    root_filesystem_available_bytes = models.PositiveBigIntegerField()

    network_rx_bytes = models.PositiveBigIntegerField()
    network_tx_bytes = models.PositiveBigIntegerField()

    class Meta:
        ordering = ("-sampled_at",)
        indexes = [
            models.Index(fields=("agent", "-sampled_at"), name="metrics_agent_sample_idx"),
        ]
