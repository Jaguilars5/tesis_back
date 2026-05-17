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
| `student-risk-scores/` | GET | `analytics.view_risk_score` |
| `student-risk-scores/{id}/` | GET | `analytics.view_risk_score` |
| `feature-snapshots/` | GET | `analytics.view_feature_snapshot` |
| `feature-snapshots/{id}/` | GET | `analytics.view_feature_snapshot` |
| `student-risk-factors/` | GET | `analytics.view_risk_factor` |
| `student-risk-factors/{id}/` | GET | `analytics.view_risk_factor` |
| `risk-factors/` | GET | `analytics.view_risk_factor` |
| `risk-factors/` | POST | `analytics.create_risk_factor` |

---

## Riesgo Estudiantil (`/api/analytics/student-risk-scores/`)

### Listar
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
        "student": 1,
        "academic_period": 1,
        "risk_score": 75.00,
        "risk_label": "Medio",
        "model_version": "v1.0",
        "calculated_at": "2024-05-20T10:30:00Z"
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
    "student": 1,
    "academic_period": 1,
    "risk_score": 75.00,
    "risk_label": "Medio",
    "model_version": "v1.0",
    "calculated_at": "2024-05-20T10:30:00Z",
    "risk_factors": [
      {
        "id": 1,
        "risk_factor": {
          "id": 1,
          "code": "LOW_ATTENDANCE",
          "name": "Baja Asistencia"
        },
        "contribution_weight": 45.00
      }
    ]
  },
  "msg": ""
}
```

---

## Snapshots de Métricas (`/api/analytics/feature-snapshots/`)

### Listar
**GET** `/api/analytics/feature-snapshots/`

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
        "academic_period": 1,
        "attendance_rate": 0.92,
        "consecutive_absences_max": 3,
        "tardiness_count": 2,
        "avg_grade_normalized": 8.50,
        "grade_trend_slope": 0.15,
        "failing_subjects_count": 0,
        "conduct_score": 9.00,
        "calculated_at": "2024-05-20T10:30:00Z"
      }
    ]
  },
  "msg": ""
}
```

### Obtener Snapshot
**GET** `/api/analytics/feature-snapshots/{id}/`

---

## Factores de Riesgo (`/api/analytics/risk-factors/`)

### Listar
**GET** `/api/analytics/risk-factors/`

### Crear
**POST** `/api/analytics/risk-factors/`

Request:
```json
{
  "code": "LOW_ATTENDANCE",
  "name": "Baja Asistencia",
  "description": "Estudiante con asistencia menor al 70%"
}
```

---

## Factores por Puntaje (`/api/analytics/student-risk-factors/`)

### Listar
**GET** `/api/analytics/student-risk-factors/`

Filtrar por `student_risk_score`:
**GET** `/api/analytics/student-risk-factors/?student_risk_score=1`