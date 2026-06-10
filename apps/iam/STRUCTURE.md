# Módulo `iam` — Identity & Access Management — Estructura

## Árbol de archivos

```
iam/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # login/, refresh/, users/, roles/, permissions/
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── user.py                 # User(AbstractBaseUser) — AUTH_USER_MODEL
│   ├── role.py                 # Role (name, code, is_active)
│   ├── permission.py           # Permission (code, module)
│   ├── user_role.py            # UserRole (user N:M role)
│   └── role_permission.py      # RolePermission (role N:M permission)
│
├── repositories/
│   ├── __init__.py
│   ├── user_repo.py            # UserRepository
│   ├── role_repo.py            # RoleRepository
│   └── permission_repo.py      # PermissionRepository
│
├── services/
│   ├── __init__.py
│   ├── user_service.py         # UserService (create, search, change_password, assign_role)
│   ├── role_service.py         # RoleService (CRUD + assign/remove permission)
│   └── permission_service.py   # PermissionService (CRUD + bulk_create + by_module)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # UserSerializer, RoleSerializer, PermissionSerializer + login/refresh
│   ├── views.py                # UserViewSet, RoleViewSet, PermissionViewSet + auth views
│   ├── filters.py              # Filtros: is_active, role_id, dni
│   └── urls.py
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_gaps.py
    ├── test_models.py
    ├── test_permissions.py
    ├── test_repositories.py
    └── test_services.py
```

## Serializers (12)

| Serializer | Tipo | Campos readonly |
|------------|------|-----------------|
| `UserListSerializer` | ModelSerializer | `dni`, `names`, `last_names`, `role` |
| `UserDetailSerializer` | ModelSerializer | `dni`, `names`, `last_names`, `role`, `created_at`, `updated_at` |
| `UserCreateSerializer` | Serializer | `username` (autogenerado post-create) |
| `UserLoginDataSerializer` | Serializer | `permissions`, `role`, `role_id`, `dni` |
| `LoginResponseSerializer` | Serializer | — |
| `TokenRefreshResponseSerializer` | Serializer | — |
| `PermissionSerializer` | ModelSerializer | — |
| `RolePermissionSerializer` | ModelSerializer | — |
| `RoleListSerializer` | ModelSerializer | — |
| `RoleDetailSerializer` | ModelSerializer | — |
| `LoginSerializer` | TokenObtainPairSerializer | — |
| `CustomTokenRefreshSerializer` | TokenRefreshSerializer | — |

## Workflow

```
POST /login/ → JWT tokens + datos de usuario + lista de permisos
    ↓
Refresh token con rotación (7 días de vida)
    ↓
Acceso a endpoints protegidos via HasPermission + action_permissions
    ↓
UserService.create_user() → crea Person + User + UserRole
```

## Guía de imports

```python
from apps.iam.models import User, Role, Permission, UserRole, RolePermission
from apps.iam.services.user_service import UserService
from apps.iam.services.role_service import RoleService
from apps.iam.services.permission_service import PermissionService
from apps.iam.api.views import UserViewSet, RoleViewSet, PermissionViewSet
```
