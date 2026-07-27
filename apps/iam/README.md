# Módulo `iam` — Identity & Access Management

> Gestión de identidad, roles y permisos. Administra usuarios, sus roles y los permisos asociados a cada rol. `AUTH_USER_MODEL = "iam.User"`.

## Modelos (5)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `User` (AbstractBaseUser) | Usuario del sistema con autenticación por **username** | `username` (unique), `email` (unique), `person` (FK OneToOne, nullable), `is_active`, `is_staff`, `is_superuser`. `USERNAME_FIELD = "username"` |
| `Role` | Rol funcional (ESTUDIANTE, DOCENTE, ADMIN, etc.) | `name` (unique), `code` (unique, nullable), `description`, `is_active`. Ordenado por `name` |
| `Permission` | Permiso granular formato `<módulo>.<acción>` | `code` (unique), `module`, `description`. Ordenado por `code` |
| `UserRole` | Asignación de rol a usuario | `user` (FK), `role` (FK), `assigned_at`, `expires_at`. Unique: `(user, role)` |
| `RolePermission` | Permisos asociados a un rol | `role` (FK), `permission` (FK). Unique: `(role, permission)` |

## Repositorios (3)

| Repositorio | Métodos clave |
|-------------|---------------|
| `UserRepository` | `get_by_id()`, `get_by_username()`, `get_by_email()`, `get_by_dni()`, `get_all_active()`, `get_by_role()`, `create()`, `update()`, `delete()` (desactiva), `search()`, `bulk_create()` |
| `RoleRepository` | `get_by_id()`, `get_by_name()`, `get_all()`, `get_all_active()`, `create()`, `update()`, `delete()` (desactiva), `add_permission()`, `remove_permission()`, `set_permissions()` |
| `PermissionRepository` | `get_by_id()`, `get_by_code()`, `get_all()`, `get_by_module()`, `create()`, `create_many()`, `update()`, `delete()`, `search()` |

> **Nota:** Los repositorios NO heredan de `BaseRepository`. Son clases con métodos `@staticmethod`.

## Servicios (3)

| Servicio | Métodos principales |
|----------|---------------------|
| `UserService` | `create_user()`, `get_user()`, `get_user_by_email()`, `list_users()`, `update_user()`, `change_password()`, `deactivate_user()`, `has_permission()`, `get_user_permissions()`, `search_users()` |
| `RoleService` | `create_role()`, `get_role()`, `list_roles()`, `update_role()`, `deactivate_role()`, `add_permission_to_role()`, `remove_permission_from_role()`, `assign_permissions_to_role()` |
| `PermissionService` | `create_permission()`, `create_permissions_bulk()`, `list_permissions()`, `list_permissions_by_module()`, `update_permission()`, `delete_permission()`, `search_permissions()` |

## API — Endpoints

| Método | Endpoint | ViewSet/Auth | Permiso |
|--------|----------|-------------|---------|
| POST | `/api/iam/login/` | CustomTokenObtainPairView | Público |
| POST | `/api/iam/refresh/` | CustomTokenRefreshView | Público |
| GET/POST | `/api/iam/users/` | UserViewSet | `iam.view/create_user` |
| GET/PUT/PATCH/DEL | `/api/iam/users/{id}/` | UserViewSet | `iam.view/update/delete_user` |
| POST | `/api/iam/users/{id}/change-password/` | UserViewSet | `iam.update_user` |
| GET | `/api/iam/users/{id}/permissions/` | UserViewSet | `iam.view_user` |
| GET | `/api/iam/users/search/` | UserViewSet | `iam.view_user` |
| GET/POST | `/api/iam/roles/` | RoleViewSet | `iam.view/create_role` |
| GET/PUT/PATCH/DEL | `/api/iam/roles/{id}/` | RoleViewSet | `iam.view/update/delete_role` |
| POST | `/api/iam/roles/{id}/add-permission/` | RoleViewSet | `iam.update_role` |
| POST | `/api/iam/roles/{id}/remove-permission/` | RoleViewSet | `iam.update_role` |
| POST | `/api/iam/roles/{id}/assign-permissions/` | RoleViewSet | `iam.update_role` |
| GET/POST | `/api/iam/permissions/` | PermissionViewSet | `iam.view/create_permission` |
| GET/PUT/PATCH/DEL | `/api/iam/permissions/{id}/` | PermissionViewSet | `iam.view/update/delete_permission` |
| POST | `/api/iam/permissions/bulk-create/` | PermissionViewSet | `iam.create_permission` |
| GET | `/api/iam/permissions/by-module/` | PermissionViewSet | `iam.view_permission` |

## Serializers (12)

| Serializer | Campos readonly |
|------------|-----------------|
| `UserListSerializer` | `dni`, `names`, `last_names`, `role` (code), `created_at` |
| `UserDetailSerializer` | `dni`, `names`, `last_names`, `role` (code), `role_id`, `username`, `created_at`, `updated_at` |
| `UserCreateSerializer` | `username` (autogenerado) |
| `UserLoginDataSerializer` | `id`, `username`, `dni`, `names`, `last_names`, `email`, `role`, `role_id`, `is_active`, `permissions` |
| `LoginResponseSerializer` | `access`, `refresh`, `user` |
| `TokenRefreshResponseSerializer` | `access`, `user` |
| `LoginSerializer` | TokenObtainPairSerializer personalizado |
| `CustomTokenRefreshSerializer` | TokenRefreshSerializer personalizado |
| `PermissionSerializer` | `id`, `created_at`, `updated_at` |
| `RolePermissionSerializer` | `id`, `created_at`, `permission` (anidado) |
| `RoleListSerializer` | `id`, `created_at` |
| `RoleDetailSerializer` | `id`, `created_at`, `updated_at`, `role_permissions` (anidado) |

## Tests

```bash
python manage.py test apps.iam --settings=config.settings.test
```

## Dependencias

- `people.Person` — Perfil físico asociado al usuario

## Autenticación JWT

| Configuración | Valor |
|---------------|-------|
| Access token | 15 minutos |
| Refresh token | 7 días (con rotación) |
| Algoritmo | HS256 |
| Campo login | `username` (con `password`) |
