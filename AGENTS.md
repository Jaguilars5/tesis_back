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

# Tests (Django test runner, NOT pytest)
# Test settings use SQLite (not PostgreSQL), in-memory cache, eager Celery, MD5 hasher
python manage.py test --settings=config.settings.test                     # All tests
python manage.py test apps.accounts --settings=config.settings.test       # Single app
python manage.py test apps.accounts.tests.test_api --settings=config.settings.test  # Single file

# Coverage
coverage run --source='.' manage.py test --settings=config.settings.test
coverage report -m
```

## Architecture

**Layered pattern per app**: `models/` → `repositories/` → `services/` → `api/` (serializers, views, urls).

- `config/settings/` — split config: `base.py`, `local.py`, `production.py`, `test.py`. Default: `config.settings.local`
- `apps/core/` — shared utilities: `StandardResponseRenderer`, `custom_exception_handler`, `StandardResultsSetPagination`, `ok_response()` / `error_response()`
- `AUTH_USER_MODEL = "accounts.User"` — custom user model, not `auth.User`
- `sys.path` inserts `apps/` as root package in `config/settings/base.py`

**Apps** (8 total): `core`, `accounts`, `academic`, `grading`, `institutions`, `scheduling`, `students`, `analytics`

**API routes** (see `config/urls.py`): `/api/accounts/`, `/api/academic/`, `/api/institutions/`, `/api/grading/`, `/api/students/`, `/api/scheduling/`, `/api/analytics/`

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
| `apps/core/permissions.py` | `HasPermission` (DRF ViewSet permission) + `require_permission` (decorator for @api_view) |
| `apps/core/schema.py` | `StandardResponseAutoSchema` para drf-spectacular |
| `apps/core/constants/permissions.py` | Constantes tipadas de permisos (única fuente de verdad) |

## Permisos DRF

- `apps/core/permissions.py` — `HasPermission` (para ViewSets) y `require_permission` (para @api_view)
- Los ViewSets deben definir `action_permissions = {"list": "codename", ...}`
- Las vistas @api_view usan `@require_permission("modulo.accion")`
- Superusuarios bypassan todas las verificaciones de permisos
- Formato de permisos: `<modulo>.<accion>` (ej: `grading.create_note`)

## Management Commands

- `python manage.py seed_permissions` — Crea todos los permisos del sistema en BD (idempotente)
- `python manage.py seed_permissions --module grading` — Crea solo permisos de un módulo
- Permisos definidos en `apps/accounts/management/commands/seed_permissions.py`
- Formato: `<modulo>.<accion>` (ej: `grading.create_note`)

## Constantes de Permisos

- Ubicación: `apps/core/constants/permissions.py`
- Uso: `from apps.core.constants.permissions import grading`
- En ViewSets: `action_permissions = {"list": grading.VIEW_NOTE, ...}`
- En decoradores: `@require_permission(grading.VIEW_NOTE)`

Instancias disponibles: `accounts`, `institutions`, `academic`, `students`, `grading`, `scheduling`, `analytics`

## Tests de Seguridad

- `apps/core/tests/test_permission_integration.py` — Tests de auth + permisos por módulo
- `apps/core/tests/test_throttling.py` — Tests de rate limiting
- `apps/core/tests/test_security_headers.py` — Tests de headers de seguridad
- `apps/core/tests/test_password_validation.py` — Tests de validación de contraseñas
- `apps/core/tests/test_jwt_config.py` — Tests de configuración JWT

### Ejecutar tests de seguridad
```bash
python manage.py test apps.core.tests.test_permission_integration --settings=config.settings.test
python manage.py test apps.core.tests.test_throttling --settings=config.settings.test
python manage.py test apps.core.tests.test_security_headers --settings=config.settings.test
python manage.py test apps.core.tests.test_password_validation --settings=config.settings.test
python manage.py test apps.core.tests.test_jwt_config --settings=config.settings.test

# O todos juntos
python manage.py test apps.core.tests --settings=config.settings.test
```

## Permisos por Módulo

Todos los endpoints requieren autenticación JWT + permiso específico excepto:
- `POST /api/accounts/login/` — Público
- `POST /api/accounts/refresh/` — Público (requiere refresh token válido)

### Formato de permisos
`<modulo>.<accion>` donde acción es: `view`, `create`, `update`, `delete`

### Ejemplo de uso en ViewSets
```python
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": "modulo.view_modelo",
        "create": "modulo.create_modelo",
        ...
    }
```

### Ejemplo de uso en @api_view
```python
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@require_permission("modulo.accion")
def my_view(request):
    ...
```
