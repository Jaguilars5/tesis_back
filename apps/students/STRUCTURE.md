# Módulo `students` — Estructura

## Árbol de archivos

```
students/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py (student, enrollments, student-representative)
├── tasks.py                    # EnrollmentSyncHandler
├── README.md
│
├── models/
│   ├── __init__.py             # 8 modelos exportados
│   ├── student.py              # Student (TimeStampedModel)
│   ├── student_representative.py # StudentRepresentative
│   ├── enrollment.py           # Enrollment (TimeStampedModel, SyncableModel) + EnrollmentStatusChoices
│   ├── withdrawal_reason.py    # WithdrawalReason (catálogo)
│   ├── residential_zone.py     # ResidentialZone (catálogo)
│   ├── special_needs_type.py   # SpecialNeedsType (catálogo)
│   ├── kinship.py              # Kinship (catálogo)
│   └── enrollment_history.py   # EnrollmentHistory
│
├── repositories/
│   ├── __init__.py             # 3 repositorios exportados
│   ├── students_repo.py        # StudentRepository, StudentRepresentativeRepository
│   └── enrollment_repo.py      # EnrollmentRepository
│
├── services/
│   ├── __init__.py             # 2 servicios exportados
│   ├── students_service.py     # StudentService
│   └── enrollment_service.py   # EnrollmentService
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── serializers.py      # StudentSerializer, StudentDetailSerializer, StudentRepresentativeSerializer, EnrollmentSerializer, EnrollmentCreateSerializer
│   ├── filters/
│   │   └── filters.py          # StudentFilter
│   ├── views.py                # 3 ViewSets (Student, StudentRepresentative, Enrollment)
│   └── urls.py                 # Router: student, student-representative, enrollments
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_gaps.py
    ├── test_api_permissions.py
    ├── test_enrollment.py
    ├── test_models.py
    ├── test_repositories.py
    └── test_services.py
```

## Workflow

```
StudentService.create_student() → Person + Student (código EST-XXXXX)
    ↓
EnrollmentService.enroll_student() → Enrollment (status=ACT)
    ↓ (opcional)
EnrollmentService.withdraw_student() → Enrollment (status=RET)
    ↓
EnrollmentHistory.create(previous_status, new_status, changed_by)
```

## Guía de imports

```python
from apps.students.models import Student, Enrollment, Kinship, WithdrawalReason

from apps.students.services.students_service import StudentService
from apps.students.services.enrollment_service import EnrollmentService

from apps.students.repositories import StudentRepository, EnrollmentRepository

from apps.students.api.views import StudentViewSet, EnrollmentViewSet
```
