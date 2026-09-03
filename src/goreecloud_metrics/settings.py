"""Django settings for the GoreeCloud Metrics development foundation."""

from pathlib import Path

from .config import load_runtime_config

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG = load_runtime_config(BASE_DIR)

SECRET_KEY = CONFIG.secret_key
DEBUG = CONFIG.debug
ALLOWED_HOSTS = list(CONFIG.allowed_hosts)

INSTALLED_APPS = [
    "metrics.apps.MetricsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "goreecloud_metrics.urls"

TEMPLATES = []

WSGI_APPLICATION = "goreecloud_metrics.wsgi.application"
ASGI_APPLICATION = "goreecloud_metrics.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": CONFIG.sqlite_path,
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Bound request memory before endpoint-specific limits are applied.
DATA_UPLOAD_MAX_MEMORY_SIZE = 64 * 1024

# Baseline HTTP hardening. These are project-level controls only and do not constitute
# Wardveil Security conformance or a production-readiness claim.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

if CONFIG.production:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
