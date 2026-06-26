# Módulo `academic` — Estructura

## Árbol de archivos

```
academic/
├── __init__.py                 # ACADEMIC_APPS list
├── urls.py                     # → api/urls.py
├── README.md
├── api/                        # Shared API layer
│   ├── __init__.py
│   ├── base.py                 # BaseAcademicViewSet (SoftDestroyMixin, get action)
│   ├── routers.py              # AcademicRouter (custom DefaultRouter)
│   ├── urls.py                 # Aggregates all sub-app urls
│   └── README.md
│
├── subject/                    # Bounded context #1
│   ├── __init__.py
│   ├── apps.py, admin.py, permissions.py, urls.py
│   ├── api/
│   │   ├── __init__.py, views.py, filters.py
│   ├── application/
│   │   ├── __init__.py, serializers.py, validators.py
│   ├── domain/
│   │   ├── __init__.py, repositories.py, services.py
│   ├── infrastructure/
│   │   ├── __init__.py, models.py, repositories.py
│   ├── migrations/
│   └── tests/
│       ├── __init__.py, test_api.py, test_models.py, test_repositories.py
│
├── period_type/                # Bounded context #2
│   ├── __init__.py
│   ├── apps.py, admin.py, permissions.py, urls.py
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── migrations/
│   └── tests/
│       ├── test_api.py, test_models.py
│
├── academic_period/            # Bounded context #3
│   ├── __init__.py
│   ├── apps.py, admin.py, permissions.py, urls.py
│   ├── constants.py            # DEFAULT_PERIOD_TYPE_CODE
│   ├── types.py                # TypedDicts
│   ├── signals.py              # Placeholder
│   ├── api/
│   │   ├── views.py, filters.py
│   ├── application/
│   │   ├── serializers.py, validators.py
│   ├── domain/
│   │   ├── entities.py         # AcademicPeriodEntity (dataclass)
│   │   ├── repositories.py, services.py
│   ├── infrastructure/
│   │   ├── models.py, mappers.py, repositories.py
│   ├── migrations/
│   └── tests/
│       └── test_api.py
│
├── subject_academic_config/    # Bounded context #4
│   ├── __init__.py
│   ├── apps.py, admin.py, permissions.py, urls.py
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── migrations/
│   └── tests/
│       └── test_api.py
│
├── subject_offering/           # Bounded context #5
│   ├── __init__.py
│   ├── apps.py, admin.py, permissions.py, urls.py
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── migrations/
│   └── tests/
│       └── test_api.py
│
├── teacher_subject_section/    # Bounded context #6
│   ├── __init__.py
│   ├── apps.py, admin.py, permissions.py, urls.py
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── migrations/
│   └── tests/
│       └── test_api.py
│
└── class_schedule/             # Bounded context #7
    ├── __init__.py
    ├── apps.py, admin.py, permissions.py, urls.py
    ├── api/
    │   ├── views.py            # + by_section, my_schedule, my_today actions
    │   └── filters.py
    ├── application/
    │   ├── serializers.py, validators.py
    ├── domain/
    │   ├── repositories.py, services.py
    ├── infrastructure/
    │   ├── models.py           # ClassSchedule + DayOfWeekChoices
    │   └── repositories.py
    ├── migrations/
    └── tests/
        └── test_api.py
```

## Capas por sub-app

| Capa | Ubicación | Responsabilidad |
|------|-----------|----------------|
| `api/` | `views.py`, `filters.py` | DRF ViewSet con action_permissions, filtros, búsqueda |
| `application/` | `serializers.py`, `validators.py` | Serialización + validación pura |
| `domain/` | `services.py`, `repositories.py` (ABC) | Lógica de negocio + interfaz repositorio |
| `infrastructure/` | `models.py`, `repositories.py` | Implementación concreta Django ORM |

## Serializers (7)

