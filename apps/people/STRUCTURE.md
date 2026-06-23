# Módulo `people` — Gestión de Personas — Estructura

## Árbol de archivos

```
people/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py (persons, document-types)
├── README.md
│
├── domain/                     # VACÍO
├── signals/                    # VACÍO
├── tasks/                      # VACÍO
│
├── models/
│   ├── __init__.py             # 2 modelos exportados
│   ├── person.py               # Person (TimeStampedModel)
│   └── document_type.py        # DocumentType (TimeStampedModel)
│
├── repositories/
│   ├── __init__.py             # 2 repositorios exportados
│   ├── person_repo.py          # PersonRepository (NO hereda BaseRepository)
│   └── document_type_repository.py  # DocumentTypeRepository
│
├── services/
│   ├── __init__.py             # 2 servicios exportados
│   ├── person_service.py       # PersonService
│   └── document_type_service.py# DocumentTypeService
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers/
│   │   ├── __init__.py         # PersonSerializer, DocumentTypeSerializer
│   │   ├── person.py
│   │   └── document_type.py
│   ├── views/
│   │   ├── __init__.py         # PersonViewSet, DocumentTypeViewSet
│   │   └── views.py
│   ├── filters/                # VACÍO
│   ├── permissions/            # VACÍO
│   └── urls.py                 # Router: persons, document-types
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_permissions.py
    └── test_models.py
```

## Workflow

```
PersonService.create_person_with_user(person_data, password) → Person + User
PersonService.create_person_with_student(person_data, student_code) → Person + Student
```

## Guía de imports

```python
from apps.people.models import Person, DocumentType

from apps.people.repositories import PersonRepository, DocumentTypeRepository

from apps.people.services.person_service import PersonService

from apps.people.api.serializers import PersonSerializer, DocumentTypeSerializer
from apps.people.api.views import PersonViewSet, DocumentTypeViewSet
```
