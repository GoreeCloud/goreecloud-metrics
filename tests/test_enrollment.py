from datetime import timedelta

from django.contrib.auth.hashers import check_password
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from metrics.enrollment import (
    EnrollmentError,
    consume_agent_enrollment,
    issue_agent_enrollment,
    revoke_agent,
)
from metrics.models import AgentCredential, AgentEnrollment, AgentIdentity, MonitoredSystem


class AgentEnrollmentTests(TestCase):
    def setUp(self):
        self.system = MonitoredSystem.objects.create(name="metrics-test-host")

    def test_issued_secret_is_not_persisted_in_plaintext(self):
        issued = issue_agent_enrollment(self.system)
        stored = AgentEnrollment.objects.get(pk=issued.enrollment_id)

        self.assertNotEqual(stored.secret_hash, issued.secret)
        self.assertNotIn(issued.secret, stored.secret_hash)
        self.assertTrue(check_password(issued.secret, stored.secret_hash))
        self.assertGreater(stored.expires_at, timezone.now())

    def test_new_issue_revokes_previous_unused_enrollment(self):
        first = issue_agent_enrollment(self.system)
        second = issue_agent_enrollment(self.system)

        first_record = AgentEnrollment.objects.get(pk=first.enrollment_id)
        second_record = AgentEnrollment.objects.get(pk=second.enrollment_id)
        self.assertIsNotNone(first_record.revoked_at)
        self.assertIsNone(second_record.revoked_at)

    def test_ttl_is_bounded(self):
        for ttl in (timedelta(0), timedelta(hours=24, seconds=1)):
            with self.subTest(ttl=ttl):
                with self.assertRaises(EnrollmentError):
                    issue_agent_enrollment(self.system, ttl=ttl)

    def test_wrong_secret_fails_closed(self):
        issued = issue_agent_enrollment(self.system)
        with self.assertRaisesRegex(EnrollmentError, "Enrollment could not be completed"):
            consume_agent_enrollment(
                issued.enrollment_id,
                "wrong-secret",
                agent_version="0.1.0-dev.1",
            )
        self.assertFalse(AgentIdentity.objects.exists())

    def test_expired_enrollment_fails_closed(self):
        issued = issue_agent_enrollment(self.system)
        AgentEnrollment.objects.filter(pk=issued.enrollment_id).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )

        with self.assertRaises(EnrollmentError):
            consume_agent_enrollment(
                issued.enrollment_id,
                issued.secret,
                agent_version="0.1.0-dev.1",
            )

    def test_revoked_enrollment_fails_closed(self):
        issued = issue_agent_enrollment(self.system)
        AgentEnrollment.objects.filter(pk=issued.enrollment_id).update(
            revoked_at=timezone.now()
        )

        with self.assertRaises(EnrollmentError):
            consume_agent_enrollment(
                issued.enrollment_id,
                issued.secret,
                agent_version="0.1.0-dev.1",
            )

    def test_successful_enrollment_creates_hashed_agent_credential_once(self):
        issued = issue_agent_enrollment(self.system)
        enrolled = consume_agent_enrollment(
            issued.enrollment_id,
            issued.secret,
            agent_version="0.1.0-dev.1",
        )

        agent = AgentIdentity.objects.get(pk=enrolled.agent_id)
        credential = AgentCredential.objects.get(pk=enrolled.credential_id)
        enrollment = AgentEnrollment.objects.get(pk=issued.enrollment_id)

        self.assertEqual(agent.system, self.system)
        self.assertEqual(agent.version, "0.1.0-dev.1")
        self.assertEqual(agent.state, AgentIdentity.State.ACTIVE)
        self.assertIsNotNone(enrollment.used_at)
        self.assertNotEqual(credential.secret_hash, enrolled.credential_secret)
        self.assertNotIn(enrolled.credential_secret, credential.secret_hash)
        self.assertTrue(check_password(enrolled.credential_secret, credential.secret_hash))

        with self.assertRaises(EnrollmentError):
            consume_agent_enrollment(
                issued.enrollment_id,
                issued.secret,
                agent_version="0.1.0-dev.1",
            )
        self.assertEqual(AgentIdentity.objects.count(), 1)
        self.assertEqual(AgentCredential.objects.count(), 1)

    def test_system_with_agent_cannot_receive_new_enrollment(self):
        issued = issue_agent_enrollment(self.system)
        consume_agent_enrollment(
            issued.enrollment_id,
            issued.secret,
            agent_version="0.1.0-dev.1",
        )

        with self.assertRaisesRegex(EnrollmentError, "already has an agent"):
            issue_agent_enrollment(self.system)

    def test_agent_revocation_keeps_history_and_revokes_credentials(self):
        issued = issue_agent_enrollment(self.system)
        enrolled = consume_agent_enrollment(
            issued.enrollment_id,
            issued.secret,
            agent_version="0.1.0-dev.1",
        )

        revoke_agent(enrolled.agent_id)

        agent = AgentIdentity.objects.get(pk=enrolled.agent_id)
        credential = AgentCredential.objects.get(pk=enrolled.credential_id)
        self.assertEqual(agent.state, AgentIdentity.State.REVOKED)
        self.assertIsNotNone(agent.revoked_at)
        self.assertIsNotNone(credential.revoked_at)
        self.assertEqual(AgentIdentity.objects.count(), 1)
        self.assertEqual(AgentCredential.objects.count(), 1)


class MonitoredSystemTests(TestCase):
    def test_system_names_are_unique(self):
        MonitoredSystem.objects.create(name="duplicate-host")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MonitoredSystem.objects.create(name="duplicate-host")
