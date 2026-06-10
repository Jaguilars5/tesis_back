# Módulo `people` — Gestión de Personas

> Gestión de personas físicas y sus tipos de documento. Es la base para estudiantes, docentes, representantes y cualquier actor del sistema.

## Modelos

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `DocumentType` | Catálogo de tipos de documento de identidad | `code` (unique: CC, CE, PP, RC, TI, NIT), `name` |
| `Person` | Persona física con datos personales | `document_type` (FK), `document_number` (unique), `names`, `last_names`, `email`, `phone`, `birth_date`, `gender`, `address`, `full_name` (property), `age` (property) |

## API

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| GET | `/api/people/persons/` | Listar personas | `people.view_person` |
| POST | `/api/people/persons/` | Crear persona | `people.create_person` |
| GET | `/api/people/persons/{id}/` | Obtener persona | `people.view_person` |
| PATCH | `/api/people/persons/{id}/` | Actualizar persona | `people.update_person` |
| DELETE | `/api/people/persons/{id}/` | Eliminar persona | `people.delete_person` |
| GET | `/api/people/persons/search/?document_number=` | Buscar por documento | `people.view_person` |
| GET/POST | `/api/people/document-types/` | Listar/Crear tipos | `people.view/create_document_type` |
| GET/PATCH/DELETE | `/api/people/document-types/{id}/` | CRUD individual | `people.view/update/delete_document_type` |

## Respuestas Enriquecidas

Todas las respuestas siguen el formato `{"ok": true, "data": {...}, "msg": ""}`.

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
    "age": 25,
    "gender": "M",
    "address": "Av. Siempre Viva 123"
  },
  "msg": ""
}
```

Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Tests

```bash
python manage.py test apps.people --settings=config.settings.test
```

## Dependencias

- Ninguna (app base, otras apps dependen de Person)
