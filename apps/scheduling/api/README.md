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
| `schedule-slots/` | GET | scheduling.view_schedule |
| `schedule-slots/` | POST | scheduling.create_schedule |
| `schedule-slots/{id}/` | GET | scheduling.view_schedule |
| `schedule-slots/{id}/` | PATCH | scheduling.update_schedule |
| `schedule-slots/{id}/` | DELETE | scheduling.delete_schedule |
| `time-slots/` | GET | scheduling.view_timeslot |
| `time-slots/` | POST | scheduling.create_timeslot |
| `time-slots/{id}/` | GET | scheduling.view_timeslot |
| `time-slots/{id}/` | PATCH | scheduling.update_timeslot |
| `time-slots/{id}/` | DELETE | scheduling.delete_timeslot |
| `teacher-availability/` | GET | scheduling.view_availability |
| `teacher-availability/` | POST | scheduling.create_availability |
| `teacher-availability/{id}/` | GET | scheduling.view_availability |
| `teacher-availability/{id}/` | PATCH | scheduling.update_availability |
| `teacher-availability/{id}/` | DELETE | scheduling.delete_availability |
| `subject-constraints/` | GET | scheduling.view_constraint |
| `subject-constraints/` | POST | scheduling.create_constraint |
| `subject-constraints/{id}/` | GET | scheduling.view_constraint |
| `subject-constraints/{id}/` | PATCH | scheduling.update_constraint |
| `subject-constraints/{id}/` | DELETE | scheduling.delete_constraint |
| `schedule-configs/` | GET | scheduling.view_template |
| `schedule-configs/` | POST | scheduling.create_template |
| `schedule-configs/{id}/` | GET | scheduling.view_template |
| `schedule-configs/{id}/` | PATCH | scheduling.update_template |
| `schedule-configs/{id}/` | DELETE | scheduling.delete_template |

---

## Patrón de Endpoints

El módulo `scheduling` utiliza ViewSets RESTful con DRF router.

### ScheduleSlots (`/api/scheduling/schedule-slots/`)

#### Listar
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
        "time_slot": 5,
        "classroom": 10
      }
    ]
  },
  "msg": ""
}
```

#### Crear
**POST** `/api/scheduling/schedule-slots/`

Request:
```json
{
  "teacher_subject_section": 1,
  "school_year": 1,
  "time_slot": 5,
  "classroom": 10,
  "is_manual": true
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "time_slot": 5
  },
  "msg": ""
}
```

#### Eliminar
**DELETE** `/api/scheduling/schedule-slots/{id}/`

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "deleted": true
  },
  "msg": ""
}
```

---

## Disponibilidad Docente (`/api/scheduling/teacher-availability/`)

### Registrar Disponibilidad
**POST** `/api/scheduling/teacher-availability/`

Request:
```json
{
  "user": 5,
  "school_year": 1,
  "time_slot": 10,
  "is_available": true
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "is_available": true
  },
  "msg": ""
}
```

---

## Franjas Horarias (`/api/scheduling/time-slots/`)

### Crear Franja
**POST** `/api/scheduling/time-slots/`

Request:
```json
{
  "day_of_week": 1,
  "start_time": "07:00:00",
  "end_time": "07:45:00"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "day_of_week": 1
  },
  "msg": ""
}
```
