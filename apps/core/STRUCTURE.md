# Módulo `core` — Estructura

## Árbol de archivos

```
core/
├── __init__.py
├── apps.py
├── urls.py                     # Vacío (sin rutas)
├── tasks.py                    # Vacío (sin tareas)
├── README.md
│
├── api/
│   ├── exceptions.py           # custom_exception_handler
│   ├── filters.py              # RoleBasedFilterBackend + PUBLIC_CATALOGS
│   ├── pagination.py           # StandardResultsSetPagination
│   ├── permissions.py          # HasPermission, require_permission
│   ├── renderers.py            # StandardResponseRenderer
│   ├── role_handlers.py        # 4 RoleHandlers (ESTUDIANTE, REPRESENTANTE, DOCENTE, CONSEJERO)
│   ├── schema.py               # StandardResponseAutoSchema
│   ├── serializers.py          # VACÍO (sin contenido)
│   └── views.py                # VACÍO (sin contenido)
│
├── models/
│   ├── __init__.py             # TimeStampedModel, AuditLog
│   ├── base.py                 # TimeStampedModel (abstracto)
│   └── audit_log.py            # AuditLog (bitácora centralizada)
│
├── constants/
│   ├── __init__.py
│   └── permissions.py          # 9 clases de permisos (sin ConfigurationPermissions)
│
├── middleware/
│   ├── __init__.py
│   └── security.py             # SecurityHeadersMiddleware
│
├── repositories/
│   └── base.py                 # BaseRepository (CRUD genérico, sin __init__.py)
│
├── management/
│   └── commands/
│       ├── __init__.py
│       ├── seed_catalogs.py    # Pobla catálogos del sistema
│       └── seed_test_data.py   # Datos de prueba (usa seed_catalogs + seed_permissions)
│
├── utils/
│   ├── __init__.py             # Nota: responses.py eliminado
│   └── (responses.py eliminado — usar StandardResponseRenderer)
│
└── tests/
    ├── __init__.py
    ├── helpers.py              # create_test_user(), create_test_student(), _create_person()
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
    ├── test_throttling.py
    └── test_timestamps.py
```

## Patrón de respuesta estándar

Todas las respuestas de API usan `{"ok": bool, "data": ..., "msg": "..."}` gestionado por `StandardResponseRenderer`.

Controladores:
- `api/renderers.StandardResponseRenderer` — Renderer global
- `api/exceptions.custom_exception_handler` — Manejador global de excepciones
- `api/pagination.StandardResultsSetPagination` — Paginación con `{ count, next, previous, results }`

## Permisos

`HasPermission` verifica `ViewSet.action_permissions`:

```python
class MyViewSet(viewsets.ModelViewSet):
    action_permissions = {
        "list": "modulo.view_model",
        "create": "modulo.create_model",
    }
    permission_classes = [IsAuthenticated, HasPermission]
```

## Guía de imports

```python
from apps.core.models import TimeStampedModel, AuditLog

from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission
from apps.core.api.renderers import StandardResponseRenderer
from apps.core.api.exceptions import custom_exception_handler
from apps.core.api.schema import StandardResponseAutoSchema

from apps.core.constants.permissions import grading, students, behavior, analytics, attendance

from apps.core.middleware.security import SecurityHeadersMiddleware

from apps.core.repositories.base import BaseRepository

from apps.core.tests.helpers import create_test_user, create_test_student
```
