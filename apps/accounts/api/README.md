# API - Módulo Accounts

---

## Formato de Respuesta

```
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Autenticación

Header:

```
Authorization: Bearer <access_token>
```

---

## Permisos

Todos los endpoints (excepto login y refresh) requieren permisos específicos:

| ViewSet | Acción | Permiso |
|---------|--------|---------|
| User | list, retrieve, search, permissions | `accounts.view_user` |
| User | create | `accounts.create_user` |
| User | update, change_password, grant_permission, revoke_permission | `accounts.update_user` |
| User | destroy | `accounts.delete_user` |
| Role | list, retrieve | `accounts.view_role` |
| Role | create | `accounts.create_role` |
| Role | update, add_permission, remove_permission, assign_permissions | `accounts.update_role` |
| Role | destroy | `accounts.delete_role` |
| Permission | list, retrieve, by_module | `accounts.view_permission` |
| Permission | create, bulk_create | `accounts.create_permission` |
| Permission | update | `accounts.update_permission` |
| Permission | destroy | `accounts.delete_permission` |

---

# Login

POST /api/accounts/login/

Request:

```
{
  "email": "admin@test.com",
  "password": "123456"
}
```

Response:

```
{
  "access": "token",
  "refresh": "token",
  "user": {
    "id": 1,
    "dni": "1234567890",
    "names": "Admin",
    "last_names": "Test",
    "email": "admin@test.com",
    "role": "Administrador",
    "role_id": 1,
    "institution": "Institución Ejemplo",
    "institution_id": 1,
    "active": true
  }
}
```

---

# Refresh

POST /api/accounts/refresh/

Request:

```
{
  "refresh": "token"
}
```

Response:

```
{
  "access": "token",
  "user": {
    "id": 1,
    "dni": "1234567890",
    "names": "Admin",
    "last_names": "Test",
    "email": "admin@test.com",
    "role": "Administrador",
    "role_id": 1,
    "institution": "Institución Ejemplo",
    "institution_id": 1,
    "active": true
  }
}
```

---

# Crear usuario

POST /api/accounts/users/

Request:

```
{
  "dni": "1234567890",
  "names": "Juan",
  "last_names": "Pérez",
  "email": "juan@test.com",
  "password": "123456",
  "role_id": 1,
  "institution_id": 1
}
```

Response:

```
{
  "ok": true,
  "data": {
    "id": 1,
    "email": "juan@test.com"
  },
  "msg": ""
}
```

---

# Listar usuarios

GET /api/accounts/users/

Response:

```
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "email": "admin@test.com"
    }
  ],
  "msg": ""
}
```

---

# Obtener usuario

GET /api/accounts/users/{id}/

Response:

```
{
  "ok": true,
  "data": {
    "id": 1,
    "email": "admin@test.com"
  },
  "msg": ""
}
```

---

# Actualizar usuario

PUT /api/accounts/users/{id}/

Request:

```
{
  "names": "Nuevo Nombre"
}
```

Response:

```
{
  "ok": true,
  "data": {
    "id": 1,
    "names": "Nuevo Nombre"
  },
  "msg": ""
}
```

---

# Eliminar usuario

DELETE /api/accounts/users/{id}/

Response:

```
{
  "ok": true,
  "data": {
    "id": 1,
    "active": false
  },
  "msg": ""
}
```

---

# Cambiar contraseña

POST /api/accounts/users/{id}/change-password/

Request:

```
{
  "new_password": "newpass123"
}
```

Response:

```
{
  "ok": true,
  "data": {},
  "msg": "Contraseña actualizada"
}
```

---

# Conceder permiso

POST /api/accounts/users/{id}/grant-permission/

Request:

```
{
  "permission_codename": "grading.view"
}
```

Response:

```
{
  "ok": true,
  "data": {
    "granted": true
  },
  "msg": ""
}
```

---

# Revocar permiso

POST /api/accounts/users/{id}/revoke-permission/

Request:

```
{
  "permission_codename": "grading.view"
}
```

Response:

```
{
  "ok": true,
  "data": {
    "granted": false
  },
  "msg": ""
}
```
