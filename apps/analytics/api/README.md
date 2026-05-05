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

## Autenticación y Permisos

Header requerido:
```
Authorization: Bearer <access_token>
```

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student-risk-scores/` | GET | analytics.view_risk_score |
| `student-risk-scores/{id}/` | GET | analytics.view_risk_score |
| `feature-snapshots/` | GET | analytics.view_feature_snapshot |
| `feature-snapshots/{id}/` | GET | analytics.view_feature_snapshot |

---

## Riesgo Estudiantil (`/api/analytics/student-risk-scores/`)

### Listar Puntajes de Riesgo
**GET** `/api/analytics/student-risk-scores/`

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
        "student_id": 1,
        "score": 0.85,
        "level": "Alto"
      }
    ]
  },
  "msg": ""
}
```

### Obtener Detalle
**GET** `/api/analytics/student-risk-scores/{id}/`

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "student_id": 1,
    "score": 0.85,
    "level": "Alto"
  },
  "msg": ""
}
```

---

## Snapshots de Métricas (`/api/analytics/feature-snapshots/`)

### Listar Snapshots
**GET** `/api/analytics/feature-snapshots/`

### Obtener Snapshot
**GET** `/api/analytics/feature-snapshots/{id}/`

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "student_id": 1,
    "attendance_rate": 0.92,
    "average_grade": 8.5
  },
  "msg": ""
}
```
