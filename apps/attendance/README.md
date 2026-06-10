# Módulo `attendance` — Gestión de Asistencia

> Registro de asistencia diaria de los estudiantes, con catálogos de estados y tipos de ausencia.

## Modelos

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `Attendance` | Registro de asistencia por estudiante, clase y fecha | `enrollment` (FK), `teacher_subject_section` (FK), `academic_period` (FK), `attendance_status` (FK), `attendance_date`, `absence_type` (FK a AbsenceType), `observation`, `created_by`, `modified_by`. Hereda `SyncableModel`: `uuid`, `sync_status`, `sync_version`, `synced_at`, `device_origin`, `conflict_resolved` |
| `AttendanceStatus` | Catálogo de estados de asistencia | `code` (unique: P, A, T, J), `name`, `description`, `tipo` (POSITIVO/NEGATIVO), `is_active` |
| `AbsenceType` | Catálogo de tipos de ausencia | `code` (unique: justified, unjustified, late, none), `name`, `description`, `is_active` |

### Unique constraints
- `Attendance`: `(enrollment, teacher_subject_section, attendance_date)` — un registro por estudiante, clase y día

### Índices
- `(enrollment, academic_period)` — consultas de asistencia por estudiante y período
- `(teacher_subject_section, attendance_date)` — asistencia diaria por clase
- `(attendance_date, academic_period)` — reportes diarios por período

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `AttendanceService` | `create_attendance(enrollment_id, teacher_subject_section_id, academic_period_id, attendance_date, attendance_status_id, ...)` | Crea o actualiza registro (upsert por unique key) |
| `AttendanceService` | `get_attendance(id)` | Obtiene registro por ID |
| `AttendanceService` | `update_attendance(id, **kwargs)` | Actualiza campos |
| `AttendanceService` | `delete_attendance(id)` | Elimina registro |

## Repositorios

| Repositorio | Métodos clave |
|-------------|---------------|
| `AttendanceRepository` | `get_by_unique_key()`, `get_by_enrollment_and_period()`, `get_absences_summary()`, `list_by_filters(student_id, academic_period_id, section_id, date, status)`, `list_for_risk_snapshot()` |

## API

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| GET/POST | `/api/attendance/attendances/` | Listar/Crear asistencias | `attendance.view/create_attendance` |
| GET/PATCH/DELETE | `/api/attendance/attendances/{id}/` | CRUD individual | `attendance.view/update/delete_attendance` |
| GET/POST | `/api/attendance/attendance-statuses/` | Listar/Crear estados | `attendance.view/create_attendance_status` |
| GET/PATCH/DELETE | `/api/attendance/attendance-statuses/{id}/` | CRUD individual | `attendance.view/update/delete_attendance_status` |
| GET/POST | `/api/attendance/absence-types/` | Listar/Crear tipos | `attendance.view/create_absence_type` |
| GET/PATCH/DELETE | `/api/attendance/absence-types/{id}/` | CRUD individual | `attendance.view/update/delete_absence_type` |

## Respuestas Enriquecidas

Todas las respuestas siguen el formato `{"ok": true, "data": {...}, "msg": ""}`.

```json
{
  "ok": true,
  "data": {
    "id": 1,
    "enrollment": 1,
    "enrollment_name": "Juan Perez - 7mo A (Activa)",
    "teacher_subject_section": 1,
    "teacher_subject_section_name": "Ana Lopez - Matematicas - 7mo A",
    "academic_period": 1,
    "academic_period_name": "Primer Trimestre",
    "attendance_status": 1,
    "attendance_status_name": "Presente",
    "attendance_date": "2025-02-01",
    "absence_type": 1,
    "observation": "",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "sync_status": "PENDING",
    "sync_version": 1
  },
  "msg": ""
}
```

Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Tests

```bash
python manage.py test apps.attendance --settings=config.settings.test
```

## Dependencias

- `students.Enrollment`
- `academic.TeacherSubjectSection`, `academic.AcademicPeriod`
- `iam.User` (created_by, modified_by)

## Sincronización

`Attendance` hereda de `SyncableModel`, proporcionando soporte offline-first con `uuid`, `sync_status`, `sync_version`, `synced_at`, `device_origin` y `conflict_resolved`. Handler registrado: `AttendanceSyncHandler` para `source_table="attendance"`.
