from pathlib import Path
import os
from unittest import TestCase
from unittest.mock import patch

from goreecloud_metrics.config import ConfigurationError, load_runtime_config


class RuntimeConfigTests(TestCase):
    def test_environment_must_be_explicit(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                load_runtime_config(Path("/tmp/metrics"))

    def test_secret_must_be_explicit(self):
        with patch.dict(os.environ, {"METRICS_ENV": "development"}, clear=True):
            with self.assertRaises(ConfigurationError):
                load_runtime_config(Path("/tmp/metrics"))

    def test_production_requires_allowed_hosts(self):
        environment = {
            "METRICS_ENV": "production",
            "METRICS_SECRET_KEY": "x" * 64,
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(ConfigurationError):
                load_runtime_config(Path("/tmp/metrics"))

    def test_relative_database_path_is_anchored_to_repository_base(self):
        environment = {
            "METRICS_ENV": "test",
            "METRICS_SECRET_KEY": "test-only-key",
            "METRICS_SQLITE_PATH": "test.sqlite3",
        }
        with patch.dict(os.environ, environment, clear=True):
            config = load_runtime_config(Path("/tmp/metrics"))
        self.assertEqual(config.sqlite_path, Path("/tmp/metrics/test.sqlite3"))

    def test_telemetry_retention_defaults_to_seven_days(self):
        environment = {
            "METRICS_ENV": "test",
            "METRICS_SECRET_KEY": "test-only-key",
        }
        with patch.dict(os.environ, environment, clear=True):
            config = load_runtime_config(Path("/tmp/metrics"))
        self.assertEqual(config.telemetry_retention_hours, 168)

    def test_telemetry_retention_is_bounded(self):
        for value in ("0", "2161", "not-a-number"):
            with self.subTest(value=value):
                environment = {
                    "METRICS_ENV": "test",
                    "METRICS_SECRET_KEY": "test-only-key",
                    "METRICS_TELEMETRY_RETENTION_HOURS": value,
                }
                with patch.dict(os.environ, environment, clear=True):
                    with self.assertRaises(ConfigurationError):
                        load_runtime_config(Path("/tmp/metrics"))
