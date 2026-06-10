# Módulo `students` — Estructura

## Árbol de archivos

```
students/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # Router: student, enrollments, student-representative, enrollment-statuses
├── tasks.py                    # EnrollmentSyncHandler
├── README.md
│
├── models/
│   ├── __init__.py             # 9 modelos exportados
│   ├── student.py              # Student (TimeStampedModel)
│   ├── enrollment.py           # Enrollment (TimeStampedModel, SyncableModel)
│   ├── enrollment_status.py    # EnrollmentStatus
│   ├── student_representative.py # StudentRepresentative
│   ├── withdrawal_reason.py    # WithdrawalReason (catálogo)
│   ├── residential_zone.py     # ResidentialZone (catálogo)
│   ├── special_needs_type.py   # SpecialNeedsType (catálogo)
│   ├── kinship.py              # Kinship (catálogo)
│   └── enrollment_history.py   # EnrollmentHistory
│
├── repositories/
│   ├── __init__.py             # 5 repositorios
│   ├── students_repo.py        # StudentRepository, StudentRepresentativeRepository
│   ├── enrollment_repo.py      # EnrollmentRepository
│   └── enrollment_status_repo.py # EnrollmentStatusRepository
│
├── services/
│   ├── __init__.py
│   ├── students_service.py     # StudentService
│   └── enrollment_service.py   # EnrollmentService
│
├── api/
│   ├── __init__.py
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── serializers.py      # StudentSerializer, StudentDetailSerializer, etc.
│   ├── filters/
│   │   ├── __init__.py
│   │   └── filters.py          # StudentFilter
│   ├── views.py                # 4 ViewSets
│   └── urls.py                 # 4 registros router
│
└── tests/
    ├── __init__.py
    ├── test_api_gaps.py
    ├── test_models.py
    ├── test_repositories.py
    └── test_services.py
```

## Serializers

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `StudentSerializer` | Student | `full_name`, `age` |
| `StudentDetailSerializer` | Student | `full_name`, `age`, `representatives` (anidado) |
| `StudentRepresentativeSerializer` | StudentRepresentative | `student_names`, `person_names` |
| `EnrollmentSerializer` | Enrollment | — |
| `EnrollmentCreateSerializer` | Enrollment | — |
| `EnrollmentStatusSerializer` | EnrollmentStatus | — |

## ViewSets (4 registrados en router)

| ViewSet | Endpoint | Acciones custom |
|---------|----------|----------------|
| `StudentViewSet` | `student/` | `search/`, `{id}/representatives/` |
| `EnrollmentViewSet` | `enrollments/` | `{id}/withdraw/`, `{id}/transfer/`, `by-section/`, `by-student/` |
| `StudentRepresentativeViewSet` | `student-representative/` | `set_primary/`, `{id}/unlink/` |
| `EnrollmentStatusViewSet` | `enrollment-statuses/` | — |

## Workflow

```
StudentService.create_student() → Person + Student (código EST-XXXXX)
    ↓
EnrollmentService.enroll_student() → Enrollment (status=ACT)
    ↓ (opcional)
EnrollmentService.withdraw_student() → Enrollment (status=RET, withdrawal_reason FK)
    ↓
EnrollmentHistory.create(previous_status, new_status, changed_by)
```

## Guía de imports

```python
from apps.students.models import Student, Enrollment, Kinship, WithdrawalReason
from apps.students.services.students_service import StudentService
from apps.students.services.enrollment_service import EnrollmentService
from apps.students.repositories.students_repo import StudentRepository
from apps.students.repositories.enrollment_repo import EnrollmentRepository
from apps.students.api.views import StudentViewSet, EnrollmentViewSet
```
