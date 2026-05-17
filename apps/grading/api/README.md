# API - Módulo Grading

Esta API gestiona el desempeño estudiantil: calificaciones, asistencia y comportamiento.

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
| `student-notes/` | GET | `grading.view_note` |
| `student-notes/` | POST | `grading.create_note` |
| `student-notes/{id}/` | GET | `grading.view_note` |
| `student-notes/{id}/` | PATCH | `grading.update_note` |
| `student-notes/{id}/` | DELETE | `grading.delete_note` |
| `attendance/` | GET | `grading.view_attendance` |
| `attendance/` | POST | `grading.create_attendance` |
| `attendance/{id}/` | GET | `grading.view_attendance` |
| `attendance/{id}/` | PATCH | `grading.update_attendance` |
| `attendance/{id}/` | DELETE | `grading.delete_attendance` |
| `conduct-incidents/` | GET | `grading.view_incident` |
| `conduct-incidents/` | POST | `grading.create_incident` |
| `conduct-incidents/{id}/` | GET | `grading.view_incident` |
| `conduct-incidents/{id}/` | PATCH | `grading.update_incident` |
| `conduct-incidents/{id}/` | DELETE | `grading.delete_incident` |

---

## Calificaciones (`/api/grading/student-notes/`)

### Listar
**GET** `/api/grading/student-notes/`

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
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "enrollment": 1,
        "class_assignment": 1,
        "grade_type": 1,
        "numeric_score": 18.50,
        "manually_overridden": false
      }
    ]
  },
  "msg": ""
}
```

### Crear
**POST** `/api/grading/student-notes/`

Request:
```json
{
  "enrollment": 1,
  "class_assignment": 1,
  "grade_type": 1,
  "qualitative_scale": 1,
  "numeric_score": 18.50,
  "teacher_observation": "Buen trabajo"
}
```

### Obtener
**GET** `/api/grading/student-notes/{id}/`

### Actualizar
**PATCH** `/api/grading/student-notes/{id}/`

Request:
```json
{
  "numeric_score": 19.00
}
```

---

## Asistencia (`/api/grading/attendance/`)

### Listar
**GET** `/api/grading/attendance/`

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
        "uuid": "550e8400-e29b-41d4-a716-446655440001",
        "enrollment": 1,
        "teacher_subject_section": 1,
        "academic_period": 1,
        "attendance_status": 1,
        "attendance_date": "2024-05-20"
      }
    ]
  },
  "msg": ""
}
```

### Crear
**POST** `/api/grading/attendance/`

Request:
```json
{
  "enrollment": 1,
  "teacher_subject_section": 1,
  "academic_period": 1,
  "attendance_status": 1,
  "attendance_date": "2024-05-20",
  "observation": ""
}
```

### Obtener
**GET** `/api/grading/attendance/{id}/`

### Actualizar
**PATCH** `/api/grading/attendance/{id}/`

---

## Incidentes de Conducta (`/api/grading/conduct-incidents/`)

### Listar
**GET** `/api/grading/conduct-incidents/`

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
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "enrollment": 1,
        "reported_by_user": 5,
        "academic_period": 1,
        "incident_date": "2024-05-21",
        "category": "Indisciplina",
        "severity": 1,
        "family_notified": false
      }
    ]
  },
  "msg": ""
}
```

### Crear
**POST** `/api/grading/conduct-incidents/`

Request:
```json
{
  "enrollment": 1,
  "reported_by_user": 5,
  "academic_period": 1,
  "incident_date": "2024-05-21",
  "category": "Indisciplina",
  "severity": 1,
  "description": "El estudiante conversó durante la clase."
}
```

### Obtener
**GET** `/api/grading/conduct-incidents/{id}/`

### Actualizar
**PATCH** `/api/grading/conduct-incidents/{id}/`

---

## Catálogos

### Estados de Asistencia
- GET/POST `/api/grading/attendance-status/`

### Tipos de Nota
- GET/POST `/api/grading/grade-type/`

### Escalas Cualitativas
- GET/POST `/api/grading/qualitative-scale/`

### Macro Evaluaciones
- GET/POST `/api/grading/evaluation-macro/`

### Criterios de Evaluación
- GET/POST `/api/grading/evaluation-criteria/`

### Subcriterios de Evaluación
- GET/POST `/api/grading/evaluation-subcriteria/`

### Actividades/Tareas
- GET/POST `/api/grading/class-assignment/`