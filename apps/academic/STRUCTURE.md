# Módulo `academic` — Estructura

## Árbol de archivos

```
academic/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py
├── README.md
│
├── models/
│   ├── __init__.py             # 10 modelos exportados
│   ├── subject.py              # Subject
│   ├── academic_period.py      # AcademicPeriod (+ parent_period self FK)
│   ├── period_type.py          # PeriodType (REGULAR, SUPLETORIO, REFUERZO)
│   ├── subject_academic_config.py  # SubjectAcademicConfig
│   ├── subject_offering.py     # SubjectOffering
│   ├── teacher_subject_section.py  # TeacherSubjectSection
│   ├── interdisciplinary_project.py # InterdisciplinaryProject (+ M2M a SubjectOffering)
│   ├── subject_project.py      # SubjectProject (+ responsible_teacher)
│   ├── day_of_week.py          # DayOfWeek (catálogo 1-7)
│   └── class_schedule.py       # ClassSchedule (FK a DayOfWeek)
│
├── repositories/
│   ├── __init__.py             # 7 repositorios exportados
│   ├── academic_repo.py        # SubjectRepository, AcademicPeriodRepository, PeriodTypeRepository,
│                               # TeacherSubjectSectionRepository, SubjectAcademicConfigRepository,
│                               # SubjectOfferingRepository
│   └── interdisciplinary_project_repository.py  # InterdisciplinaryProjectRepository, SubjectProjectRepository
│
├── services/
│   ├── __init__.py
│   └── academic_service.py     # AcademicService
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 10 serializers (Subject, AcademicPeriod, TeacherSubjectSection,
│                               #   SubjectAcademicConfig, SubjectOffering, SubjectProject,
│                               #   DayOfWeek, ClassSchedule, PeriodType, InterdisciplinaryProject)
│   ├── views.py                # 8 ViewSets (Subject, AcademicPeriod, TeacherSubjectSection,
│                               #   SubjectAcademicConfig, SubjectOffering, InterdisciplinaryProject,
│                               #   SubjectProject, PeriodType)
│   ├── filters.py              # Filtros avanzados
│   └── urls.py                 # Router con 8 registros
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_gaps.py
    ├── test_api_permissions.py
    ├── test_models.py
    ├── test_repositories.py
    └── test_services.py
```

## Serializers (10)

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `SubjectSerializer` | Subject | — |
| `AcademicPeriodSerializer` | AcademicPeriod | `school_year_name` |
| `TeacherSubjectSectionSerializer` | TeacherSubjectSection | `user_name`, `subject_offering_name` |
| `SubjectAcademicConfigSerializer` | SubjectAcademicConfig | `subject_name`, `academic_grade_name` |
| `SubjectOfferingSerializer` | SubjectOffering | `school_year_name`, `section_name`, `subject_academic_config_name` |
| `SubjectProjectSerializer` | SubjectProject | `interdisciplinary_project_title`, `subject_offering_name` |
| `InterdisciplinaryProjectSerializer` | InterdisciplinaryProject | `academic_period_name`, `subject_projects` (anidado) |
| `DayOfWeekSerializer` | DayOfWeek | — |
| `ClassScheduleSerializer` | ClassSchedule | `subject_offering_name`, `day_of_week_name` |
| `PeriodTypeSerializer` | PeriodType | — |

## ViewSets (8 registrados en router)

| ViewSet | Endpoint | action_permissions usados |
|---------|----------|---------------------------|
| `SubjectViewSet` | `subject/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT |
| `AcademicPeriodViewSet` | `academic-period/` | VIEW/CREATE/UPDATE/DELETE_PERIOD |
| `TeacherSubjectSectionViewSet` | `teacher-subject-section/` | VIEW/CREATE/UPDATE/DELETE_TEACHER_SUBJECT |
| `SubjectAcademicConfigViewSet` | `subject-academic-configs/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT_CONFIG |
| `SubjectOfferingViewSet` | `subject-offerings/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT_OFFERING |
| `InterdisciplinaryProjectViewSet` | `interdisciplinary-projects/` | VIEW/CREATE/UPDATE/DELETE_INTERDISCIPLINARY_PROJECT |
| `SubjectProjectViewSet` | `subject-projects/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT_PROJECT |
| `PeriodTypeViewSet` | `period-types/` | VIEW/CREATE/UPDATE/DELETE_PERIOD_TYPE |

Todos heredan de `BaseAcademicViewSet` que incluye `soft-delete/` action (desactiva `is_active`).

## Workflow

```
SchoolYear
  └─ AcademicPeriod (varios por año, pueden tener parent_period)
      └─ EvaluationBlock (en grading) ← SubjectOffering
          └─ SubjectAcademicConfig ← Subject + AcademicGrade
              └─ Subject

Section
  └─ SubjectOffering (unique: school_year + section + config)
      ├─ TeacherSubjectSection (unique: user + offering)
      ├─ ClassSchedule (unique: offering + day_of_week + start_time)
      └─ InterdisciplinaryProject (M2M via SubjectProject)
```

## Guía de imports

```python
# Modelos
from apps.academic.models import Subject, AcademicPeriod, SubjectOffering, ClassSchedule, DayOfWeek

# Repositorios
from apps.academic.repositories import SubjectRepository, AcademicPeriodRepository

# Servicios
from apps.academic.services.academic_service import AcademicService

# API
from apps.academic.api.serializers import SubjectSerializer, ClassScheduleSerializer
from apps.academic.api.views import SubjectViewSet
```
