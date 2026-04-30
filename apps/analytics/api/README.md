# API - Módulo Analytics

Esta API permite consultar los perfiles de riesgo y los snapshots de métricas de los estudiantes.

---

## Formato de Respuesta

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Riesgo Estudiantil (`/api/analytics/student-risk/`)

### Listar Estudiantes de Alto Riesgo
**POST** `/api/analytics/student-risk/list/`

Request:
```json
{
  "academic_period_id": 1
}
```

Response:
```json
{
  "ok": true,
  "data": [
    {
      "student_id": 1,
      "score": 0.85,
      "level": "Alto"
    }
  ],
  "msg": ""
}
```

### Obtener Riesgo por Estudiante
**POST** `/api/analytics/student-risk/get/`

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
    "student_id": 1,
    "score": 0.85,
    "level": "Alto"
  },
  "msg": ""
}
```

---

## Snapshots de Métricas (`/api/analytics/feature-snapshot/`)

### Obtener Snapshot
**POST** `/api/analytics/feature-snapshot/get/`

Request:
```json
{
  "student_id": 1,
  "academic_period_id": 1
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "student_id": 1,
    "attendance_rate": 0.92,
    "average_grade": 8.5
  },
  "msg": ""
}
```
