# Módulo `attendance` — Gestión de Asistencia

> Registro de asistencia diaria de los estudiantes, con catálogos de estados y tipos de ausencia.

## Modelos (3)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `Attendance` | Registro de asistencia por estudiante, clase y fecha | `enrollment` (FK), `teacher_subject_section` (FK), `academic_period` (FK), `attendance_status` (FK), `attendance_date`, `absence_type` (FK), `observation`, `created_by`, `modified_by`. Hereda `TimeStampedModel` + `SyncableModel` |
| `AttendanceStatus` | Catálogo de estados de asistencia | `code` (unique: P, A, T, J), `name`, `description`, `is_active`. Ordenado por `name` |
| `AbsenceType` | Catálogo de tipos de ausencia | `code` (unique: justified, unjustified, late, none), `name`, `description`, `is_active`. Ordenado por `name` |

### Unique constraints
- `Attendance`: `(enrollment, teacher_subject_section, attendance_date)`

### Índices
- `(enrollment, academic_period)`
- `(teacher_subject_section, attendance_date)`
- `(attendance_date, academic_period)`

## Repositorios (3)

| Repositorio | Métodos adicionales |
|-------------|---------------------|
| `AttendanceRepository` | `get_all()` ordenado por `-id`; `get_by_unique_key()`, `get_by_enrollment_and_period()`, `get_absences_summary()`, `list_by_filters()` (student_id, academic_period_id, section_id, date, status), `list_for_risk_snapshot()` |
| `AttendanceStatusRepository` | `get_all()` ordenado por `name` |
| `AbsenceTypeRepository` | `get_all()` ordenado por `name` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `AttendanceService` | `create_attendance()` | Crea o actualiza registro (upsert por unique key). Soporta `device_origin` para sincronización |
| `AttendanceService` | `get_attendance(id)` | Obtiene registro por ID |
| `AttendanceService` | `update_attendance(id, **kwargs)` | Actualiza campos |
| `AttendanceService` | `delete_attendance(id)` | Elimina registro |

## API — Endpoints Registrados

| Método | Endpoint | ViewSet | Permiso |
|--------|----------|---------|---------|
| GET/POST | `/api/attendance/attendances/` | AttendanceViewSet | `attendance.view/create_attendance` |
| GET/PUT/PATCH/DEL | `/api/attendance/attendances/{id}/` | AttendanceViewSet | `attendance.view/update/delete_attendance` |
| GET/POST | `/api/attendance/attendance-statuses/` | AttendanceStatusViewSet | `attendance.view/create_attendance_status` |
| GET/PUT/PATCH/DEL | `/api/attendance/attendance-statuses/{id}/` | AttendanceStatusViewSet | `attendance.view/update/delete_attendance_status` |
| GET/POST | `/api/attendance/absence-types/` | AbsenceTypeViewSet | `attendance.view/create_absence_type` |
| GET/PUT/PATCH/DEL | `/api/attendance/absence-types/{id}/` | AbsenceTypeViewSet | `attendance.view/update/delete_absence_type` |

> No hay acciones `soft-delete` en este módulo. Los ViewSets heredan de `ModelViewSet`, no de `BaseAcademicViewSet`.

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `AttendanceSerializer` | `enrollment_name`, `teacher_subject_section_name`, `academic_period_name`, `attendance_status_name`, `uuid`, `created_at`, `updated_at`, `sync_version` |
| `AttendanceStatusSerializer` | — |
| `AbsenceTypeSerializer` | — |

## Tests

```bash
python manage.py test apps.attendance --settings=config.settings.test
```

## Dependencias

- `students.Enrollment`
- `academic.TeacherSubjectSection`, `academic.AcademicPeriod`
- `iam.User` (created_by, modified_by)
- `integration.SyncableModel`

## Sincronización

`Attendance` hereda de `SyncableModel`. Handler registrado: `AttendanceSyncHandler` para `source_table="attendance"` (en `tasks.py`).
