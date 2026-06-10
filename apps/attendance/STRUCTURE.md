# Módulo `attendance` — Estructura

## Árbol de archivos

```
attendance/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # Router: attendances, attendance-statuses, absence-types
├── tasks.py                    # AttendanceSyncHandler (BaseSyncHandler)
│
├── models/
│   ├── __init__.py             # AbsenceType, Attendance, AttendanceStatus
│   ├── attendance.py           # Attendance(TimeStampedModel, SyncableModel)
│   ├── attendance_status.py    # AttendanceStatus (code, name, tipo)
│   └── absence_type.py         # AbsenceType (code, name)
│
├── repositories/
│   ├── __init__.py
│   ├── attendance_repository.py            # AttendanceRepository
│   ├── attendance_status_repository.py     # AttendanceStatusRepository
│   └── absence_type_repository.py          # AbsenceTypeRepository
│
├── services/
│   ├── __init__.py
│   └── attendance_service.py   # AttendanceService (CRUD con upsert)
│
├── api/
│   ├── __init__.py
│   ├── README.md               # Documentación de la API
│   ├── serializers.py          # AttendanceSerializer, AttendanceStatusSerializer, AbsenceTypeSerializer
│   └── views.py                # AttendanceViewSet, AttendanceStatusViewSet, AbsenceTypeViewSet
│
├── tests/
│   ├── __init__.py
│   ├── test_attendance_models.py
│   ├── test_attendance_api.py
│   ├── test_api_gaps.py
│   ├── test_api_permissions.py
│   └── test_repositories.py
│
└── migrations/
    └── 0001_initial.py
```

## Serializers

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `AttendanceSerializer` | Attendance | `enrollment_name`, `teacher_subject_section_name`, `academic_period_name`, `attendance_status_name`, `uuid`, `created_at`, `updated_at`, `sync_version` |
| `AttendanceStatusSerializer` | AttendanceStatus | — |
| `AbsenceTypeSerializer` | AbsenceType | — |

## Modelos

### Attendance
```python
class Attendance(TimeStampedModel, SyncableModel):
    enrollment = FK(students.Enrollment, null=True)
    teacher_subject_section = FK(academic.TeacherSubjectSection)
    academic_period = FK(academic.AcademicPeriod)
    attendance_status = FK(attendance.AttendanceStatus, null=True)
    attendance_date = DateField(null=True)
    absence_type = FK(attendance.AbsenceType, null=True, blank=True)
    observation = TextField(null=True, blank=True)
    created_by = FK(iam.User, null=True, blank=True)
    modified_by = FK(iam.User, null=True, blank=True)
    # Heredado de SyncableModel:
    # uuid, sync_status, sync_version, synced_at, device_origin,
    # conflict_resolved, conflict_notes
```

### AttendanceStatus
```python
class AttendanceStatus(TimeStampedModel):
    code = CharField(unique=True)    # P, A, T, J
    name = CharField()
    description = TextField(blank=True)
    tipo = CharField(choices=[POSITIVO, NEGATIVO], null=True)
    is_active = BooleanField(default=True)
```

### AbsenceType
```python
class AbsenceType(TimeStampedModel):
    code = CharField(unique=True)    # justified, unjustified, late, none
    name = CharField()
    description = TextField(blank=True)
    is_active = BooleanField(default=True)
```

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
# Modelos
from apps.attendance.models import Attendance, AttendanceStatus, AbsenceType

# Repositorios
from apps.attendance.repositories import AttendanceRepository, AttendanceStatusRepository, AbsenceTypeRepository

# Servicios
from apps.attendance.services import AttendanceService

# API
from apps.attendance.api.serializers import AttendanceSerializer, AttendanceStatusSerializer, AbsenceTypeSerializer
from apps.attendance.api.views import AttendanceViewSet, AttendanceStatusViewSet, AbsenceTypeViewSet

# Tareas (sync handler)
from apps.attendance.tasks import AttendanceSyncHandler
```
