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
| `document-types/` | GET | `people.view_document_type` |
| `document-types/` | POST | `people.create_document_type` |
| `document-types/{id}/` | GET | `people.view_document_type` |
| `document-types/{id}/` | PATCH | `people.update_document_type` |
| `document-types/{id}/` | DELETE | `people.delete_document_type` |

## Personas (`/api/people/persons/`)

### Listar

**GET** `/api/people/persons/`

### Crear

**POST** `/api/people/persons/`

```json
{
  "document_type": 1,
  "document_number": "1234567890",
  "names": "Juan",
  "last_names": "Pérez",
  "email": "juan@example.com",
  "birth_date": "2000-01-15"
}
```

Response incluye `full_name` y `age` como campos de solo lectura.

## Tipos de Documento (`/api/people/document-types/`)

### Crear

**POST** `/api/people/document-types/`

```json
{
  "code": "CC",
  "name": "Cédula de Ciudadanía"
}
```
