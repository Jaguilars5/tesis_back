# API — Módulo Attendance

Gestiona el registro de asistencia diaria, estados de asistencia y tipos de ausencia.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `attendances/` | GET | `attendance.view_attendance` |
| `attendances/` | POST | `attendance.create_attendance` |
| `attendances/{id}/` | GET | `attendance.view_attendance` |
| `attendances/{id}/` | PUT/PATCH | `attendance.update_attendance` |
| `attendances/{id}/` | DELETE | `attendance.delete_attendance` |
| `attendance-statuses/` | GET | `attendance.view_attendance_status` |
| `attendance-statuses/` | POST | `attendance.create_attendance_status` |
| `attendance-statuses/{id}/` | GET/PUT/PATCH/DEL | `attendance.view/update/delete_attendance_status` |
| `absence-types/` | GET | `attendance.view_absence_type` |
| `absence-types/` | POST | `attendance.create_absence_type` |
| `absence-types/{id}/` | GET/PUT/PATCH/DEL | `attendance.view/update/delete_absence_type` |

---

## Asistencia (`/api/attendance/attendances/`)

### POST — Registrar asistencia (upsert)

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

**Response (201):**
```json
{
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
  "uuid": "550e8400-...",
  "sync_status": "PENDING",
  "sync_version": 1
}
```

### GET — Listar con filtros

- `?date=2025-02-01` — Por fecha
- `?status=1` — Por estado (ID)
- `?student_id=1` — Por estudiante
- `?academic_period_id=1` — Por período
- `?section_id=1` — Por sección

### PATCH — Actualizar

```json
{
  "attendance_status": 2,
  "absence_type": 2,
  "observation": "Justificación presentada al día siguiente"
}
```

---

## Estados de Asistencia (`/api/attendance/attendance-statuses/`)

```json
{"id": 1, "code": "P", "name": "Presente", "is_active": true}
{"id": 2, "code": "A", "name": "Ausente", "is_active": true}
{"id": 3, "code": "T", "name": "Tardanza", "is_active": true}
{"id": 4, "code": "J", "name": "Justificado", "is_active": true}
```

---

## Tipos de Ausencia (`/api/attendance/absence-types/`)

```json
{"id": 1, "code": "justified", "name": "Justificada", "is_active": true}
{"id": 2, "code": "unjustified", "name": "Injustificada", "is_active": true}
{"id": 3, "code": "late", "name": "Atraso", "is_active": true}
{"id": 4, "code": "none", "name": "Sin falta", "is_active": true}
```

---

## Características Comunes

### Paginación

Usa `StandardResultsSetPagination`. Respuesta paginada: `{ count, next, previous, results }`.
