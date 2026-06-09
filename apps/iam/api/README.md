# API - Módulo IAM

Esta API gestiona usuarios, roles, permisos y autenticación JWT del sistema.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Endpoints Públicos (sin autenticación)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `login/` | POST | Iniciar sesión (username + password) → JWT tokens + datos de usuario |
| `refresh/` | POST | Refrescar access token usando refresh token |

## Autenticación y Permisos

Header para endpoints protegidos: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `permissions/` | GET | `iam.view_permission` |
| `permissions/` | POST | `iam.create_permission` |
| `permissions/{id}/` | PATCH/DELETE | `iam.update/delete_permission` |
| `permissions/bulk-create/` | POST | `iam.create_permission` |
| `permissions/by-module/` | GET | `iam.view_permission` |
| `roles/` | GET/POST | `iam.view/create_role` |
| `roles/{id}/` | GET/PATCH/DELETE | `iam.view/update/delete_role` |
| `roles/{id}/add-permission/` | POST | `iam.update_role` |
| `roles/{id}/remove-permission/` | POST | `iam.update_role` |
| `roles/{id}/assign-permissions/` | POST | `iam.update_role` |
| `users/` | GET/POST | `iam.view/create_user` |
| `users/{id}/` | GET/PATCH/DELETE | `iam.view/update/delete_user` |
| `users/{id}/change-password/` | POST | `iam.update_user` |
| `users/{id}/permissions/` | GET | `iam.view_user` |
| `users/search/` | GET | `iam.view_user` |

## Autenticación

### Login

**POST** `/api/iam/login/`

```json
{
  "username": "admin",
  "password": "contraseña"
}
```

Response: `{ "access": "...", "refresh": "...", "user": { ... } }`

### Refresh

**POST** `/api/iam/refresh/`

```json
{
  "refresh": "..."
}
```

Response: `{ "access": "...", "user": { ... } }`

## Usuarios (`/api/iam/users/`)

### Crear

**POST** `/api/iam/users/`

```json
{
  "document_number": "1234567890",
  "names": "Juan",
  "last_names": "Pérez",
  "email": "juan@example.com",
  "password": "contraseña123",
  "role_id": 1
}
```

El usuario se crea automáticamente con Person asociada y el rol asignado.

### Cambiar Contraseña

**POST** `/api/iam/users/{id}/change-password/`

```json
{
  "new_password": "nueva_contraseña"
}
```
