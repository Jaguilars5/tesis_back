import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ─── Rutas ───────────────────────────────────────────────────────────────────
# Construye rutas dentro del proyecto como esta: BASE_DIR / 'subdir'.
# config/settings/base.py -> padre = settings/ -> padre = config/ -> padre = raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Hacer que el directorio 'apps' sea importable como raíz de paquete
sys.path.insert(0, str(BASE_DIR / "apps"))

from apps.institutions import INSTITUTIONS_APPS
from apps.attendance import ATTENDANCE_APPS
from apps.behavior import BEHAVIOR_APPS
from apps.grading import GRADING_APPS
from apps.academic import ACADEMIC_APPS
from apps.analytics import ANALYTICS_APPS

# ─── Carga de .env ───────────────────────────────────────────────────────────
load_dotenv(BASE_DIR / ".env")

# ─── Core Django ─────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("SECRET_KEY environment variable is required")

# ─── Aplicaciones ────────────────────────────────────────────────────────────
DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.core",
    "apps.iam",
    *ACADEMIC_APPS,
    *GRADING_APPS,
    *INSTITUTIONS_APPS,
    "apps.students",
    "apps.analytics",
    *ANALYTICS_APPS,
    *ATTENDANCE_APPS,
    "apps.people",
    *BEHAVIOR_APPS,
    "apps.integration",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Autenticación ───────────────────────────────────────────────────────────
AUTH_USER_MODEL = "iam.User"

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ─── Validación de contraseñas ────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internacionalización ─────────────────────────────────────────────────────
LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

# ─── Archivos estáticos ───────────────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─── REST Framework ───────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "apps.core.api.pagination.StandardResultsSetPagination",
    "DEFAULT_RENDERER_CLASSES": (
        "apps.core.api.renderers.StandardResponseRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "apps.core.api.filters.RoleBasedFilterBackend",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "10/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "apps.core.api.schema.StandardResponseAutoSchema",
    "EXCEPTION_HANDLER": "apps.core.api.exceptions.custom_exception_handler",
}

# ─── DRF Spectacular (OpenAPI) ───────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Sistema de Gestion Academica API",
    "DESCRIPTION": """
API RESTful para la gestion academica de instituciones educativas.

## Autenticacion
Todos los endpoints (excepto login y refresh) requieren:
```
Authorization: Bearer <access_token>
```

## Formato de Respuesta
Todas las respuestas siguen el formato:
```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

## Codigos de Error
- 401: No autenticado
- 403: Sin permiso
- 404: No encontrado
- 422: Error de validacion
- 429: Rate limit excedido
""",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {
            "name": "iam",
            "description": "Usuarios, autenticacion, roles y permisos",
        },
        {
            "name": "institutions",
            "description": "Instituciones, años escolares, niveles, grados y secciones",
        },
        {
            "name": "academic",
            "description": "Materias, periodos academicos, oferta academica y proyectos interdisciplinarios",
        },
        {"name": "students", "description": "Estudiantes, representantes y matriculas"},
        {"name": "grading", "description": "Calificaciones, bloques, componentes, indicadores y actividades evaluativas"},
        {"name": "analytics", "description": "An\u00e1lisis de riesgo estudiantil y alertas tempranas"},
        {"name": "attendance", "description": "Asistencia, estados de asistencia y tipos de ausencia"},
        {"name": "behavior", "description": "Incidentes de conducta, habilidades socioemocionales y evaluaciones de comportamiento"},
        {"name": "configuration", "description": "Configuracion del sistema"},
        {"name": "integration", "description": "Sincronizacion con sistemas externos"},
        {"name": "people", "description": "Personas y tipos de documento"},
    ],
}

# ─── JWT (Compatibilidad y SimpleJWT) ─────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", 15))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", 7))

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=JWT_REFRESH_EXPIRE_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": JWT_SECRET,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}


# ─── CSRF ─────────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:3000").split(
    ","
)

# ─── Socket.IO ───────────────────────────────────────────────────────────────
SOCKETIO_REDIS_URL = os.getenv(
    "SOCKETIO_REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# ─── Celery ──────────────────────────────────────────────────────────────────
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "process-pending-sync-items": {
        "task": "apps.integration.tasks.sync_tasks.process_pending_sync_batch",
        "schedule": 300.0,
        "description": "Procesa items pendientes de SyncQueue cada 5 minutos",
    },
}
