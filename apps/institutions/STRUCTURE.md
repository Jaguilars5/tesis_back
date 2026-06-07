# Estructura Técnica: Módulo `institutions`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo institucional.

## Árbol de Directorios

```text
institutions/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Serializers (SchoolYear, DocumentType, AcademicLevel, AcademicGrade)
│   ├── views.py          # ViewSets (SchoolYear, DocumentType, AcademicLevel, AcademicGrade)
│   └── urls.py           # Rutas vía DefaultRouter
├── models/               # Capa de Datos (Entidades)
│   ├── school_year.py      # Años escolares
│   ├── document_type.py   # Tipos de documento
│   ├── academic_level.py  # Niveles académicos
│   ├── academic_grade.py  # Grados académicos
│   └── section.py         # Secciones (grado/paralelo)
├── repositories/         # Capa de Persistencia (Queries)
│   ├── institution_repo.py
│   └── section_repository.py
├── services/             # Capa de Negocio (Orquestación)
│   └── institution_service.py # Lógica de validaciones de fechas
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_services.py
    ├── test_api.py
    └── test_api_gaps.py
```

## API — Serializers

Los serializers del módulo exponen campos descriptivos adicionales para las ForeignKeys:

| Serializer                | Campos enriquecidos                                   |
| ------------------------- | ----------------------------------------------------- |
| `SectionSerializer`       | `school_year_name` (source: `school_year.name`)       |
|                           | `academic_grade_name` (source: `academic_grade.name`) |
| `AcademicGradeSerializer` | `academic_level_name` (source: `academic_level.name`) |

Estos campos son de solo lectura (`read_only=True`) y no afectan la creación/actualización de registros.

## Modelos Principales

### School_Year

Año escolar con fechas de inicio y fin, estado activo.

### DocumentType

Catálogo de tipos de documento (cédula, pasaporte, etc.)

### AcademicLevel

Niveles académicos (Educación Inicial, EGB, BGU).

### AcademicGrade

Grados dentro de un nivel (1º EGB, 2º EGB, etc.)

### Section

Representa un grado y paralelo específico. Vinculada a School_Year, AcademicLevel y AcademicGrade.

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** ignore las validaciones de fechas en la creación de años escolares. Utilice siempre `InstitutionService.create_school_year` para evitar solapamientos cronológicos que podrían corromper la lógica de otros módulos (como `academic`).

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares:

### ✅ Prácticas Correctas

```python
# Importar servicios
from apps.institutions.services.institution_service import InstitutionService

# Importar modelos (re-exportados en models/__init__.py)
from apps.institutions.models import School_Year, AcademicLevel, AcademicGrade, Section

# Importar repositorios
from apps.institutions.repositories.institution_repo import InstitutionRepository
```

### ❌ Prácticas a Evitar

```python
# Importar desde archivos internos específicos (rompe el encapsulamiento)
from apps.institutions.models.school_year import School_Year
```

## Responsabilidades de Capas

1.  **Models**: Definen el "qué" (entidades base del sistema).
2.  **Repositories**: Definen el "cómo buscar" (centralizan queries ORM).
3.  **Services**: Definen el "qué hacer" (validaciones complejas de fechas y capacidad).
4.  **API**: Exponen los recursos mediante ViewSets con `DefaultRouter` para estandarizar las respuestas (`ok`, `data`, `msg`).
