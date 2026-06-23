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
│   ├── __init__.py             # 7 modelos exportados
│   ├── subject.py              # Subject
│   ├── academic_period.py      # AcademicPeriod (+ parent_period self FK, peso_en_anio)
│   ├── period_type.py          # PeriodType (code, name, description, divisions_per_year)
│   ├── subject_academic_config.py  # SubjectAcademicConfig
│   ├── subject_offering.py     # SubjectOffering
│   ├── teacher_subject_section.py  # TeacherSubjectSection
│   └── class_schedule.py       # ClassSchedule (day_of_week integer choices, FK a TeacherSubjectSection)
│
├── repositories/
│   ├── __init__.py             # 7 repositorios exportados
│   ├── academic_repo.py        # SubjectRepository, AcademicPeriodRepository, PeriodTypeRepository,
│   │                           # TeacherSubjectSectionRepository, SubjectAcademicConfigRepository,
│   │                           # SubjectOfferingRepository
│   └── class_schedule_repo.py  # ClassScheduleRepository
│
├── services/
│   ├── __init__.py
│   └── academic_service.py     # AcademicService
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 7 serializers (Subject, AcademicPeriod, TeacherSubjectSection,
│   │                           #   SubjectAcademicConfig, SubjectOffering, ClassSchedule, PeriodType)
│   ├── views.py                # 7 ViewSets (Subject, AcademicPeriod, TeacherSubjectSection,
│   │                           #   SubjectAcademicConfig, SubjectOffering, PeriodType, ClassSchedule)
│   └── urls.py                 # Router con 7 registros
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

## Serializers (7)

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `SubjectSerializer` | Subject | — |
| `AcademicPeriodSerializer` | AcademicPeriod | `school_year_name`, `period_type_name` |
| `TeacherSubjectSectionSerializer` | TeacherSubjectSection | `user_name`, `subject_offering_name` |
| `SubjectAcademicConfigSerializer` | SubjectAcademicConfig | `subject_name`, `academic_grade_name` |
| `SubjectOfferingSerializer` | SubjectOffering | `school_year_name`, `section_name`, `subject_academic_config_name` |
| `ClassScheduleSerializer` | ClassSchedule | `subject_offering_name`, `day_of_week_name` |
| `PeriodTypeSerializer` | PeriodType | — |

## ViewSets (7 registrados en router)

| ViewSet | Endpoint | action_permissions usados |
|---------|----------|---------------------------|
| `SubjectViewSet` | `subject/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT |
| `AcademicPeriodViewSet` | `academic-period/` | VIEW/CREATE/UPDATE/DELETE_PERIOD |
| `TeacherSubjectSectionViewSet` | `teacher-subject-section/` | VIEW/CREATE/UPDATE/DELETE_TEACHER_SUBJECT |
| `SubjectAcademicConfigViewSet` | `subject-academic-configs/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT_CONFIG |
| `SubjectOfferingViewSet` | `subject-offerings/` | VIEW/CREATE/UPDATE/DELETE_SUBJECT_OFFERING |
| `PeriodTypeViewSet` | `period-types/` | VIEW/CREATE/UPDATE/DELETE_PERIOD_TYPE |
| `ClassScheduleViewSet` | `class-schedule/` | VIEW/CREATE/UPDATE/DELETE_CLASS_SCHEDULE |

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
      └─ ClassSchedule (unique: teacher_subject_section + day_of_week + start_time)
```

## Guía de imports

```python
# Modelos
from apps.academic.models import Subject, AcademicPeriod, SubjectOffering, ClassSchedule

# Repositorios
from apps.academic.repositories import SubjectRepository, AcademicPeriodRepository

# Servicios
from apps.academic.services.academic_service import AcademicService

# API
from apps.academic.api.serializers import SubjectSerializer, ClassScheduleSerializer
from apps.academic.api.views import SubjectViewSet
```
