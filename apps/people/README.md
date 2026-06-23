# Módulo `people` — Gestión de Personas

> Gestión de personas físicas y sus tipos de documento. Base para estudiantes, docentes, representantes y cualquier actor del sistema.

## Modelos (2)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `DocumentType` | Catálogo de tipos de documento | `code` (unique: CC, CE, PP, RC, TI, NIT), `name`, `is_active`. Ordenado por `name`. `db_table = "people_document_type"`. Hereda `TimeStampedModel` |
| `Person` | Persona física con datos personales | `document_type` (FK, nullable), `document_number` (unique), `names`, `last_names`, `birth_date`, `email`, `phone`, `is_active`. Properties: `get_full_name()`, `get_age()`. Hereda `TimeStampedModel` |

## Repositorios (2)

| Repositorio | Métodos adicionales | Nota |
|-------------|-------------------|------|
| `PersonRepository` | `get_all()`, `get_by_id()`, `get_by_document_number()`, `search()`, `get_by_email()`, `create()` | **No hereda `BaseRepository`** |
| `DocumentTypeRepository` | `get_all()` ordenado por `name` | Hereda `BaseRepository` |

## Servicios (2)

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `PersonService` | `create_person_with_user()`, `create_person_with_student()`, `search_person()` | Creación transaccional de Person + User o Person + Student |
| `DocumentTypeService` | `list_document_types()`, `get_document_type()`, `create_document_type()`, `update_document_type()`, `delete_document_type()` | CRUD de tipos de documento |

## API — Endpoints

| Método | Endpoint | ViewSet | Permiso |
|--------|----------|---------|---------|
| GET/POST | `/api/people/persons/` | PersonViewSet | `people.view/create_person` |
| GET/PUT/PATCH/DEL | `/api/people/persons/{id}/` | PersonViewSet | `people.view/update/delete_person` |
| GET/POST | `/api/people/document-types/` | DocumentTypeViewSet | `people.view/create_document_type` |
| GET/PUT/PATCH/DEL | `/api/people/document-types/{id}/` | DocumentTypeViewSet | `people.view/update/delete_document_type` |

> No existe endpoint `persons/search/` — no hay acción `search` definida en `PersonViewSet`.

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `PersonSerializer` | `full_name`, `age`, `id`, `created_at`, `updated_at` |
| `DocumentTypeSerializer` | — |

## Tests

```bash
python manage.py test apps.people --settings=config.settings.test
```
