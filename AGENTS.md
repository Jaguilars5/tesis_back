# AGENTS.md — Backend: Sistema de Gestión Académica

## Developer Commands

```bash
# Local dev (requires venv + PostgreSQL + Redis)
# Default settings module: config.settings.local
python manage.py runserver                # Dev server on :8000
celery -A config worker --loglevel=info   # Celery worker (separate terminal)
celery -A config flower --port=5555       # Celery monitor (optional)

# Docker (recommended)
docker-compose build
docker-compose up
docker-compose exec web python manage.py createsuperuser
bash scripts/verify_docker_setup.sh       # Verify Docker setup

# Database
python manage.py migrate
python manage.py makemigrations <app_name>

# Seeds (idempotentes, orden sugerido)
python manage.py seed_catalogs        # Catálogos del sistema (tipos de documento, etc.)
python manage.py seed_permissions     # Permisos + Roles (DOCENTE, ESTUDIANTE, etc.)
python manage.py seed_test_data       # Datos de prueba

# Tests (Django test runner, NOT pytest)
# Test settings use SQLite (not PostgreSQL), in-memory cache, eager Celery, MD5 hasher
python manage.py test --settings=config.settings.test                     # All tests
python manage.py test apps.iam --settings=config.settings.test            # Single app
python manage.py test apps.grading.tests.test_models --settings=config.settings.test  # Single file

# Coverage
coverage run --source='.' manage.py test --settings=config.settings.test
coverage report -m
```

## Architecture

**Layered pattern per app**: `models/` → `repositories/` → `services/` → `api/` (serializers, views, urls).

- `config/settings/` — split config: `base.py`, `local.py`, `production.py`, `test.py`. Default: `config.settings.local`
- `apps/core/` — shared utilities: `StandardResponseRenderer`, `custom_exception_handler`, `StandardResultsSetPagination`, `ok_response()` / `error_response()`
- `AUTH_USER_MODEL = "iam.User"` — Custom user model in iam app
- `sys.path` inserts `apps/` as root package in `config/settings/base.py`

**Apps** (12 apps): `core`, `iam`, `people`, `institutions`, `students`, `academic`, `grading`, `attendance`, `behavior`, `analytics`, `configuration`, `integration`

**API routes** (see `config/urls.py`):
- `/api/accounts/` → `apps.iam.urls` (compatibilidad)
- `/api/academic/`, `/api/institutions/`, `/api/grading/`, `/api/students/`, `/api/analytics/`, `/api/attendance/`, `/api/behavior/`, `/api/configuration/`, `/api/integration/`

**API Documentation** (pública, sin auth):
- `/api/schema/` — Schema OpenAPI 3.0
- `/api/docs/` — Swagger UI
- `/api/redoc/` — ReDoc

## Convenciones de Vistas

- **ViewSets**: TODOS los módulos usan ViewSets (NO funciones @api_view)
- **URLs**: RESTful con router.register, no funciones sueltas
- **Permisos**: action_permissions dict en cada ViewSet
- **Paginación**: StandardResultsSetPagination
- **Respuestas**: ok_response/error_response de apps.core.utils, o el renderer global StandardResponseRenderer

## API Contract

All responses use format: `{"ok": bool, "data": ..., "msg": "..."}` via `apps.core.renderers.StandardResponseRenderer`.

- Default permission: `IsAuthenticated` (all endpoints require auth unless overridden)
- Auth: JWT Bearer tokens via `djangorestframework-simplejwt`
- Pagination: `StandardResultsSetPagination` (metadata inside `data`)
- Frontend expected at `localhost:3000` (CORS config)

## Critical Conventions

- **NO `Model.objects.query()` in views or services** — all ORM queries must live in `repositories/` layer
- Use `ok_response(data)` and `error_response(msg)` from `apps.core.utils` for responses
- Model names use `Camel_Case` (historical convention); methods/variables use `snake_case`
- `.env` loaded via `python-dotenv` in `config/settings/base.py` — copy `.env.example` to `.env` for local setup
- `db.sqlite3` is gitignored and only used for local fallback — production/Docker uses PostgreSQL
- Analytics app uses `numpy`, `pandas`, `scikit-learn`, `joblib` for risk analysis
- **NO central `catalogs/` app** — each domain app manages its own catalogs

## Test Setup

- Uses Django `TestCase` + DRF `APIClient` — **not pytest**
- No `conftest.py`, no `pytest.ini`, no linter/formatter config
- Tests use `force_authenticate(user=...)` for auth, not JWT tokens
- Test fixtures created manually in `setUp()` — no factory library
- **Must use `--settings=config.settings.test`** — swaps PostgreSQL for SQLite, Celery for eager execution, Redis cache for locmem
- Test DB file: `test_db.sqlite3` (gitignored)

