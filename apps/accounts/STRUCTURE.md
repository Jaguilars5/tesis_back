# Estructura del Módulo Accounts

```
accounts/
├─ api/                          # REST API (DRF)
│  ├─ __init__.py
│  ├─ filters.py                 # Filtros de búsqueda
│  ├─ serializers.py             # Validadores de entrada/salida
│  ├─ urls.py                    # Router DRF
│  └─ views.py                   # ViewSets (3)
│
├─ decorators/                   # Decoradores personalizados
│  ├─ __init__.py                # @require_permission()
│  └─ README.md
│
├─ middleware/                   # Middleware personalizado
│  ├─ __init__.py                # JWTAuthMiddleware
│  ├─ jwt_auth.py                # Implementación JWT
│  └─ README.md
│
├─ models/                       # Capa de datos (5 modelos)
│  ├─ __init__.py                # Re-export de modelos
│  ├─ permission.py              # Permission
│  ├─ role.py                    # Role
│  ├─ role_permission.py         # RolePermission (M2M explícito)
│  ├─ user.py                    # User
│  └─ user_permission.py         # UserPermission (excepciones)
│
├─ repositories/                 # Capa de acceso a datos (3 repos)
│  ├─ __init__.py
│  ├─ permission_repo.py         # PermissionRepository
│  ├─ role_repo.py               # RoleRepository
│  └─ user_repo.py               # UserRepository
│
├─ services/                     # Capa de lógica de negocio (3)
│  ├─ __init__.py
│  ├─ permission_service.py      # PermissionService
│  ├─ role_service.py            # RoleService
│  └─ user_service.py            # UserService
│
├─ tests/                        # Tests (3 suites)
│  ├─ __init__.py
│  ├─ test_api.py                # Tests HTTP (APIClient)
│  ├─ test_models.py             # Tests unitarios de modelos
│  └─ test_services.py           # Tests de lógica de negocio
│
├─ utils/                        # Funciones auxiliares
│  ├─ __init__.py                # JWT, password, permission helpers
│  └─ README.md
│
├─ __init__.py                   # Paquete Python
├─ admin.py                      # Panel Django (5 ModelAdmin)
├─ apps.py                       # Configuración de app
├─ README.md                     # Documentación principal
├─ urls.py                       # Rutas: path('', include(api.urls))
└─ migrations/                   # (Auto-generadas)
```

## Organización por Responsabilidades

### 🗄️ Capa de Datos

- **models/** — Definiciones de tablas y lógica de modelo
- **repositories/** — Queries complejas, acceso a BD

### 💼 Capa de Lógica

- **services/** — Orquestación de operaciones, validaciones
- **tests/** — Verificación de comportamiento

### 🌐 Capa HTTP

- **api/** — Serialización, vistas, rutas
- **admin.py** — Interfaz de administración

### 🛠️ Utilidades

- **utils/** — Helpers (JWT, hashing, permisos)
- **middleware/** — Procesamiento de requests
- **decorators/** — Protección de vistas

## ¿Dónde agregar cosas nuevas?

| Necesidad         | Carpeta         | Archivo                    |
| ----------------- | --------------- | -------------------------- |
| Nuevo modelo      | `models/`       | `nuevo_modelo.py`          |
| Query compleja    | `repositories/` | `{modelo}_repo.py`         |
| Lógica de negocio | `services/`     | `{modelo}_service.py`      |
| Endpoint API      | `api/`          | `views.py` (nuevo ViewSet) |
| Serializer        | `api/`          | `serializers.py`           |
| Función auxiliar  | `utils/`        | `__init__.py`              |
| Test              | `tests/`        | `test_{tipo}.py`           |

## Niveles de Importación

### ✅ Correcto

```python
# Desde otra app
from apps.accounts.models import User
from apps.accounts.services.user_service import UserService
from apps.accounts.middleware import JWTAuthMiddleware
from apps.accounts.decorators import require_permission

# Dentro del módulo accounts
from apps.accounts.models import User  # Desde models/__init__.py
from .repositories.user_repo import UserRepository
from .services.user_service import UserService
```

### ❌ Incorrecto

```python
# No importes de archivos internos de carpetas
from apps.accounts.utils.helpers import hash_password  # NO
from apps.accounts.middleware.jwt_auth import JWTAuthMiddleware  # Usa __init__.py
```

## Re-exports

Las siguientes carpetas re-exportan sus contenidos en `__init__.py`:

- **models/** → Todos los modelos disponibles
- **utils/** → Todas las funciones útiles
- **middleware/** → JWTAuthMiddleware
- **decorators/** → @require_permission()

Esto permite importaciones limpias:

```python
from apps.accounts.utils import generate_access_token  # ✓
from apps.accounts.middleware import JWTAuthMiddleware  # ✓
from apps.accounts.models import User  # ✓
```
