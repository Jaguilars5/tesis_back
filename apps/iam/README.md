# Módulo `iam` — Identity & Access Management

> Gestión de identidad, roles y permisos. Administra usuarios, sus roles y los permisos asociados a cada rol.

## Modelos

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `User` (AbstractBaseUser) | Usuario del sistema con autenticación por email | `username`, `email` (unique), `person` (FK OneToOne a Person), `is_active`, `is_staff`, `is_superuser`. `dni` expuesto via serializer desde `person.document_number`. `AUTH_USER_MODEL = "iam.User"` |
| `Role` | Rol funcional (ESTUDIANTE, DOCENTE, ADMIN, etc.) | `name`, `code` (unique), `description`, `is_active` |
| `Permission` | Permiso granular formato `<módulo>.<acción>` | `code`, `module`, `description` |
| `UserRole` | Asignación de rol a usuario | `user` (FK), `role` (FK). Unique: `(user, role)` |
| `RolePermission` | Permisos asociados a un rol | `role` (FK), `permission` (FK). Unique: `(role, permission)` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `UserService` | `create_user()`, `get_by_email()`, `search()` | Creación y búsqueda de usuarios |
| `UserService` | `change_password()` | Cambio de contraseña con validación |
| `UserService` | `assign_role()`, `remove_role()` | Gestión de roles de usuario |

## API

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| POST | `/api/iam/login/` | Iniciar sesión → JWT tokens | Público |
| POST | `/api/iam/refresh/` | Refrescar access token | Público (requiere refresh token) |
| GET/POST | `/api/iam/users/` | Listar/Crear usuarios | `iam.view/create_user` |
| GET/PATCH/DELETE | `/api/iam/users/{id}/` | CRUD individual | `iam.view/update/delete_user` |
| POST | `/api/iam/users/{id}/change-password/` | Cambiar contraseña | `iam.update_user` |
| GET | `/api/iam/users/{id}/permissions/` | Permisos del usuario | `iam.view_user` |
| GET | `/api/iam/users/search/` | Buscar usuarios | `iam.view_user` |
| GET/POST | `/api/iam/roles/` | Listar/Crear roles | `iam.view/create_role` |
| GET/PATCH/DELETE | `/api/iam/roles/{id}/` | CRUD individual | `iam.view/update/delete_role` |
| POST | `/api/iam/roles/{id}/add-permission/` | Asignar permiso a rol | `iam.update_role` |
| POST | `/api/iam/roles/{id}/remove-permission/` | Quitar permiso a rol | `iam.update_role` |
| POST | `/api/iam/roles/{id}/assign-permissions/` | Asignar múltiples permisos | `iam.update_role` |
| GET/POST | `/api/iam/permissions/` | Listar/Crear permisos | `iam.view/create_permission` |
| PATCH/DELETE | `/api/iam/permissions/{id}/` | Actualizar/Eliminar | `iam.update/delete_permission` |
| POST | `/api/iam/permissions/bulk-create/` | Crear múltiples permisos | `iam.create_permission` |
| GET | `/api/iam/permissions/by-module/` | Permisos agrupados por módulo | `iam.view_permission` |

## Respuestas Enriquecidas

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": ""}`.

```json
{
  "ok": true,
  "data": {
    "id": 1,
    "username": "juan@example.com",
    "dni": "1234567890",
    "names": "Juan",
    "last_names": "Pérez",
    "email": "juan@example.com",
    "role": "DOCENTE",
    "role_id": 2,
    "is_active": true,
    "permissions": ["grading.view_note", "grading.create_note"]
  },
  "msg": ""
}
```

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
| Blacklist | Refresh tokens invalidados al refrescar |
