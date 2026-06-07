# Estructura Técnica: Módulo `academic`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo académico.

## Árbol de Directorios

```text
academic/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Transformación de datos
│   ├── views.py          # ViewSets con StandardResponse
│   ├── filters.py        # Filtrado avanzado
│   └── urls.py           # Definición de rutas del módulo
├── models/               # Capa de Datos (Entidades)
│   ├── academic_period.py         # Períodos académicos
│   ├── subject.py                  # Materias
│   ├── subject_academic_config.py # Config de materia por grado
│   ├── subject_offering.py         # Oferta de materia en sección
│   ├── teacher_subject_section.py  # Asignación docente
│   ├── interdisciplinary_project.py  # Proyectos interdisciplinarios
│   └── subject_project.py          # Materias vinculadas a proyectos
├── repositories/         # Capa de Persistencia (Queries)
│   ├── academic_repo.py
│   └── interdisciplinary_project_repository.py
├── services/             # Capa de Negocio (Orquestación)
│   └── academic_service.py # Lógica de cálculos y validaciones
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_services.py
    ├── test_api.py
    └── test_api_gaps.py
```

## API — Serializers

Los serializers del módulo exponen campos descriptivos adicionales para las ForeignKeys:

| Serializer                           | Campos enriquecidos                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| `Academic_PeriodSerializer`          | `school_year_name` (source: `school_year.name`)                               |
| `Teacher_Subject_SectionSerializer`  | `user_name` (source: `user.person.get_full_name`)                             |
|                                      | `subject_offering_name` (source: `subject_offering.__str__`)                  |
| `SubjectAcademicConfigSerializer`    | `subject_name` (source: `subject.name`)                                       |
|                                      | `academic_grade_name` (source: `academic_grade.name`)                         |
| `SubjectOfferingSerializer`          | `school_year_name` (source: `school_year.name`)                               |
|                                      | `section_name` (source: `section.__str__`)                                    |
|                                      | `subject_academic_config_name` (source: `subject_academic_config.__str__`)    |
| `SubjectProjectSerializer`           | `interdisciplinary_project_title` (source: `interdisciplinary_project.title`) |
|                                      | `subject_offering_name` (source: `subject_offering.__str__`)                  |
| `InterdisciplinaryProjectSerializer` | `academic_period_name` (source: `academic_period.name`)                       |

Estos campos son de solo lectura (`read_only=True`) y no afectan la creación/actualización de registros.

## Modelos Principales

### Academic_Period

Períodos dentro de un año escolar (Quimestres, parciales, etc.)

### Subject

Asignaturas disponibles en el sistema.

### SubjectAcademicConfig

Vincula una materia a un nivel académico con parámetros pedagógicos (horas semanales, orden, etc.)

### SubjectOffering

Instancia de una materia en una sección para un año escolar específico.

### Teacher_Subject_Section

Vinculación entre un docente (User) y una oferta de materia.

### InterdisciplinaryProject

Proyectos que abarcan múltiples materias.

### SubjectProject

Asociación entre una materia y un proyecto interdisciplinario.

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** realize cálculos de promedios o normalización de notas directamente en los ViewSets. Estas operaciones deben residir exclusivamente en `AcademicService`.

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares y mantener el código limpio:

### ✅ Prácticas Correctas

```python
# Importar servicios
from apps.academic.services.academic_service import AcademicService

# Importar modelos (re-exportados en models/__init__.py)
from apps.academic.models import Subject, Academic_Period, SubjectOffering

# Importar repositorios
from apps.academic.repositories.academic_repo import SubjectRepository
```

### ❌ Prácticas a Evitar

```python
# Importar desde archivos internos específicos
from apps.academic.models.subject import Subject

# Realizar cálculos complejos fuera del service
promedio = sum(notas) / len(notas)
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura y restricciones (ej: `capacity > 0`).
2.  **Repositories**: Centralizan las consultas (ej: `get_active_subjects()`).
3.  **Services**: Orquestan la lógica (ej: `record_student_note` valida rangos y normaliza).
4.  **API**: Exponen los recursos mediante ViewSets que heredan de patrones base para estandarizar las respuestas (`ok`, `data`, `msg`).
