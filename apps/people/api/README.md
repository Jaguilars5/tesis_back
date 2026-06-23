# API — Módulo People

Gestiona personas físicas y tipos de documento del sistema.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `persons/` | GET | `people.view_person` |
| `persons/` | POST | `people.create_person` |
| `persons/{id}/` | GET | `people.view_person` |
| `persons/{id}/` | PUT/PATCH | `people.update_person` |
| `persons/{id}/` | DELETE | `people.delete_person` |
| `document-types/` | GET | `people.view_document_type` |
| `document-types/` | POST | `people.create_document_type` |
| `document-types/{id}/` | GET/PUT/PATCH/DEL | `people.view/update/delete_document_type` |

---

## Personas (`/api/people/persons/`)

### GET — Listar

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "document_type": 1,
      "document_number": "1234567890",
      "names": "Juan",
      "last_names": "Pérez",
      "full_name": "Juan Pérez",
      "email": "juan@example.com",
      "phone": "0987654321",
      "age": 25
    }
  ]
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

---

## Tipos de Documento (`/api/people/document-types/`)

### GET — Listar

```json
{"id": 1, "code": "CC", "name": "Cédula de Ciudadanía"}
{"id": 2, "code": "CE", "name": "Cédula de Extranjería"}
{"id": 3, "code": "PP", "name": "Pasaporte"}
```

### POST — Crear

```json
{"code": "DNI", "name": "Documento Nacional de Identidad"}
```
