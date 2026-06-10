# Estructura Técnica: Módulo `institutions`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo institucional.

## Árbol de Directorios

```text
institutions/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Serializers (SchoolYear, AcademicLevel, AcademicSubnivel, AcademicGrade, Section)
│   ├── views.py          # ViewSets (SchoolYear, AcademicLevel, AcademicSubnivel, AcademicGrade, Section)
│   └── urls.py           # Rutas vía DefaultRouter (5 ViewSets)
├── models/               # Capa de Datos (Entidades)
│   ├── __init__.py
│   ├── school_year.py      # Años escolares
│   ├── academic_level.py   # Niveles académicos
│   ├── academic_sublevel.py# Subniveles académicos
│   ├── academic_grade.py   # Grados académicos
│   └── section.py          # Secciones (grado/paralelo)
├── repositories/         # Capa de Persistencia (Queries)
│   ├── __init__.py
│   ├── institution_repo.py
│   └── section_repository.py
├── services/             # Capa de Negocio (Orquestación)
│   ├── __init__.py
│   └── institution_service.py # Lógica de validaciones de fechas
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_repositories.py
    ├── test_services.py
    ├── test_api.py
    ├── test_api_gaps.py
    └── test_api_permissions.py
```

## API — Serializers

Los serializers del módulo exponen campos descriptivos adicionales para las ForeignKeys:

| Serializer                    | Campos enriquecidos                                           |
| ----------------------------- | ------------------------------------------------------------- |
| `SectionSerializer`           | `school_year_name` (source: `school_year.name`)               |
|                               | `academic_grade_name` (source: `academic_grade.name`)         |
| `AcademicSublevelSerializer`  | `academic_level_name` (source: `academic_level.name`)         |
| `AcademicGradeSerializer`     | `academic_level_name` (source: `academic_level.name`)         |

Estos campos son de solo lectura (`read_only=True`) y no afectan la creación/actualización de registros.

## Modelos Principales

### SchoolYear

Año escolar con fechas de inicio y fin, estado activo.



### AcademicLevel

Niveles académicos (Educación Inicial, EGB, BGU).

### AcademicSubnivel

Subniveles pedagógicos dentro de un nivel académico (Básica, Bachillerato, etc.)

### AcademicGrade

Grados dentro de un subnivel (1º EGB, 2º EGB, etc.). Vinculado a AcademicSubnivel (no directamente a AcademicLevel).

### Section

Representa un grado y paralelo específico. Vinculada a SchoolYear y AcademicGrade.

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
from apps.institutions.models import SchoolYear, AcademicLevel, AcademicSublevel, AcademicGrade, Section

# Importar repositorios
from apps.institutions.repositories.institution_repo import InstitutionRepository
```

### ❌ Prácticas a Evitar

```python
# Importar desde archivos internos específicos (rompe el encapsulamiento)
from apps.institutions.models.school_year import SchoolYear
```

## Responsabilidades de Capas

1.  **Models**: Definen el "qué" (entidades base del sistema).
2.  **Repositories**: Definen el "cómo buscar" (centralizan queries ORM).
3.  **Services**: Definen el "qué hacer" (validaciones complejas de fechas y capacidad).
4.  **API**: Exponen los recursos mediante ViewSets con `DefaultRouter` para estandarizar las respuestas (`ok`, `data`, `msg`).
