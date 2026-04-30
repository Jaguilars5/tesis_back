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
  "refresh": "token"
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
  "access": "token"
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
