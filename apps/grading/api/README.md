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
| `student-notes/` | GET | grading.view_note |
| `student-notes/` | POST | grading.create_note |
| `student-notes/{id}/` | GET | grading.view_note |
| `student-notes/{id}/` | PATCH | grading.update_note |
| `student-notes/{id}/` | DELETE | grading.delete_note |
| `attendance/` | GET | grading.view_attendance |
| `attendance/` | POST | grading.create_attendance |
| `attendance/{id}/` | GET | grading.view_attendance |
| `attendance/{id}/` | PATCH | grading.update_attendance |
| `attendance/{id}/` | DELETE | grading.delete_attendance |
| `conduct-incidents/` | GET | grading.view_incident |
| `conduct-incidents/` | POST | grading.create_incident |
| `conduct-incidents/{id}/` | GET | grading.view_incident |
| `conduct-incidents/{id}/` | PATCH | grading.update_incident |
| `conduct-incidents/{id}/` | DELETE | grading.delete_incident |

Respuesta sin permiso:
```json
{
  "ok": false,
  "data": null,
  "msg": "You do not have permission to perform this action."
}
```

---

## Calificaciones (`/api/grading/student-notes/`)

### Listar Notas
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
        "student": 1,
        "note_value": 18.5,
        "normalized_value": 9.25
      }
    ]
  },
  "msg": ""
}
```

### Obtener Detalle
**GET** `/api/grading/student-notes/{id}/`

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "note_value": 18.5,
    "normalized_value": 9.25
  },
  "msg": ""
}
```

### Crear Nota
**POST** `/api/grading/student-notes/`

Request:
```json
{
  "student": 1,
  "academic_activity": 5,
  "academic_period": 1,
  "teacher_subject_section": 1,
  "note_value": 18.5,
  "observation": "Buen trabajo"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "note_value": 18.5,
    "normalized_value": 9.25
  },
  "msg": ""
}
```

### Actualizar Nota
**PATCH** `/api/grading/student-notes/{id}/`

Request:
```json
{
  "note_value": 19.0
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "note_value": 19.0,
    "normalized_value": 9.5
  },
  "msg": ""
}
```

---

## Asistencia (`/api/grading/attendance/`)

### Listar Asistencia
**GET** `/api/grading/attendance/`

### Detalle de Asistencia
**GET** `/api/grading/attendance/{id}/`

### Crear/Registrar Asistencia
**POST** `/api/grading/attendance/`

Request:
```json
{
  "student": 1,
  "teacher_subject_section": 1,
  "academic_period": 1,
  "date": "2024-05-20",
  "status": "P",
  "observation": ""
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "status": "P",
    "date": "2024-05-20"
  },
  "msg": ""
}
```

---

## Conducta (`/api/grading/conduct-incidents/`)

### Listar Incidentes
**GET** `/api/grading/conduct-incidents/`

### Detalle de Incidente
**GET** `/api/grading/conduct-incidents/{id}/`

### Reportar Incidente
**POST** `/api/grading/conduct-incidents/`

Request:
```json
{
  "student": 1,
  "reported_by": 5,
  "academic_period": 1,
  "incident_date": "2024-05-21",
  "category": "Indisciplina",
  "severity": "Leve",
  "description": "El estudiante conversó durante la clase."
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "severity": "Leve"
  },
  "msg": ""
}
```
