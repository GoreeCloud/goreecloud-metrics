import json
from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from metrics.enrollment import issue_agent_enrollment, revoke_agent
from metrics.models import AgentCredential, AgentIdentity, MonitoredSystem, TelemetrySnapshot


def telemetry_payload(*, sample_id="38e38ea8-cc62-46fb-a4a8-776eefed9e43", agent_version="0.1.0-dev.2"):
    return {
        "schema_version": 1,
        "sample_id": sample_id,
        "sampled_at": timezone.now().isoformat(),
        "agent_version": agent_version,
        "cpu": {
            "logical_processors": 4,
            "load_1": 0.5,
            "load_5": 0.25,
            "load_15": 0.1,
            "user_ticks": 100,
            "nice_ticks": 1,
            "system_ticks": 50,
            "idle_ticks": 1000,
            "iowait_ticks": 5,
            "irq_ticks": 2,
            "softirq_ticks": 3,
            "steal_ticks": 0,
        },
        "memory": {
            "total_bytes": 8_000,
            "available_bytes": 4_000,
            "swap_total_bytes": 2_000,
            "swap_free_bytes": 1_500,
        },
        "filesystem": {
            "mount": "/",
            "total_bytes": 100_000,
            "available_bytes": 60_000,
        },
        "network": {"rx_bytes": 1_000, "tx_bytes": 2_000},
    }


