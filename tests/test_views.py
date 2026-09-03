from django.test import TestCase
from django.urls import reverse


class HealthEndpointTests(TestCase):
    def test_liveness_is_bounded(self):
        response = self.client.get(reverse("livez"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "alive"})

    def test_readiness_checks_database(self):
        response = self.client.get(reverse("readyz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready"})

    def test_status_exposes_only_bounded_source_identity(self):
        response = self.client.get(reverse("service-status"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["service"], "goreecloud-metrics")
        self.assertEqual(payload["product"], "GoreeCloud Metrics")
        self.assertEqual(payload["lifecycle"], "development")
        self.assertEqual(payload["api_version"], "v1")
        self.assertTrue(payload["version"].startswith("0.1.0-dev."))
        self.assertNotIn("database", payload)
        self.assertNotIn("secret", payload)

    def test_baseline_security_headers_are_enforced(self):
        response = self.client.get(reverse("livez"))
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["Referrer-Policy"], "same-origin")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
