# Módulo `core` — Componentes Transversales

> Utilidades globales, middleware de seguridad, permisos DRF, paginación, renderer de respuestas, modelo base, repositorio base y bitácora de auditoría.

## Componentes

### `StandardResponseRenderer` (`apps.core.api.renderers`)
Renderer global que envuelve todas las respuestas JSON en el formato `{"ok": bool, "data": ..., "msg": "..."}`.
- Respuestas exitosas (<400): `{"ok": true, "data": ..., "msg": ""}`
- Respuestas de error (≥400): `{"ok": false, "data": ..., "msg": "..."}`
- Si la respuesta ya tiene el formato, no lo modifica.

### `custom_exception_handler` (`apps.core.api.exceptions`)
Manejador global de excepciones DRF. Garantiza que errores no controlados también retornen el formato estándar.
- Errores DRF: reformatea con `{"ok": false, "data": response.data, "msg": str(exc)}`
- Errores 500: retorna `{"ok": false, "data": {}, "msg": "Error interno del servidor: ..."}`

### `StandardResultsSetPagination` (`apps.core.api.pagination`)
Paginación por defecto: 20 items/página, configurable vía `?page_size=` (máx 100).
Respuesta paginada: `{ count, next, previous, results }`

### `HasPermission` (`apps.core.api.permissions`), `require_permission` (`apps.core.api.permissions`)
Control de acceso basado en permisos (RBAC).
- `HasPermission`: clase de permiso DRF para ViewSets. Lee `action_permissions` del ViewSet y verifica `user.has_perm(codename)`.
- `require_permission(codename)`: decorador para vistas basadas en función (`@api_view`).
- Superusuarios bypassan todas las verificaciones.

### `BaseRepository` (`apps.core.repositories.base`)
CRUD genérico: `get_all()`, `get_by_id()`, `get_by_uuid()`, `exists()`, `count()`, `create()`, `update()`, `delete()`.

### `TimeStampedModel` (`apps.core.models.base`)
Modelo abstracto: `created_at` (default=timezone.now), `updated_at` (default=timezone.now).

### `AuditLog` (`apps.core.models.audit_log`)
Bitácora centralizada: `user` (FK), `action` (CREATE/UPDATE/DELETE/RECOVER), `model_name`, `record_id`, `changes` (JSON), `ip_address`, `user_agent`.

### `SecurityHeadersMiddleware` (`apps.core.middleware.security`)
Agrega headers de seguridad a todas las respuestas:
`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`.

### `RoleBasedFilterBackend` (`apps.core.api.filters`)
Filtro global de seguridad a nivel de fila (RLS). Despacha según `user.user_category` a handlers específicos.

### `StandardResponseAutoSchema` (`apps.core.api.schema`)
Extiende `drf-spectacular AutoSchema` para documentar automáticamente el formato `{ok, data, msg}` en OpenAPI 3.0.

### `RoleHandlers` (`apps.core.api.role_handlers`)
Manejadores de RLS para cada categoría de usuario (ESTUDIANTE, DOCENTE, REPRESENTANTE, ADMIN).

### `SeedCatalogsCommand` (`apps.core.management.commands.seed_catalogs`)
Pobla 26+ catálogos del sistema. Idempotente: `python manage.py seed_catalogs`.

## Constantes de Permisos (`apps.core.constants.permissions`)

| Instancia | Módulo |
|-----------|--------|
| `iam` | Usuarios, roles, permisos |
| `people` | Personas, tipos de documento |
| `institutions` | Años escolares, niveles, subniveles, grados, secciones |
| `academic` | Materias, períodos, configuraciones, ofertas, asignación docente, proyectos |
| `students` | Estudiantes, representantes, matrículas |
| `grading` | Notas, bloques, componentes, actividades, promedios, recuperación |
| `attendance` | Asistencia, estados, tipos de ausencia |
| `behavior` | Incidentes, evaluaciones conductuales, habilidades socioemocionales |
| `analytics` | Scores de riesgo, snapshots, alertas, factores |
| `configuration` | Configuración del sistema |
| `integration` | Cola de sincronización, operaciones, estados |

## Tests

```bash
python manage.py test apps.core.tests --settings=config.settings.test
```

| Archivo | Prueba |
|---------|--------|
| `test_permissions.py` | HasPermission, require_permission |
| `test_permission_integration.py` | Auth + permisos multi-módulo |
| `test_permission_constants.py` | Constantes de permisos |
| `test_throttling.py` | Rate limiting |
| `test_security_headers.py` | Headers de seguridad |
| `test_password_validation.py` | Validación de contraseñas |
| `test_jwt_config.py` | Configuración JWT |
| `test_openapi_schema.py` | Schema OpenAPI |
| `test_exceptions.py` | Manejador de excepciones |
| `test_renderers.py` | StandardResponseRenderer |
| `test_pagination.py` | Paginación |
| `test_row_level_security.py` | RLS multi-rol |
| `test_seed_catalogs.py` | Seed de catálogos |
| `test_phase8_functional.py` | Flujos funcionales completos |

## OpenAPI

| URL | Descripción |
|-----|-------------|
| `GET /api/schema/` | Schema OpenAPI 3.0 (JSON) |
| `GET /api/docs/` | Swagger UI |
| `GET /api/redoc/` | ReDoc UI |

```bash
python manage.py spectacular --validate
```
