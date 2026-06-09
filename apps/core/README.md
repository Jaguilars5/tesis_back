# Módulo Core

El módulo `core` contiene componentes transversales y utilidades globales que son utilizadas por múltiples aplicaciones dentro del proyecto. Su objetivo es reducir la duplicación de código y centralizar la lógica técnica que no pertenece a un dominio de negocio específico.

## Utilidades de API

### Respuestas Estandarizadas (`apps.core.utils.responses`)

Proporciona funciones para asegurar que todas las respuestas de la API sigan el formato unificado requerido por el sistema.

#### `ok_response(data, status=200)`
Retorna una respuesta exitosa.
- **data**: El cuerpo de datos (diccionario o lista).
- **status**: Código de estado HTTP (opcional, por defecto 200). Use 201 para creaciones exitosas.

#### `error_response(msg, status=400)`
Retorna una respuesta de error.
- **msg**: Descripción del error (string o excepción).
- **status**: Código de estado HTTP (opcional, por defecto 400).

## Estándares de Uso

1. **Importación**: Siempre importe desde el paquete de utilidades:
   ```python
   from apps.core.utils import ok_response, error_response
   ```
2. **Consistencia**: No utilice la clase `Response` de DRF directamente en las vistas a menos que sea estrictamente necesario para un comportamiento no estándar (como descarga de archivos).
3. **Mantenimiento**: Cualquier lógica que se repita en más de dos módulos de negocio debería ser evaluada para su promoción al módulo `core`.

## Middleware de Seguridad

### `SecurityHeadersMiddleware`

Agrega headers de seguridad a todas las respuestas HTTP:

- `X-Content-Type-Options: nosniff` — Previene MIME sniffing
- `X-Frame-Options: DENY` — Previene clickjacking
- `X-XSS-Protection: 1; mode=block` — Activa filtro XSS del navegador
- `Referrer-Policy: strict-origin-when-cross-origin` — Controla información de referrer
- `Permissions-Policy: camera=(), microphone=(), geolocation=()` — Restringe acceso a APIs del navegador

Registrado en `MIDDLEWARE` después de `django.middleware.security.SecurityMiddleware`.

## Constantes de Permisos

### `apps/core/constants/permissions.py`

Define constantes tipadas para todos los permisos del sistema.

```python
from apps.core.constants.permissions import grading, accounts

# Uso en ViewSet
action_permissions = {
    "list": grading.VIEW_NOTE,
    "create": grading.CREATE_NOTE,
}

# Uso en decorador
@require_permission(grading.VIEW_NOTE)
```

### Módulos disponibles

| Instancia | Módulo |
|-----------|--------|
| `iam` | Cuentas de usuario, roles, permisos |
| `institutions` | Instituciones, años escolares, aulas |
| `academic` | Secciones, materias, períodos, actividades |
| `students` | Estudiantes, representantes, relaciones |
| `grading` | Calificaciones, asistencia, incidentes |

| `analytics` | Puntajes de riesgo, snapshots |

### Generación del Catálogo

`seed_permissions.py` genera el catálogo de permisos automáticamente desde estas constantes, asegurando que siempre estén sincronizadas.

## Tests

### Tests de Seguridad

| Archivo | Qué prueba |
|---------|-----------|
| `test_permissions.py` | `HasPermission` y `require_permission` |
| `test_permission_integration.py` | Auth + permisos en todos los módulos |
| `test_throttling.py` | Rate limiting |
| `test_security_headers.py` | Headers de seguridad en respuestas |
| `test_password_validation.py` | Validación de contraseñas |
| `test_jwt_config.py` | Configuración JWT |
| `test_openapi_schema.py` | Schema OpenAPI, Swagger UI y ReDoc |
| `test_permission_constants.py` | Constantes de permisos |

### Ejecutar
```bash
python manage.py test apps.core.tests --settings=config.settings.test
```

## Esquema OpenAPI

### `apps/core/schema.py`

`StandardResponseAutoSchema` extiende `drf_spectacular.openapi.AutoSchema` para integrar la generación automática de esquemas OpenAPI 3.0 con DRF.

```python
from apps.core.schema import StandardResponseAutoSchema
```

Configurado como `DEFAULT_SCHEMA_CLASS` en `REST_FRAMEWORK`.

### Endpoints

| URL | Descripción |
|-----|-------------|
| `GET /api/schema/` | Schema OpenAPI 3.0 (JSON) |
| `GET /api/docs/` | Swagger UI |
| `GET /api/redoc/` | ReDoc UI |

```bash
# Validar schema
python manage.py spectacular --settings=config.settings.local --validate

# Generar archivo
python manage.py spectacular --settings=config.settings.local --file schema.yml
```

## Permisos DRF

### `HasPermission`

Clase de permiso DRF para ViewSets. Verifica que el usuario autenticado tenga el permiso requerido para la acción actual.

Uso en ViewSets:
```python
from apps.core.permissions import HasPermission

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": "modulo.view_modelo",
        "create": "modulo.create_modelo",
        "retrieve": "modulo.view_modelo",
        "update": "modulo.update_modelo",
        "partial_update": "modulo.update_modelo",
        "destroy": "modulo.delete_modelo",
    }
```

### `require_permission`

Decorador para vistas basadas en funciones (`@api_view`).

Uso:
```python
from apps.core.permissions import require_permission

@require_permission("modulo.accion")
@api_view(["POST"])
def my_view(request):
    ...
```

### Comportamiento

- Superusuarios (`is_superuser=True`) bypassan todas las verificaciones
- Si la acción no está mapeada en `action_permissions`, se deniega por defecto
- Usa `user.has_perm(codename)` del sistema RBAC personalizado
