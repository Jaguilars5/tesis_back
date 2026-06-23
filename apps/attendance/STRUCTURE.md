# Módulo `attendance` — Estructura

## Árbol de archivos

```
attendance/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # Router directo (no delega a api/urls.py): attendances, attendance-statuses, absence-types
├── tasks.py                    # AttendanceSyncHandler
│
├── models/
│   ├── __init__.py             # 3 modelos exportados
│   ├── attendance.py           # Attendance (TimeStampedModel, SyncableModel)
│   ├── attendance_status.py    # AttendanceStatus (code, name, description)
│   └── absence_type.py         # AbsenceType (code, name, description)
│
├── repositories/
│   ├── __init__.py             # 3 repositorios exportados
│   ├── attendance_repository.py         # AttendanceRepository
│   ├── attendance_status_repository.py  # AttendanceStatusRepository
│   └── absence_type_repository.py       # AbsenceTypeRepository
│
├── services/
│   ├── __init__.py
│   └── attendance_service.py   # AttendanceService (CRUD con upsert)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # AttendanceSerializer, AttendanceStatusSerializer, AbsenceTypeSerializer
│   └── views.py                # AttendanceViewSet, AttendanceStatusViewSet, AbsenceTypeViewSet
│
└── tests/
    ├── __init__.py
    ├── test_attendance_models.py
    ├── test_attendance_api.py
    ├── test_api_gaps.py
    ├── test_api_permissions.py
    └── test_repositories.py
```

## Serializers (3)

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `AttendanceSerializer` | Attendance | `enrollment_name`, `teacher_subject_section_name`, `academic_period_name`, `attendance_status_name`, `uuid`, `created_at`, `updated_at`, `sync_version` |
| `AttendanceStatusSerializer` | AttendanceStatus | — |
| `AbsenceTypeSerializer` | AbsenceType | — |

## ViewSets (3 registrados en router)

| ViewSet | Endpoint | Tipo |
|---------|----------|------|
| `AttendanceViewSet` | `attendances/` | CRUD (ModelViewSet) |
| `AttendanceStatusViewSet` | `attendance-statuses/` | CRUD (ModelViewSet) |
| `AbsenceTypeViewSet` | `absence-types/` | CRUD (ModelViewSet) |

## Workflow

```
TeacherSubjectSection
    ↓
Attendance.create(enrollment, teacher_subject_section, academic_period, attendance_date, attendance_status)
    ↓ (upsert por unique_key: enrollment + teacher_subject_section + attendance_date)
AttendanceRepository.get_absences_summary() → para EarlyAlertService (tasa < 70% → alerta)
    ↓
AttendanceRepository.list_for_risk_snapshot() → para AcademicRiskFeatureBuilder
```

## Guía de imports

```python
from apps.attendance.models import Attendance, AttendanceStatus, AbsenceType

from apps.attendance.repositories import AttendanceRepository, AttendanceStatusRepository, AbsenceTypeRepository

from apps.attendance.services import AttendanceService

from apps.attendance.api.serializers import AttendanceSerializer, AttendanceStatusSerializer, AbsenceTypeSerializer
from apps.attendance.api.views import AttendanceViewSet, AttendanceStatusViewSet, AbsenceTypeViewSet

from apps.attendance.tasks import AttendanceSyncHandler
```
