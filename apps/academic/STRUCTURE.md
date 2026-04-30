# Estructura Técnica: Módulo `academic`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo académico.

## Árbol de Directorios

```text
academic/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Transformación de datos (8+ serializers)
│   ├── views.py          # ViewSets con StandardResponse
│   ├── filters.py        # Filtrado avanzado (section, subject, etc.)
│   └── urls.py           # Definición de rutas del módulo
├── models/               # Capa de Datos (Entidades)
│   ├── config_academic.py
│   ├── section.py
│   ├── subject.py
│   ├── student_note.py
│   └── ... (8 modelos en total)
├── repositories/         # Capa de Persistencia (Queries)
│   └── academic_repo.py  # Repositorios centralizados por entidad
├── services/             # Capa de Negocio (Orquestación)
│   └── academic_service.py # Lógica de cálculos y validaciones
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_services.py
    └── test_api.py
```

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** realice cálculos de promedios o normalización de notas directamente en los ViewSets. Estas operaciones deben residir exclusivamente en `AcademicService` para garantizar la consistencia en todos los puntos de entrada (API, Admin, Scripts).

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares y mantener el código limpio:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.academic.services.academic_service import AcademicService

# Importar modelos (re-exportados en models/__init__.py)
from apps.academic.models import Section, Subject, StudentNote

# Importar repositorios
from apps.academic.repositories.academic_repo import SectionRepository
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos
from apps.academic.models.section import Section 

# Realizar cálculos complejos fuera del service
promedio = sum(notas) / len(notas) # Debería estar en AcademicService
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura y restricciones (ej: `capacity > 0`).
2.  **Repositories**: Centralizan las consultas (ej: `get_active_sections()`).
3.  **Services**: Orquestan la lógica (ej: `record_student_note` valida rangos y normaliza).
4.  **API**: Exponen los recursos mediante ViewSets que heredan de `BaseAcademicViewSet` para estandarizar las respuestas (`ok`, `data`, `msg`).
