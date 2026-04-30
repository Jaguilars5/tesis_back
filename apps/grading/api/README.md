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

## Calificaciones (`/api/grading/student-note/`)

### Listar Notas
**POST** `/api/grading/student-note/list/`

Response:
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "student": 1,
      "note_value": 18.5,
      "normalized_value": 9.25
    }
  ],
  "msg": ""
}
```

### Obtener Detalle
**POST** `/api/grading/student-note/get/`

Request:
```json
{
  "id": 1
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

### Registrar/Agregar Nota
**POST** `/api/grading/student-note/add/`

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
**POST** `/api/grading/student-note/update/`

Request:
```json
{
  "id": 1,
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

### Registrar Asistencia
**POST** `/api/grading/attendance/add/`

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

## Conducta (`/api/grading/conduct-incident/`)

### Reportar Incidente
**POST** `/api/grading/conduct-incident/add/`

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
