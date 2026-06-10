# API - Módulo People

Esta API gestiona personas físicas y tipos de documento del sistema.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `persons/` | GET | `people.view_person` |
| `persons/` | POST | `people.create_person` |
| `persons/{id}/` | GET | `people.view_person` |
| `persons/{id}/` | PATCH | `people.update_person` |
| `persons/{id}/` | DELETE | `people.delete_person` |
| `document-types/` | GET/POST | `people.view/create_document_type` |
| `document-types/{id}/` | GET/PATCH/DELETE | `people.view/update/delete_document_type` |

---

## Personas (`/api/people/persons/`)

### GET — Listar personas

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "full_name": "Juan Pérez",
        "document_type_name": "Cédula de Ciudadanía",
        "document_number": "1234567890",
        "email": "juan@example.com",
        "phone": "0987654321",
        "age": 25
      }
    ]
  },
  "msg": ""
}
```

### POST — Crear persona

```json
{
  "document_type": 1,
  "document_number": "1234567890",
  "names": "Juan",
  "last_names": "Pérez",
  "email": "juan@example.com",
  "phone": "0987654321",
  "birth_date": "2000-01-15"
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "document_type": 1,
    "document_type_name": "Cédula de Ciudadanía",
    "document_number": "1234567890",
    "names": "Juan",
    "last_names": "Pérez",
    "full_name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "0987654321",
    "birth_date": "2000-01-15",
    "age": 25
  },
  "msg": ""
}
```

### PATCH — Actualizar persona

**PATCH** `/api/people/persons/1/`

```json
{
  "phone": "0999999999",
  "email": "juan.nuevo@example.com"
}
```

### DELETE — Eliminar persona

**DELETE** `/api/people/persons/1/`

**Response (204 No Content):**
```json
{
  "ok": true,
  "data": null,
  "msg": "Persona eliminada exitosamente"
}
```

---

## Tipos de Documento (`/api/people/document-types/`)

### GET — Listar

**Response (200 OK):**
```json
{
  "ok": true,
  "data": [
    {"id": 1, "code": "CC", "name": "Cédula de Ciudadanía"},
    {"id": 2, "code": "CE", "name": "Cédula de Extranjería"},
    {"id": 3, "code": "PP", "name": "Pasaporte"},
    {"id": 4, "code": "RC", "name": "Registro Civil"},
    {"id": 5, "code": "TI", "name": "Tarjeta de Identidad"},
    {"id": 6, "code": "NIT", "name": "NIT"}
  ],
  "msg": ""
}
```

### POST — Crear tipo de documento

```json
{
  "code": "DNI",
  "name": "Documento Nacional de Identidad"
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "data": {"id": 7, "code": "DNI", "name": "Documento Nacional de Identidad"},
  "msg": ""
}
```
