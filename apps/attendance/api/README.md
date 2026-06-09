# API - Módulo Attendance

Esta API gestiona el registro de asistencia diaria, estados de asistencia y tipos de ausencia.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `attendances/` | GET | `attendance.view_attendance` |
| `attendances/` | POST | `attendance.create_attendance` |
| `attendances/{id}/` | GET | `attendance.view_attendance` |
| `attendances/{id}/` | PATCH | `attendance.update_attendance` |
| `attendances/{id}/` | DELETE | `attendance.delete_attendance` |
| `attendance-statuses/` | GET | `attendance.view_attendance_status` |
| `attendance-statuses/` | POST | `attendance.create_attendance_status` |
| `attendance-statuses/{id}/` | GET | `attendance.view_attendance_status` |
| `attendance-statuses/{id}/` | PATCH | `attendance.update_attendance_status` |
| `attendance-statuses/{id}/` | DELETE | `attendance.delete_attendance_status` |
| `absence-types/` | GET | `attendance.view_absence_type` |
| `absence-types/` | POST | `attendance.create_absence_type` |
| `absence-types/{id}/` | GET | `attendance.view_absence_type` |
| `absence-types/{id}/` | PATCH | `attendance.update_absence_type` |
| `absence-types/{id}/` | DELETE | `attendance.delete_absence_type` |

## Asistencia (`/api/attendance/attendances/`)

### Registrar

**POST** `/api/attendance/attendances/`

```json
{
  "enrollment": 1,
  "teacher_subject_section": 1,
  "academic_period": 1,
  "attendance_date": "2025-02-01",
  "attendance_status": 1
}
```

Response incluye `enrollment_name`, `teacher_subject_section_name`, `academic_period_name`, `attendance_status_name`.
