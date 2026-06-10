# Módulo `people` — Gestión de Personas — Estructura

## Árbol de archivos

```
people/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # Router: persons, document-types
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── person.py               # Person (documento, nombres, email, birth_date, género, full_name, age)
│   └── document_type.py        # DocumentType (code unique: CC, CE, PP, RC, TI, NIT)
│
├── repositories/
│   ├── __init__.py
│   ├── person_repository.py    # PersonRepository (+ search_by_document)
│   └── document_type_repository.py
│
├── services/
│   ├── __init__.py
│   └── person_service.py       # PersonService (create_with_user, create_student)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # PersonSerializer (full_name, age readonly), DocumentTypeSerializer
│   ├── views.py                # PersonViewSet, DocumentTypeViewSet
│   └── urls.py
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_permissions.py
    └── test_models.py
```

## Serializers

| Serializer | Campos readonly |
|------------|-----------------|
| `PersonSerializer` | `full_name`, `age`, `document_type_name` |
| `DocumentTypeSerializer` | — |

## Workflow

```
PersonService.create_person(document_number, names, last_names, ...) → Person.create()
    ↓
UserService.create_user(person=person, ...) → User.create() — en módulo iam
    ↓
StudentService.create_student(person=person, ...) → Student.create() — en módulo students
```

## Guía de imports

```python
from apps.people.models import Person, DocumentType
from apps.people.services.person_service import PersonService
from apps.people.api.serializers import PersonSerializer, DocumentTypeSerializer
from apps.people.api.views import PersonViewSet, DocumentTypeViewSet
```