| Serializer | Modelo | Campos readonly adicionales |
|------------|--------|---------------------------|
| `SubjectSerializer` | Subject | `created_at`, `updated_at` |
| `AcademicPeriodSerializer` | AcademicPeriod | `school_year_name`, `period_type_name` |
| `PeriodTypeSerializer` | PeriodType | `created_at`, `updated_at` |
| `TeacherSubjectSectionSerializer` | TeacherSubjectSection | `user_name`, `subject_offering_name`, `subject_offering_school_year`, `subject_offering_school_year_name`, `subject_offering_section`, `subject_offering_section_name`, `subject_offering_academic_grade`, `subject_offering_academic_grade_name`, `subject_offering_subject`, `subject_offering_subject_name`, `subject_offering_config`, `subject_offering_config_name` |
| `SubjectAcademicConfigSerializer` | SubjectAcademicConfig | `subject_name`, `academic_grade_name` |
| `SubjectOfferingSerializer` | SubjectOffering | `school_year`, `school_year_name`, `section_name`, `subject_academic_config_name` |
| `ClassScheduleSerializer` | ClassSchedule | `subject_offering_name`, `day_of_week_name`, `section_name`, `section_id`, `subject_name`, `subject_id`, `teacher_name`, `teacher_id` |

## ViewSets (7 registrados vía AcademicRouter)

| ViewSet | Endpoint (plural) | Extra actions |
|---------|-------------------|---------------|
| `SubjectViewSet` | `subjects/` | `soft-delete` |
| `AcademicPeriodViewSet` | `academic-periods/` | `soft-delete` |
| `PeriodTypeViewSet` | `period-types/` | `soft-delete` |
| `SubjectAcademicConfigViewSet` | `subject-academic-configs/` | `soft-delete` |
| `SubjectOfferingViewSet` | `subject-offerings/` | `soft-delete` |
| `TeacherSubjectSectionViewSet` | `teacher-subject-sections/` | `soft-delete` |
| `ClassScheduleViewSet` | `class-schedules/` | `soft-delete`, `by-section`, `my-schedule`, `my-today` |

Todos heredan de `BaseAcademicViewSet` que incluye `SoftDestroyMixin` + acción `soft-delete` con confirmación explícita (`{"confirm": true}`).

## BaseAcademicViewSet

Ubicación: `api/base.py`

```python
class BaseAcademicViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    SoftDestroyMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination
```

- Reemplaza `retrieve` por `get` (compatible con DRF `retrieve` → `get` mapping en `AcademicRouter`)
- `create()` y `update()` con manejo de errores vía `ValidationError`

## AcademicRouter

Ubicación: `api/routers.py`

Custom `DefaultRouter` con routing explícito:
- `GET {prefix}/` → `list`
- `POST {prefix}/` → `create`
- `GET {prefix}/{lookup}/` → `get` (no `retrieve`)
- `PUT {prefix}/{lookup}/` → `update`
- `PATCH {prefix}/{lookup}/` → `partial_update`
- `DELETE {prefix}/{lookup}/` → `destroy`
- `POST {prefix}/{lookup}/soft-delete/` → `soft_delete` (DynamicRoute)
- `GET {prefix}/by-section/` → `by_section` (DynamicRoute, detail=False)
- `GET {prefix}/my-schedule/` → `my_schedule` (DynamicRoute, detail=False)
- `GET {prefix}/my-today/` → `my_today` (DynamicRoute, detail=False)

## Workflow

```
SchoolYear
  └─ AcademicPeriod (varios por año, year_weight para nota anual)
      └─ EvaluationBlock (en grading) ← SubjectOffering
          └─ SubjectAcademicConfig ← Subject + AcademicGrade
              └─ Subject

Section (pertenece a SchoolYear via school_year FK)
  └─ SubjectOffering (unique: section + subject_academic_config)
      ├─ TeacherSubjectSection (unique: user + offering)
      └─ ClassSchedule (unique: teacher_subject_section + day_of_week + start_time)
```

## Guía de imports

```python
# Modelos
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.class_schedule.infrastructure.models import ClassSchedule, DayOfWeekChoices

# Repositorios
from apps.academic.subject.infrastructure.repositories import SubjectRepository
from apps.academic.class_schedule.infrastructure.repositories import ClassScheduleRepository

# Servicios
from apps.academic.subject.domain.services import SubjectService
from apps.academic.class_schedule.domain.services import ClassScheduleService

# API
from apps.academic.subject.application.serializers import SubjectSerializer
from apps.academic.subject.api.views import SubjectViewSet

# Permisos
from apps.academic.subject.permissions import ACTION_PERMISSIONS as SUBJECT_PERMISSIONS
```
