# API — Módulo IAM

Gestiona usuarios, roles, permisos y autenticación JWT.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Endpoints Públicos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `login/` | POST | Iniciar sesión (username + password) → JWT + datos de usuario |
| `refresh/` | POST | Refrescar access token usando refresh token |

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `users/` | GET/POST | `iam.view/create_user` |
| `users/{id}/` | GET/PUT/PATCH/DEL | `iam.view/update/delete_user` |
| `users/{id}/change-password/` | POST | `iam.update_user` |
| `users/{id}/permissions/` | GET | `iam.view_user` |
| `users/search/` | GET | `iam.view_user` |
| `roles/` | GET/POST | `iam.view/create_role` |
| `roles/{id}/` | GET/PUT/PATCH/DEL | `iam.view/update/delete_role` |
| `roles/{id}/add-permission/` | POST | `iam.update_role` |
| `roles/{id}/remove-permission/` | POST | `iam.update_role` |
| `roles/{id}/assign-permissions/` | POST | `iam.update_role` |
| `permissions/` | GET/POST | `iam.view/create_permission` |
| `permissions/{id}/` | GET/PUT/PATCH/DEL | `iam.view/update/delete_permission` |
| `permissions/bulk-create/` | POST | `iam.create_permission` |
| `permissions/by-module/` | GET | `iam.view_permission` |

---

## Autenticación

### POST — Login

**POST** `/api/iam/login/`

```json
{"username": "admin", "password": "contraseña"}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "admin",
    "dni": "1234567890",
    "names": "Admin",
    "last_names": "Sistema",
    "email": "admin@example.com",
    "role": "ADMIN",
    "role_id": 1,
    "is_active": true,
    "permissions": ["grading.view_note", "..."]
  }
}
```

### POST — Refresh Token

**POST** `/api/iam/refresh/`

```json
{"refresh": "eyJhbGciOiJIUzI1NiIs..."}
```

---

## Usuarios (`/api/iam/users/`)

### GET — Listar

Response incluye `username`, `dni`, `names`, `last_names`, `email`, `role` (string code), `is_active`, `created_at`.

### POST — Crear usuario

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

Crea automáticamente Person + User + UserRole.

### POST — Cambiar contraseña

**POST** `/api/iam/users/{id}/change-password/`

```json
{"new_password": "nueva_contraseña"}
```

### GET — Buscar

**GET** `/api/iam/users/search/?q=Juan`

---

## Roles (`/api/iam/roles/`)

### GET — Listar

Response: `id`, `name`, `description`, `is_active`, `created_at`.

### POST — Crear rol

```json
{"name": "Coordinador", "code": "COORDINADOR", "description": "Coordinador académico"}
```

### POST — Asignar permiso a rol

**POST** `/api/iam/roles/{id}/add-permission/`

```json
{"permission_code": "grading.view_note"}
```

Espera `permission_code` (string), no `permission_id`.

### POST — Remover permiso

**POST** `/api/iam/roles/{id}/remove-permission/`

```json
{"permission_code": "grading.view_note"}
```

### POST — Asignar múltiples permisos

**POST** `/api/iam/roles/{id}/assign-permissions/`

```json
{"permission_codes": ["grading.view_note", "grading.create_note"]}
```

Espera `permission_codes` (lista de strings), no `permission_ids`.

---

## Permisos (`/api/iam/permissions/`)

### GET — Listar

Response: `id`, `code`, `module`, `description`, `created_at`, `updated_at`.

### POST — Crear

```json
{"code": "grading.view_note", "module": "grading", "description": "Ver notas"}
```

### POST — Bulk Create

**POST** `/api/iam/permissions/bulk-create/`

```json
{
  "permissions": [
    {"code": "students.view_enrollment", "module": "students", "description": "Ver"},
    {"code": "students.create_enrollment", "module": "students", "description": "Crear"}
  ]
}
```

### GET — Por módulo

**GET** `/api/iam/permissions/by-module/?module=grading`

Requiere `?module=` query param.
