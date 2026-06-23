# Módulo `iam` — Identity & Access Management — Estructura

## Árbol de archivos

```
iam/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py (login/, refresh/, users/, roles/, permissions/)
├── README.md
│
├── models/
│   ├── __init__.py             # 5 modelos exportados
│   ├── user.py                 # User (AbstractBaseUser, TimeStampedModel) — AUTH_USER_MODEL
│   ├── role.py                 # Role (TimeStampedModel)
│   ├── permission.py           # Permission (TimeStampedModel)
│   ├── user_role.py            # UserRole (TimeStampedModel)
│   └── role_permission.py      # RolePermission (TimeStampedModel)
│
├── repositories/
│   ├── __init__.py             # 3 repositorios exportados
│   ├── user_repo.py            # UserRepository (NO hereda BaseRepository)
│   ├── role_repo.py            # RoleRepository (NO hereda BaseRepository)
│   └── permission_repo.py      # PermissionRepository (NO hereda BaseRepository)
│
├── services/
│   ├── __init__.py             # 3 servicios exportados
│   ├── user_service.py         # UserService
│   ├── role_service.py         # RoleService
│   └── permission_service.py   # PermissionService
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 12 serializers
│   ├── views.py                # UserViewSet, RoleViewSet, PermissionViewSet + auth views
│   ├── filters.py              # UserFilter, RoleFilter, PermissionFilter
│   └── urls.py                 # Router: users/, roles/, permissions/ + login/, refresh/
│
├── management/
│   └── commands/
│       ├── __init__.py
│       └── seed_permissions.py # Pobla permisos + roles del sistema
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

from apps.iam.repositories import UserRepository, RoleRepository, PermissionRepository

from apps.iam.services.user_service import UserService
from apps.iam.services.role_service import RoleService
from apps.iam.services.permission_service import PermissionService

from apps.iam.api.views import UserViewSet, RoleViewSet, PermissionViewSet
```
