from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from metrics.enrollment import EnrollmentError, consume_agent_enrollment, revoke_agent


class EnrollmentInputValidationTests(TestCase):
    def test_malformed_enrollment_id_fails_closed(self):
        with self.assertRaisesRegex(EnrollmentError, "Enrollment could not be completed"):
            consume_agent_enrollment(
                "not-a-uuid",
                "irrelevant-secret",
                agent_version="0.1.0-dev.1",
            )

    def test_malformed_agent_id_fails_closed(self):
        with self.assertRaisesRegex(EnrollmentError, "Agent could not be revoked"):
            revoke_agent("not-a-uuid")

    def test_management_command_rejects_malformed_system_id(self):
        with self.assertRaisesRegex(CommandError, "Unknown monitored system"):
            call_command("issue_agent_enrollment", "not-a-uuid")