## Docker Services

| Service | Port | Notes |
|---------|------|-------|
| web | 8000 | `WAIT_FOR_DB=true`, `RUN_MIGRATIONS=true` auto-run migrations |
| db | 5432 | PostgreSQL 15 |
| redis | 6379 | Celery broker + Django cache |
| celery | — | Worker: `celery -A config worker` |
| flower | 5555 | Celery monitoring UI |

Entrypoint (`scripts/entrypoint.sh`) waits for DB and runs migrations based on env vars.

## Seguridad

### Headers de Producción
- HTTPS forzado con HSTS (1 año)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()

### Rate Limiting
- Anónimos: 100 requests/día
- Autenticados: 1000 requests/día
- Login: 10 intentos/hora

### JWT
- Access token: 15 minutos (configurable via JWT_ACCESS_EXPIRE_MINUTES)
- Refresh token: 7 días (configurable via JWT_REFRESH_EXPIRE_DAYS)
- Rotación de refresh tokens activada

### Passwords
- Longitud mínima: 12 caracteres
- Validadores: similitud, longitud, comunes, numéricos

### Middleware de Seguridad
- `apps.core.middleware.SecurityHeadersMiddleware` — Agrega headers de seguridad a todas las respuestas

## API Documentation (OpenAPI)

- Schema JSON: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`

drf-spectacular genera schema OpenAPI 3.0 automáticamente desde los ViewSets.

```bash
# Validar schema
python manage.py spectacular --settings=config.settings.local --validate

# Generar archivo
python manage.py spectacular --settings=config.settings.local --file schema.yml
```

## Key Files

| Path | Purpose |
|------|---------|
| `config/settings/base.py` | All shared settings, JWT config, REST_FRAMEWORK defaults |
| `config/settings/test.py` | Test overrides: SQLite, eager Celery, MD5 hasher |
| `config/urls.py` | Root URL routing to all apps |
| `config/celery.py` | Celery app setup, auto-discovers tasks from all apps |
| `apps/core/utils/responses.py` | `ok_response()`, `error_response()` helpers |
| `apps/core/exceptions.py` | Global exception handler enforcing response format |
| `apps/core/permissions.py` | `HasPermission` (DRF ViewSet permission) |
| `apps/core/schema.py` | `StandardResponseAutoSchema` para drf-spectacular |
| `apps/core/constants/permissions.py` | Constantes tipadas de permisos para todos los módulos |

## Permisos DRF

- `apps/core/permissions.py` — `HasPermission` (para ViewSets)
- Los ViewSets deben definir `action_permissions = {"list": "codename", ...}`
- Superusuarios bypassan todas las verificaciones de permisos
- Formato de permisos: `<modulo>.<accion>` (ej: `grading.create_note`)

### Módulos de Permisos Disponibles

```python
from apps.core.constants.permissions import (
    iam, people, institutions, academic, students,
    grading, analytics, attendance, behavior,
    configuration, integration,
)

# Ejemplos:
iam.VIEW_USER         # "iam.view_user"
people.VIEW_PERSON    # "people.view_person"
behavior.VIEW_CONDUCT_INCIDENT  # "behavior.view_conduct_incident"
```

## Management Commands

- `python manage.py seed_catalogs` — Crea todos los catálogos del sistema (idempotente)
- `python manage.py seed_permissions` — Crea todos los permisos + roles del sistema (idempotente)
- `python manage.py seed_test_data` — Crea datos de prueba para desarrollo

## Tests de Seguridad

- `apps/core/tests/test_permission_integration.py` — Tests de auth + permisos por módulo
- `apps/core/tests/test_throttling.py` — Tests de rate limiting
- `apps/core/tests/test_security_headers.py` — Tests de headers de seguridad
- `apps/core/tests/test_password_validation.py` — Tests de validación de contraseñas
- `apps/core/tests/test_jwt_config.py` — Tests de configuración JWT

### Ejecutar tests de seguridad
```bash
python manage.py test apps.core.tests --settings=config.settings.test
```

## Permisos por Módulo

Todos los endpoints requieren autenticación JWT + permiso específico excepto:
- `POST /api/accounts/login/` — Público
- `POST /api/accounts/refresh/` — Público (requiere refresh token válido)

### Formato de permisos
`<modulo>.<accion>` donde acción es: `view`, `create`, `update`, `delete`
