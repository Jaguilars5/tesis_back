# Estructura de IAM

## models/
- `user.py` — User model + UserManager
- `role.py` — Role model
- `permission.py` — Permission model
- `user_role.py` — UserRole (N:M User ↔ Role)
- `role_permission.py` — RolePermission (N:M Role ↔ Permission)

## api/
- `views.py` — 4 ViewSets (User, Role, Permission) + login/refresh
- `serializers.py` — Serializers con datos extendidos de usuario
- `filters.py` — Filtros por is_active, role_id, dni
- `urls.py` — Rutas RESTful

## services/
- `user_service.py` — Creación, búsqueda, permisos de usuarios
- `role_service.py` — CRUD de roles + asignación de permisos
- `permission_service.py` — CRUD de permisos

## repositories/
- `user_repo.py`, `role_repo.py`, `permission_repo.py`
