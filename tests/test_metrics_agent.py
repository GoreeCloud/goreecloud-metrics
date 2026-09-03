import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from metrics_agent.client import ClientError, validate_server_url
from metrics_agent.collectors import collect_snapshot
from metrics_agent.state import AgentState, StateError, load_state, save_state


class AgentStateTests(SimpleTestCase):
    def test_state_is_written_with_owner_only_permissions(self):
        with self.subTest("round-trip"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as directory:
                path = Path(directory) / "state.json"
                state = AgentState(
                    server_url="https://metrics.example.test",
                    agent_id="7f274ee5-50d8-43db-8a08-87e25220533f",
                    credential_id="6fce9fd7-447d-4cb7-9c65-f3f5ec7e563d",
                    credential_secret="development-agent-secret",
                )
                save_state(path, state)
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(load_state(path), state)

    def test_state_with_group_or_other_access_fails_closed(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = AgentState(
                server_url="https://metrics.example.test",
                agent_id="7f274ee5-50d8-43db-8a08-87e25220533f",
                credential_id="6fce9fd7-447d-4cb7-9c65-f3f5ec7e563d",
                credential_secret="development-agent-secret",
            )
            save_state(path, state)
            os.chmod(path, 0o640)
            with self.assertRaisesRegex(StateError, "permissions are too broad"):
                load_state(path)


class AgentTransportTests(SimpleTestCase):
    def test_non_loopback_http_is_rejected(self):
        with self.assertRaisesRegex(ClientError, "HTTPS is required"):
            validate_server_url("http://metrics.example.test")

    def test_loopback_http_is_allowed_for_development(self):
        self.assertEqual(validate_server_url("http://127.0.0.1:8000/"), "http://127.0.0.1:8000")

    def test_https_is_allowed(self):
        self.assertEqual(
            validate_server_url("https://metrics.example.test"),
            "https://metrics.example.test",
        )

    def test_server_url_rejects_embedded_credentials(self):
        with self.assertRaises(ClientError):
            validate_server_url("https://user:password@metrics.example.test")


class LinuxCollectorTests(SimpleTestCase):
    def test_core_snapshot_is_bounded_and_excludes_identifying_private_fields(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            proc_root = Path(directory)
            (proc_root / "net").mkdir()
            (proc_root / "stat").write_text(
                "cpu 100 1 50 1000 5 2 3 0 0 0\n",
                encoding="utf-8",
            )
            (proc_root / "meminfo").write_text(
                "MemTotal: 8000 kB\n"
                "MemAvailable: 4000 kB\n"
                "SwapTotal: 2000 kB\n"
                "SwapFree: 1500 kB\n",
                encoding="utf-8",
            )
            (proc_root / "net" / "dev").write_text(
                "Inter-| Receive | Transmit\n"
                " face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed\n"
                "    lo: 100 0 0 0 0 0 0 0 200 0 0 0 0 0 0 0\n"
                "  eth0: 1000 0 0 0 0 0 0 0 2000 0 0 0 0 0 0 0\n",
                encoding="utf-8",
            )
            statvfs = SimpleNamespace(f_blocks=100, f_bavail=60, f_frsize=4096)
            with (
                patch("metrics_agent.collectors.os.getloadavg", return_value=(0.5, 0.25, 0.1)),
                patch("metrics_agent.collectors.os.cpu_count", return_value=4),
                patch("metrics_agent.collectors.os.statvfs", return_value=statvfs),
                patch("metrics_agent.collectors.current_version", return_value="0.1.0-dev.2"),
            ):
                snapshot = collect_snapshot(proc_root=proc_root)

        self.assertEqual(
            set(snapshot),
            {
                "schema_version",
                "sample_id",
                "sampled_at",
                "agent_version",
                "cpu",
                "memory",
                "filesystem",
                "network",
            },
        )
        self.assertEqual(snapshot["network"], {"rx_bytes": 1000, "tx_bytes": 2000})
        self.assertEqual(snapshot["filesystem"]["mount"], "/")
        serialized_keys = repr(snapshot).lower()
        for forbidden in (
            "hostname",
            "ip_address",
            "serial",
            "process",
            "environment",
            "command",
            "username",
            "log",
        ):
            self.assertNotIn(forbidden, serialized_keys)
