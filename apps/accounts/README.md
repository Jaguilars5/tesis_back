# Módulo `accounts` — Gestión de Identidad y Acceso

Este módulo constituye el núcleo de seguridad del sistema, encargado de la gestión de usuarios, roles, permisos y autenticación basada en JWT.

Su diseño sigue una arquitectura desacoplada en capas (Modelos → Repositorios → Servicios → API), permitiendo escalabilidad, mantenibilidad y facilidad de prueba.

---

## Estructura del Módulo

```
accounts/
├── models/
├── repositories/
├── services/
├── api/
├── middleware/
├── decorators/
├── utils/
└── tests/
```

---

## Modelos de Datos

### User

Entidad principal del sistema.

- `dni`
- `names`
- `last_names`
- `email`
- `role`
- `institution`
- `active`

---

### Role

- `name`
- `description`
- `active`

---

### Permission

Formato:

```
modulo.accion
```

Ejemplo:

```
grading.create_note
```

---

### RolePermission / UserPermission

- RolePermission: permisos por rol
- UserPermission: overrides individuales

---

## Capa de Servicios

### UserService

- create_user
- update_user
- change_password
- grant_permission
- revoke_permission
- has_permission

### RoleService

- create_role
- assign_permissions_to_role
- deactivate_role

### PermissionService

- create_permissions_bulk
- list_permissions_by_module

---

## Management Commands

### `seed_permissions`

Crea todos los permisos del catálogo en la base de datos. Es idempotente (puede ejecutarse múltiples veces sin duplicar).

```bash
# Seedear todos los permisos
python manage.py seed_permissions

# Seedear solo permisos de un módulo
python manage.py seed_permissions --module grading
```

Módulos disponibles: `accounts`, `institutions`, `academic`, `students`, `grading`, `scheduling`, `analytics`

---

## API REST (Resumen)

### Autenticación

- POST /api/accounts/login/
- POST /api/accounts/refresh/

### Usuarios

- GET /api/accounts/users/
- POST /api/accounts/users/
- GET /api/accounts/users/{id}/
- PUT /api/accounts/users/{id}/
- DELETE /api/accounts/users/{id}/
- POST /api/accounts/users/{id}/change-password/
- POST /api/accounts/users/{id}/grant-permission/
- POST /api/accounts/users/{id}/revoke-permission/
- GET /api/accounts/users/search/

### Roles

- GET /api/accounts/roles/
- POST /api/accounts/roles/
- POST /api/accounts/roles/{id}/assign-permissions/

### Permisos

- GET /api/accounts/permissions/
- POST /api/accounts/permissions/bulk-create/

📌 Ver documentación detallada:
accounts/api/README.md

---

## Seguridad

### Autenticación y Permisos

Endpoints públicos (sin auth):
- `POST /api/accounts/login/`
- `POST /api/accounts/refresh/`

Endpoints protegidos (requieren auth + permiso):

| ViewSet | View | Create | Update | Delete |
|---------|------|--------|--------|--------|
| User | `accounts.view_user` | `accounts.create_user` | `accounts.update_user` | `accounts.delete_user` |
| Role | `accounts.view_role` | `accounts.create_role` | `accounts.update_role` | `accounts.delete_role` |
| Permission | `accounts.view_permission` | `accounts.create_permission` | `accounts.update_permission` | `accounts.delete_permission` |

Seedear permisos:
```bash
python manage.py seed_permissions --module accounts
```

---

## Pruebas

```
python manage.py test apps.accounts
```

---

## Lógica de Permisos

1. Permisos por rol
2. Overrides por usuario

```
user.has_perm('grading.view_note')

service.revoke_permission(...)
service.grant_permission(...)
```
