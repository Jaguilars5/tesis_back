# API - Módulo Accounts

Esta API gestiona la autenticación y administración de usuarios, roles y permisos del sistema.

---

## Formato de Respuesta

Todas las respuestas siguen el esquema estandarizado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Autenticación

Header requerido:
```
Authorization: Bearer <access_token>
```

### Endpoints Públicos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/accounts/login/` | Iniciar sesión |
| POST | `/api/accounts/refresh/` | Refrescar token |

### Login
**POST** `/api/accounts/login/`

Request:
```json
{
  "email": "admin@test.com",
  "password": "123456"
}
```

Response:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "email": "admin@test.com",
    "person": {
      "id": 1,
      "names": "Admin",
      "last_names": "Test",
      "document_number": "1234567890"
    },
    "institution": {
      "id": 1,
      "name": "Institución Ejemplo"
    },
    "active": true
  }
}
```

### Refresh
**POST** `/api/accounts/refresh/`

Request:
```json
{
  "refresh": "eyJ..."
}
```

Response:
```json
{
  "access": "eyJ...",
  "user": { ... }
}
```

---

## Permisos

Todos los endpoints (excepto login y refresh) requieren permisos específicos:

| ViewSet | Acción | Permiso |
|---------|--------|---------|
| User | list, retrieve | `accounts.view_user` |
| User | create | `accounts.create_user` |
| User | update, change_password, grant_permission, revoke_permission | `accounts.update_user` |
| User | destroy | `accounts.delete_user` |
| Role | list, retrieve | `accounts.view_role` |
| Role | create | `accounts.create_role` |
| Role | update, assign_permissions | `accounts.update_role` |
| Role | destroy | `accounts.delete_role` |
| Permission | list, retrieve | `accounts.view_permission` |
| Permission | create, bulk_create | `accounts.create_permission` |

---

## Usuarios (`/api/accounts/users/`)

### Listar
**GET** `/api/accounts/users/`

Response (paginado):
```json
{
  "ok": true,
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "email": "admin@test.com",
        "person": { "names": "Admin", "last_names": "Test" },
        "institution": { "id": 1, "name": "Colegio" },
        "active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear
**POST** `/api/accounts/users/`

Request:
```json
{
  "person": {
    "document_type": 1,
    "document_number": "1234567890",
    "names": "Juan",
    "last_names": "Pérez",
    "email": "juan@test.com",
    "birth_date": "1990-05-15"
  },
  "password": "123456",
  "institution": 1
}
```

### Obtener
**GET** `/api/accounts/users/{id}/`

### Actualizar
**PATCH** `/api/accounts/users/{id}/`

### Eliminar (soft delete)
**DELETE** `/api/accounts/users/{id}/`

### Cambiar Contraseña
**POST** `/api/accounts/users/{id}/change-password/`

Request:
```json
{
  "new_password": "newpass123"
}
```

### Conceder Permiso
**POST** `/api/accounts/users/{id}/grant-permission/`

Request:
```json
{
  "permission_code": "grading.view_note",
  "reason": "Acceso temporal"
}
```

### Revocar Permiso
**POST** `/api/accounts/users/{id}/revoke-permission/`

Request:
```json
{
  "permission_code": "grading.view_note"
}
```

---

## Roles (`/api/accounts/roles/`)

### Listar
**GET** `/api/accounts/roles/`

### Crear
**POST** `/api/accounts/roles/`

Request:
```json
{
  "name": "Docente",
  "code": "TEACHER",
  "description": "Rol para docentes"
}
```

### Obtener
**GET** `/api/accounts/roles/{id}/`

### Actualizar
**PATCH** `/api/accounts/roles/{id}/`

### Asignar Permisos
**POST** `/api/accounts/roles/{id}/assign-permissions/`

Request:
```json
{
  "permission_ids": [1, 2, 3]
}
```

---

## Permisos (`/api/accounts/permissions/`)

### Listar
**GET** `/api/accounts/permissions/`

### Crear
**POST** `/api/accounts/permissions/`

Request:
```json
{
  "code": "grading.view_note",
  "module": "grading",
  "description": "Ver calificaciones"
}
```

### Creación Masiva
**POST** `/api/accounts/permissions/bulk-create/`

Request:
```json
{
  "permissions": [
    {"code": "grading.view_note", "module": "grading", "description": "Ver notas"},
    {"code": "grading.create_note", "module": "grading", "description": "Crear notas"}
  ]
}
```