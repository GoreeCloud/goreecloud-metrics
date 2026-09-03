"""Fail-closed agent enrollment and credential lifecycle primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AgentCredential, AgentEnrollment, AgentIdentity, MonitoredSystem

_MAX_ENROLLMENT_TTL = timedelta(hours=24)
_DEFAULT_ENROLLMENT_TTL = timedelta(minutes=15)


class EnrollmentError(RuntimeError):
    """Raised when an enrollment operation cannot safely proceed."""


@dataclass(frozen=True)
class IssuedEnrollment:
    enrollment_id: uuid.UUID
    secret: str
    expires_at: datetime


@dataclass(frozen=True)
class EnrolledAgent:
    agent_id: uuid.UUID
    credential_id: uuid.UUID
    credential_secret: str


def _validate_ttl(ttl: timedelta) -> None:
    if ttl <= timedelta(0) or ttl > _MAX_ENROLLMENT_TTL:
        raise EnrollmentError("Enrollment lifetime must be greater than zero and at most 24 hours.")


def _new_secret() -> str:
    return secrets.token_urlsafe(32)


@transaction.atomic
def issue_agent_enrollment(
    system: MonitoredSystem,
    *,
    ttl: timedelta = _DEFAULT_ENROLLMENT_TTL,
) -> IssuedEnrollment:
    """Issue one bounded one-time secret, returning plaintext only to the caller."""

    _validate_ttl(ttl)
    locked_system = MonitoredSystem.objects.select_for_update().get(pk=system.pk)
    if AgentIdentity.objects.filter(system=locked_system).exists():
        raise EnrollmentError("System already has an agent identity.")

    now = timezone.now()
    AgentEnrollment.objects.filter(
        system=locked_system,
        used_at__isnull=True,
        revoked_at__isnull=True,
    ).update(revoked_at=now)

    secret = _new_secret()
    enrollment = AgentEnrollment.objects.create(
        system=locked_system,
        secret_hash=make_password(secret),
        expires_at=now + ttl,
    )
    return IssuedEnrollment(
        enrollment_id=enrollment.id,
        secret=secret,
        expires_at=enrollment.expires_at,
    )


@transaction.atomic
def consume_agent_enrollment(
    enrollment_id: uuid.UUID | str,
    secret: str,
    *,
    agent_version: str,
) -> EnrolledAgent:
    """Consume a one-time enrollment and issue the first hashed agent credential."""

    if not isinstance(agent_version, str):
        raise EnrollmentError("Enrollment could not be completed.")
    version = agent_version.strip()
    if not version or len(version) > 64:
        raise EnrollmentError("Enrollment could not be completed.")
    if not isinstance(secret, str) or not secret or len(secret) > 256:
        raise EnrollmentError("Enrollment could not be completed.")

    try:
        enrollment = (
            AgentEnrollment.objects.select_for_update()
            .select_related("system")
            .get(pk=enrollment_id)
        )
    except (AgentEnrollment.DoesNotExist, ValidationError, ValueError, TypeError):
        raise EnrollmentError("Enrollment could not be completed.") from None

    locked_system = MonitoredSystem.objects.select_for_update().get(pk=enrollment.system_id)

    now = timezone.now()
    invalid = (
        enrollment.used_at is not None
        or enrollment.revoked_at is not None
        or enrollment.expires_at <= now
        or not check_password(secret, enrollment.secret_hash)
    )
    if invalid:
        raise EnrollmentError("Enrollment could not be completed.")

    if AgentIdentity.objects.filter(system=locked_system).exists():
        raise EnrollmentError("Enrollment could not be completed.")

    agent = AgentIdentity.objects.create(system=locked_system, version=version)
    credential_secret = _new_secret()
    credential = AgentCredential.objects.create(
        agent=agent,
        secret_hash=make_password(credential_secret),
    )
    enrollment.used_at = now
    enrollment.save(update_fields=("used_at",))

    return EnrolledAgent(
        agent_id=agent.id,
        credential_id=credential.id,
        credential_secret=credential_secret,
    )


@transaction.atomic
def revoke_agent(agent_id: uuid.UUID | str) -> None:
    """Revoke an agent and every active credential without deleting history."""

    try:
        agent = AgentIdentity.objects.select_for_update().get(pk=agent_id)
    except (AgentIdentity.DoesNotExist, ValidationError, ValueError, TypeError):
        raise EnrollmentError("Agent could not be revoked.") from None

    now = timezone.now()
    if agent.revoked_at is None:
        agent.state = AgentIdentity.State.REVOKED
        agent.revoked_at = now
        agent.save(update_fields=("state", "revoked_at"))

    AgentCredential.objects.filter(agent=agent, revoked_at__isnull=True).update(revoked_at=now)
    AgentEnrollment.objects.filter(
        system=agent.system,
        used_at__isnull=True,
        revoked_at__isnull=True,
    ).update(revoked_at=now)