class AgentProtocolTests(TestCase):
    def setUp(self):
        self.system = MonitoredSystem.objects.create(name="api-test-host")
        self.issued = issue_agent_enrollment(self.system)

    def _enroll(self):
        response = self.client.post(
            reverse("agent-enroll"),
            data=json.dumps(
                {
                    "enrollment_id": str(self.issued.enrollment_id),
                    "enrollment_secret": self.issued.secret,
                    "agent_version": "0.1.0-dev.2",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def _telemetry_headers(self, enrolled):
        return {
            "HTTP_AUTHORIZATION": f"Bearer {enrolled['credential_secret']}",
            "HTTP_X_GOREECLOUD_METRICS_CREDENTIAL_ID": enrolled["credential_id"],
        }

    def test_network_enrollment_consumes_one_time_secret(self):
        payload = self._enroll()
        self.assertEqual(set(payload), {"agent_id", "credential_id", "credential_secret"})
        self.assertEqual(
            self.client.post(
                reverse("agent-enroll"),
                data=json.dumps(
                    {
                        "enrollment_id": str(self.issued.enrollment_id),
                        "enrollment_secret": self.issued.secret,
                        "agent_version": "0.1.0-dev.2",
                    }
                ),
                content_type="application/json",
            ).status_code,
            400,
        )
        self.assertEqual(AgentIdentity.objects.count(), 1)
        self.assertEqual(AgentCredential.objects.count(), 1)

    def test_enrollment_response_is_not_cacheable(self):
        response = self.client.post(
            reverse("agent-enroll"),
            data=json.dumps(
                {
                    "enrollment_id": str(self.issued.enrollment_id),
                    "enrollment_secret": self.issued.secret,
                    "agent_version": "0.1.0-dev.2",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_enrollment_rejects_unexpected_fields_and_oversized_body(self):
        bad = {
            "enrollment_id": str(self.issued.enrollment_id),
            "enrollment_secret": self.issued.secret,
            "agent_version": "0.1.0-dev.2",
            "extra": "not-allowed",
        }
        response = self.client.post(
            reverse("agent-enroll"),
            data=json.dumps(bad),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            reverse("agent-enroll"),
            data=b"{" + (b"x" * 9000),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_enrollment_rejects_non_string_secret_or_version_without_server_error(self):
        for secret, version in ((1234, "0.1.0-dev.2"), (self.issued.secret, 1234)):
            with self.subTest(secret=secret, version=version):
                response = self.client.post(
                    reverse("agent-enroll"),
                    data=json.dumps(
                        {
                            "enrollment_id": str(self.issued.enrollment_id),
                            "enrollment_secret": secret,
                            "agent_version": version,
                        }
                    ),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertFalse(AgentIdentity.objects.exists())

    @override_settings(CONFIG=SimpleNamespace(production=True))
    def test_production_enrollment_requires_secure_transport(self):
        response = self.client.post(
            reverse("agent-enroll"),
            data=json.dumps(
                {
                    "enrollment_id": str(self.issued.enrollment_id),
                    "enrollment_secret": self.issued.secret,
                    "agent_version": "0.1.0-dev.2",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(AgentIdentity.objects.exists())

    def test_authenticated_telemetry_is_persisted_and_activates_pending_system(self):
        enrolled = self._enroll()
        payload = telemetry_payload()
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(payload),
            content_type="application/json",
            **self._telemetry_headers(enrolled),
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {"status": "accepted", "sample_id": payload["sample_id"]})
        self.assertEqual(response.headers["Cache-Control"], "no-store")

        snapshot = TelemetrySnapshot.objects.get()
        agent = AgentIdentity.objects.get()
        credential = AgentCredential.objects.get()
        self.system.refresh_from_db()
        self.assertEqual(snapshot.agent, agent)
        self.assertEqual(snapshot.memory_total_bytes, 8_000)
        self.assertEqual(snapshot.root_filesystem_available_bytes, 60_000)
        self.assertIsNotNone(agent.last_seen_at)
        self.assertIsNotNone(credential.last_used_at)
        self.assertEqual(self.system.monitoring_state, MonitoredSystem.MonitoringState.ACTIVE)

    def test_invalid_agent_secret_fails_closed_without_writing_telemetry(self):
        enrolled = self._enroll()
        headers = self._telemetry_headers(enrolled)
        headers["HTTP_AUTHORIZATION"] = "Bearer wrong-secret"
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(telemetry_payload()),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TelemetrySnapshot.objects.exists())

    def test_missing_authentication_is_401(self):
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(telemetry_payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["WWW-Authenticate"], "Bearer")
        self.assertFalse(TelemetrySnapshot.objects.exists())

    def test_revoked_agent_cannot_submit(self):
        enrolled = self._enroll()
        revoke_agent(enrolled["agent_id"])
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(telemetry_payload()),
            content_type="application/json",
            **self._telemetry_headers(enrolled),
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TelemetrySnapshot.objects.exists())

    def test_paused_system_cannot_submit(self):
        enrolled = self._enroll()
        self.system.monitoring_state = MonitoredSystem.MonitoringState.PAUSED
        self.system.save(update_fields=("monitoring_state",))
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(telemetry_payload()),
            content_type="application/json",
            **self._telemetry_headers(enrolled),
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TelemetrySnapshot.objects.exists())

    def test_duplicate_sample_id_is_rejected_without_duplicate_storage(self):
        enrolled = self._enroll()
        payload = telemetry_payload()
        for expected in (202, 400):
            response = self.client.post(
                reverse("agent-telemetry"),
                data=json.dumps(payload),
                content_type="application/json",
                **self._telemetry_headers(enrolled),
            )
            self.assertEqual(response.status_code, expected)
        self.assertEqual(TelemetrySnapshot.objects.count(), 1)

    def test_telemetry_schema_is_strict_and_relationships_are_validated(self):
        enrolled = self._enroll()
        headers = self._telemetry_headers(enrolled)

        extra = telemetry_payload(sample_id="ed188103-e8d3-41d7-9b33-16d66364c90a")
        extra["hostname"] = "should-not-be-collected"
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(extra),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 400)

        invalid_memory = telemetry_payload(sample_id="ef83ec1a-323f-454a-96e8-76000130c3ec")
        invalid_memory["memory"]["available_bytes"] = invalid_memory["memory"]["total_bytes"] + 1
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(invalid_memory),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TelemetrySnapshot.objects.exists())

    def test_production_telemetry_requires_secure_transport(self):
        enrolled = self._enroll()
        with self.settings(CONFIG=SimpleNamespace(production=True)):
            response = self.client.post(
                reverse("agent-telemetry"),
                data=json.dumps(telemetry_payload()),
                content_type="application/json",
                **self._telemetry_headers(enrolled),
            )
        self.assertEqual(response.status_code, 401)
        self.assertFalse(TelemetrySnapshot.objects.exists())

    def test_ingestion_prunes_expired_telemetry(self):
        enrolled = self._enroll()
        agent = AgentIdentity.objects.get()
        old = TelemetrySnapshot.objects.create(
            agent=agent,
            sample_id="0fd337b2-0507-4f8f-a360-1c2b8b89b5d5",
            schema_version=1,
            sampled_at=timezone.now(),
            agent_version="0.1.0-dev.2",
            logical_processors=1,
            load_1=0,
            load_5=0,
            load_15=0,
            cpu_user_ticks=0,
            cpu_nice_ticks=0,
            cpu_system_ticks=0,
            cpu_idle_ticks=1,
            cpu_iowait_ticks=0,
            cpu_irq_ticks=0,
            cpu_softirq_ticks=0,
            cpu_steal_ticks=0,
            memory_total_bytes=1,
            memory_available_bytes=1,
            swap_total_bytes=0,
            swap_free_bytes=0,
            root_filesystem_total_bytes=1,
            root_filesystem_available_bytes=1,
            network_rx_bytes=0,
            network_tx_bytes=0,
        )
        cutoff_time = timezone.now() - timedelta(hours=169)
        TelemetrySnapshot.objects.filter(pk=old.pk).update(received_at=cutoff_time)
        fresh = telemetry_payload(sample_id="2a910887-2f71-4e83-915e-2b537df00114")
        response = self.client.post(
            reverse("agent-telemetry"),
            data=json.dumps(fresh),
            content_type="application/json",
            **self._telemetry_headers(enrolled),
        )
        self.assertEqual(response.status_code, 202)
        self.assertFalse(TelemetrySnapshot.objects.filter(pk=old.pk).exists())
        self.assertTrue(TelemetrySnapshot.objects.filter(sample_id=fresh["sample_id"]).exists())
