from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ─── Base de Datos ───────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ─── Caché y Broker de Celery ────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = "redis://localhost:6379/0"

# ─── Correo Electrónico ──────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─── Aplicaciones de Desarrollo ───────────────────────────────────────────────
INSTALLED_APPS += [
    # "debug_toolbar",
    # "django_extensions",
]

# ─── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True
