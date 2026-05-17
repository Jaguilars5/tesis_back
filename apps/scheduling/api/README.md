# API - Módulo Scheduling

Esta API gestiona la organización temporal del centro: franjas horarias, disponibilidad docente y asignaciones de clases.

---

## Formato de Respuesta

Todas las peticiones devuelven el esquema estandarizado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Autenticación y Permisos

Header requerido:
```
Authorization: Bearer <access_token>
```

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `schedule-slots/` | GET | `scheduling.view_schedule` |
| `schedule-slots/` | POST | `scheduling.create_schedule` |
| `schedule-slots/{id}/` | GET | `scheduling.view_schedule` |
| `schedule-slots/{id}/` | PATCH | `scheduling.update_schedule` |
| `schedule-slots/{id}/` | DELETE | `scheduling.delete_schedule` |
| `time-slots/` | GET | `scheduling.view_timeslot` |
| `time-slots/` | POST | `scheduling.create_timeslot` |
| `time-slots/{id}/` | GET | `scheduling.view_timeslot` |
| `time-slots/{id}/` | PATCH | `scheduling.update_timeslot` |
| `time-slots/{id}/` | DELETE | `scheduling.delete_timeslot` |
| `teacher-availability/` | GET | `scheduling.view_availability` |
| `teacher-availability/` | POST | `scheduling.create_availability` |
| `teacher-availability/{id}/` | GET | `scheduling.view_availability` |
| `teacher-availability/{id}/` | PATCH | `scheduling.update_availability` |
| `teacher-availability/{id}/` | DELETE | `scheduling.delete_availability` |
| `subject-constraints/` | GET | `scheduling.view_constraint` |
| `subject-constraints/` | POST | `scheduling.create_constraint` |
| `subject-constraints/{id}/` | GET | `scheduling.view_constraint` |
| `subject-constraints/{id}/` | PATCH | `scheduling.update_constraint` |
| `subject-constraints/{id}/` | DELETE | `scheduling.delete_constraint` |
| `schedule-configs/` | GET | `scheduling.view_template` |
| `schedule-configs/` | POST | `scheduling.create_template` |
| `schedule-configs/{id}/` | GET | `scheduling.view_template` |
| `schedule-configs/{id}/` | PATCH | `scheduling.update_template` |
| `schedule-configs/{id}/` | DELETE | `scheduling.delete_template` |

---

## Bloques de Horario (`/api/scheduling/schedule-slots/`)

### Listar
**GET** `/api/scheduling/schedule-slots/`

Response (paginado):
```json
{
  "ok": true,
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "teacher_subject_section": 1,
        "time_slot": 5,
        "classroom": 10,
        "is_manual": true,
        "active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear
**POST** `/api/scheduling/schedule-slots/`

Request:
```json
{
  "teacher_subject_section": 1,
  "time_slot": 5,
  "classroom": 10,
  "is_manual": true
}
```

### Obtener
**GET** `/api/scheduling/schedule-slots/{id}/`

### Actualizar
**PATCH** `/api/scheduling/schedule-slots/{id}/`

### Eliminar
**DELETE** `/api/scheduling/schedule-slots/{id}/`

---

## Franjas Horarias (`/api/scheduling/time-slots/`)

### Listar
**GET** `/api/scheduling/time-slots/`

### Crear
**POST** `/api/scheduling/time-slots/`

Request:
```json
{
  "timing_regime": 1,
  "name": "1ra Hora",
  "day_of_week": 1,
  "start_time": "07:00:00",
  "end_time": "07:45:00",
  "is_break": false
}
```

### Obtener
**GET** `/api/scheduling/time-slots/{id}/`

### Actualizar
**PATCH** `/api/scheduling/time-slots/{id}/`

---

## Disponibilidad Docente (`/api/scheduling/teacher-availability/`)

### Listar
**GET** `/api/scheduling/teacher-availability/`

### Crear
**POST** `/api/scheduling/teacher-availability/`

Request:
```json
{
  "user": 5,
  "time_slot": 10,
  "is_available": true
}
```

### Obtener
**GET** `/api/scheduling/teacher-availability/{id}/`

### Actualizar
**PATCH** `/api/scheduling/teacher-availability/{id}/`

---

## Restricciones de Materia (`/api/scheduling/subject-constraints/`)

### Listar
**GET** `/api/scheduling/subject-constraints/`

### Crear
**POST** `/api/scheduling/subject-constraints/`

Request:
```json
{
  "subject_academic_config": 1,
  "required_consecutive_slots": 2,
  "max_slots_per_day": 4,
  "preferred_room_type": 1
}
```

---

## Configuraciones de Horario (`/api/scheduling/schedule-configs/`)

### Listar
**GET** `/api/scheduling/schedule-configs/`

### Crear
**POST** `/api/scheduling/schedule-configs/`

Request:
```json
{
  "timing_regime": 1,
  "day_start_time": "07:00:00",
  "class_duration_minutes": 45,
  "break_duration_minutes": 15,
  "slots_before_break": 3,
  "total_slots_per_day": 6
}
```