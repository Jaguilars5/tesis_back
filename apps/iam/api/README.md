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
| `users/` | GET/POST | `iam.view/create_user` |
| `users/{id}/` | GET/PATCH/DELETE | `iam.view/update/delete_user` |
| `users/{id}/change-password/` | POST | `iam.update_user` |
| `users/{id}/permissions/` | GET | `iam.view_user` |
| `users/search/` | GET | `iam.view_user` |
| `roles/` | GET/POST | `iam.view/create_role` |
| `roles/{id}/` | GET/PATCH/DELETE | `iam.view/update/delete_role` |
| `roles/{id}/add-permission/` | POST | `iam.update_role` |
| `roles/{id}/remove-permission/` | POST | `iam.update_role` |
| `roles/{id}/assign-permissions/` | POST | `iam.update_role` |
| `permissions/` | GET/POST | `iam.view/create_permission` |
| `permissions/{id}/` | PATCH/DELETE | `iam.update/delete_permission` |
| `permissions/bulk-create/` | POST | `iam.create_permission` |
| `permissions/by-module/` | GET | `iam.view_permission` |

---

## Autenticación

### POST — Login

**POST** `/api/iam/login/`

```json
{
  "username": "admin",
  "password": "contraseña"
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
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
      "permissions": ["grading.view_note", "grading.create_note", "..."]
    }
  },
  "msg": ""
}
```

### POST — Refresh Token

**POST** `/api/iam/refresh/`

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "user": { "...datos de usuario..." }
  },
  "msg": ""
}
```

---

## Usuarios (`/api/iam/users/`)

### GET — Listar usuarios

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "username": "juan@example.com",
        "dni": "1234567890",
        "names": "Juan",
        "last_names": "Pérez",
        "email": "juan@example.com",
        "role": "DOCENTE",
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z"
      }
    ]
  },
  "msg": ""
}
```

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

El usuario se crea automáticamente con Person asociada y el rol asignado.

### POST — Cambiar Contraseña

**POST** `/api/iam/users/{id}/change-password/`

```json
{
  "new_password": "nueva_contraseña"
}
```

### GET — Buscar usuarios

**GET** `/api/iam/users/search/?q=Juan`

---

## Roles (`/api/iam/roles/`)

### GET — Listar roles

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 3,
    "results": [
      {"id": 1, "name": "Admin", "code": "ADMIN", "description": "Acceso total", "is_active": true},
      {"id": 2, "name": "Docente", "code": "DOCENTE", "description": "Profesor", "is_active": true},
      {"id": 3, "name": "Estudiante", "code": "ESTUDIANTE", "description": "Alumno", "is_active": true}
    ]
  },
  "msg": ""
}
```

### POST — Crear rol

```json
{
  "name": "Coordinador",
  "code": "COORDINADOR",
  "description": "Coordinador académico"
}
```

### POST — Asignar permiso a rol

**POST** `/api/iam/roles/{id}/add-permission/`

```json
{
  "permission_id": 5
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "role": 2,
    "permission": {"id": 5, "code": "grading.view_note", "module": "grading"},
    "created_at": "2025-06-08T12:00:00Z"
  },
  "msg": ""
}
```

### POST — Asignar múltiples permisos

**POST** `/api/iam/roles/{id}/assign-permissions/`

```json
{
  "permission_ids": [1, 2, 3, 4, 5]
}
```

---

## Permisos (`/api/iam/permissions/`)

### GET — Listar permisos

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 50,
    "results": [
      {"id": 1, "code": "grading.view_note", "module": "grading", "description": "Ver notas"},
      {"id": 2, "code": "grading.create_note", "module": "grading", "description": "Crear notas"}
    ]
  },
  "msg": ""
}
```

### POST — Crear permiso

```json
{
  "code": "grading.view_note",
  "module": "grading",
  "description": "Permite visualizar notas de actividades evaluativas"
}
```

### POST — Bulk Create

**POST** `/api/iam/permissions/bulk-create/`

```json
{
  "permissions": [
    {"code": "students.view_enrollment", "module": "students", "description": "Ver matrículas"},
    {"code": "students.create_enrollment", "module": "students", "description": "Crear matrículas"}
  ]
}
```

### GET — Agrupados por módulo

**GET** `/api/iam/permissions/by-module/`

```json
{
  "ok": true,
  "data": {
    "grading": [
      {"id": 1, "code": "grading.view_note", "description": "Ver notas"},
      {"id": 2, "code": "grading.create_note", "description": "Crear notas"}
    ],
    "students": [
      {"id": 3, "code": "students.view_enrollment", "description": "Ver matrículas"}
    ]
  },
  "msg": ""
}
```
