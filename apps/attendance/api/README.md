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
| `attendance-statuses/` | GET/POST | `attendance.view/create_attendance_status` |
| `attendance-statuses/{id}/` | GET/PATCH/DELETE | `attendance.view/update/delete_attendance_status` |
| `absence-types/` | GET/POST | `attendance.view/create_absence_type` |
| `absence-types/{id}/` | GET/PATCH/DELETE | `attendance.view/update/delete_absence_type` |

---

## Asistencia (`/api/attendance/attendances/`)

### POST — Registrar asistencia

```json
{
  "enrollment": 1,
  "teacher_subject_section": 1,
  "academic_period": 1,
  "attendance_date": "2025-02-01",
  "attendance_status": 1,
  "absence_type": 1,
  "observation": "Llegó 5 minutos tarde"
}
```

**Response (201 Created):**
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
    "observation": "Llegó 5 minutos tarde",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "sync_status": "PENDING",
    "sync_version": 1,
    "device_origin": null
  },
  "msg": ""
}
```

### GET — Listar con filtros

**Filtros disponibles:**
- `?date=2025-02-01` — Filtrar por fecha
- `?status=1` — Filtrar por estado de asistencia (ID)
- `?student_id=1` — Filtrar por estudiante
- `?academic_period_id=1` — Filtrar por período
- `?section_id=1` — Filtrar por sección

**GET** `/api/attendance/attendances/?date=2025-02-01&academic_period_id=1`

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "enrollment_name": "Juan Perez - 7mo A (Activa)",
        "teacher_subject_section_name": "Ana Lopez - Matematicas - 7mo A",
        "attendance_date": "2025-02-01",
        "attendance_status_name": "Presente"
      },
      {
        "id": 2,
        "enrollment_name": "Maria Lopez - 7mo A (Activa)",
        "teacher_subject_section_name": "Ana Lopez - Matematicas - 7mo A",
        "attendance_date": "2025-02-01",
        "attendance_status_name": "Ausente"
      }
    ]
  },
  "msg": ""
}
```

### PATCH — Actualizar

**PATCH** `/api/attendance/attendances/1/`

```json
{
  "attendance_status": 2,
  "absence_type": 2,
  "observation": "Justificación presentada al día siguiente"
}
```

---

## Estados de Asistencia (`/api/attendance/attendance-statuses/`)

### GET — Listar

```json
{"id": 1, "code": "P", "name": "Presente", "tipo": "POSITIVO", "is_active": true}
{"id": 2, "code": "A", "name": "Ausente", "tipo": "NEGATIVO", "is_active": true}
{"id": 3, "code": "T", "name": "Tardanza", "tipo": "NEGATIVO", "is_active": true}
{"id": 4, "code": "J", "name": "Justificado", "tipo": "POSITIVO", "is_active": true}
```

---

## Tipos de Ausencia (`/api/attendance/absence-types/`)

### GET — Listar

```json
{"id": 1, "code": "justified", "name": "Justificada", "is_active": true}
{"id": 2, "code": "unjustified", "name": "Injustificada", "is_active": true}
{"id": 3, "code": "late", "name": "Atraso", "is_active": true}
{"id": 4, "code": "none", "name": "Sin falta", "is_active": true}
```
