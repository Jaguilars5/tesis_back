# Módulo `core` — Estructura

## Árbol de archivos

```
core/
├── __init__.py
├── apps.py
├── urls.py
├── tasks.py                    # Tareas Celery base
├── README.md
│
├── api/
│   ├── __init__.py
│   ├── exceptions.py           # custom_exception_handler (formato {"ok":false,"msg":"..."})
│   ├── filters.py              # Filtros DRF para búsqueda
│   ├── pagination.py           # StandardResultsSetPagination
│   ├── permissions.py          # HasPermission (DRF permission check por action_permissions)
│   ├── renderers.py            # StandardResponseRenderer (envuelve respuestas en {"ok":true,"data":...})
│   ├── role_handlers.py        # Manejadores de roles por defecto
│   ├── schema.py               # StandardResponseAutoSchema para drf-spectacular
│   ├── serializers.py          # Serializers base compartidos
│   └── views.py                # Vistas base compartidas
│
├── models/
│   ├── __init__.py             # TimeStampedModel, AuditLog
│   ├── base.py                 # TimeStampedModel (created_at, updated_at)
│   └── audit_log.py            # AuditLog (bitácora centralizada)
│
├── constants/
│   ├── __init__.py
│   └── permissions.py          # Constantes de permisos por módulo
│
├── middleware/
│   ├── __init__.py
│   └── security.py             # SecurityHeadersMiddleware
│
├── repositories/
│   ├── __init__.py
│   └── base.py                 # BaseRepository (CRUD genérico)
│
├── management/
│   └── commands/
│       └── seed_catalogs.py    # Pobla catálogos del sistema
│
├── utils/
│   ├── __init__.py
│   └── responses.py            # ok_response(), error_response()
│
└── tests/
    ├── __init__.py
    ├── helpers.py           # create_test_user(), create_test_student(), _create_person()
    ├── test_exceptions.py
    ├── test_jwt_config.py
    ├── test_openapi_schema.py
    ├── test_pagination.py
    ├── test_password_validation.py
    ├── test_permission_constants.py
    ├── test_permission_integration.py
    ├── test_permissions.py
    ├── test_phase8_functional.py
    ├── test_renderers.py
    ├── test_row_level_security.py
    ├── test_security_headers.py
    ├── test_seed_catalogs.py
    └── test_throttling.py
```

## Patrón de respuesta estándar

Todas las respuestas de API usan el formato `{"ok": bool, "data": ..., "msg": "..."}` gestionado por `StandardResponseRenderer`.

Controladores:
- `api/renderers.StandardResponseRenderer` — Renderer global que envuelve respuestas DRF en `{ok, data, msg}`
- `api/exceptions.custom_exception_handler` — Manejador global de excepciones que garantiza el formato incluso en errores
- `api/pagination.StandardResultsSetPagination` — Paginación con `{ count, next, previous, results }`

**Nota:** El archivo `utils/responses.py` fue eliminado (contenía `ok_response()`/`error_response()`). Ahora el renderer gestiona el formato automáticamente.

## Permisos

`HasPermission` verifica que el usuario tenga el permiso definido en `ViewSet.action_permissions`:
```python
class MyViewSet(viewsets.ModelViewSet):
    action_permissions = {
        "list": "modulo.view_model",
        "create": "modulo.create_model",
        ...
    }
    permission_classes = [IsAuthenticated, HasPermission]
```

## Guía de imports

```python
# Modelos
from apps.core.models import TimeStampedModel, AuditLog

# API
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission
from apps.core.api.renderers import StandardResponseRenderer
from apps.core.api.exceptions import custom_exception_handler
from apps.core.api.schema import StandardResponseAutoSchema

# Constantes
from apps.core.constants.permissions import grading, students, behavior, ...

# Middleware
from apps.core.middleware.security import SecurityHeadersMiddleware

# Repositorio base
from apps.core.repositories.base import BaseRepository

# Tests helpers
from apps.core.tests.helpers import create_test_user, create_test_student

# Nota: utils/responses.py fue eliminado. Usar StandardResponseRenderer en su lugar.
```
