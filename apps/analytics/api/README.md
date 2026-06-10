# API - Módulo Analytics

Esta API permite consultar perfiles de riesgo, snapshots de métricas, alertas tempranas, catálogos analíticos y KPIs de dashboard.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student-risk-scores/` | GET | `analytics.view_risk_score` |
| `student-risk-scores/{id}/` | GET | `analytics.view_risk_score` |
| `student-risk-scores/calculate/` | POST | `analytics.create_student_risk_factor` |
| `student-risk-scores/batch_calculate/` | POST | `analytics.create_student_risk_factor` |
| `feature-snapshots/` | GET | `analytics.view_feature_snapshot` |
| `feature-snapshots/{id}/` | GET | `analytics.view_feature_snapshot` |
| `alert-types/` | GET/POST | `analytics.view/create_alert_type` |
| `alert-types/{id}/` | GET/PATCH/DEL | `analytics.view/update/delete_alert_type` |
| `urgency-levels/` | GET/POST | `analytics.view/create_urgency_level` |
| `urgency-levels/{id}/` | GET/PATCH/DEL | `analytics.view/update/delete_urgency_level` |
| `risk-factors/` | GET | `analytics.view_risk_factor` |
| `student-risk-factors/` | GET | `analytics.view_student_risk_factor` |
| `early-alerts/` | GET/POST | `analytics.view/create_early_alert` |
| `early-alerts/{id}/` | GET/PATCH/DEL | `analytics.view/update/delete_early_alert` |
| `early-alerts/{id}/mark_attended/` | POST | `analytics.update_early_alert` |
| `dashboard/overview/` | GET | `analytics.view_risk_score` |
| `dashboard/risk-distribution/` | GET | `analytics.view_risk_score` |
| `dashboard/students-at-risk/` | GET | `analytics.view_risk_score` |
| `dashboard/export-csv/` | GET | `analytics.view_risk_score` |
| `dashboard/section-summary/` | GET | `analytics.view_risk_score` |

---

## Riesgo Estudiantil (`/api/analytics/student-risk-scores/`)

### GET — Listar

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
        "enrollment": 1,
        "enrollment_name": "Juan Perez - 7mo A (Activa)",
        "academic_period": 1,
        "academic_period_name": "Primer Trimestre",
        "risk_score": "75.00",
        "risk_label": "rojo",
        "model_version": "rules-fallback-v1",
        "calculated_at": "2025-06-01T00:00:00Z",
        "risk_factors": [
          {"id": 1, "risk_factor_name": "Baja Asistencia", "contribution_weight": "35.00"}
        ]
      }
    ]
  },
  "msg": ""
}
```

### POST — Calcular riesgo de un estudiante

**POST** `/api/analytics/student-risk-scores/calculate/`

```json
{
  "student_id": 1,
  "academic_period_id": 1
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {"task_id": "550e8400-...", "status": "PENDING"},
  "msg": ""
}
```

---

## Snapshots de Métricas (`/api/analytics/feature-snapshots/`)

### GET — Listar

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 1,
    "results": [
      {
        "id": 1,
        "enrollment": 1,
        "enrollment_name": "Juan Perez - 7mo A (Activa)",
        "academic_period": 1,
        "academic_period_name": "Primer Trimestre",
        "attendance_rate": "85.00",
        "consecutive_absences_max": 3,
        "formative_avg_normalized": "7.50",
        "summative_avg_normalized": "6.80",
        "failing_subjects_count": 0,
        "conduct_score": "8.50",
        "calculated_at": "2025-06-01T00:00:00Z"
      }
    ]
  },
  "msg": ""
}
```

---

## Alertas Tempranas (`/api/analytics/early-alerts/`)

### POST — Crear alerta

```json
{
  "enrollment": 1,
  "academic_period": 1,
  "alert_type": 1,
  "description": "Tasa de asistencia por debajo del 70%",
  "urgency_level": 2
}
```

### POST — Marcar como atendida

**POST** `/api/analytics/early-alerts/{id}/mark_attended/`

```json
{
  "response_actions": "Contacto telefónico con representante. Compromiso firmado."
}
```

---

## Dashboard (`/api/analytics/dashboard/`)

### GET — Overview

**GET** `/api/analytics/dashboard/overview/?period_id=1`

```json
{
  "ok": true,
  "data": {
    "total_students": 100,
    "attendance_rate_avg": 87.5,
    "formative_avg": 7.2,
    "summative_avg": 6.8,
    "failing_count": 15,
    "risk_distribution": {"rojo": 10, "amarillo": 25, "verde": 65},
    "active_alerts": 8,
    "avg_severe_incidents": 0.3
  },
  "msg": ""
}
```

### GET — Exportar CSV

**GET** `/api/analytics/dashboard/export-csv/?type=risk&period_id=1`

Response: `Content-Type: text/csv` con headers `Código Estudiante, Score Riesgo, Nivel`.

### GET — Sección

**GET** `/api/analytics/dashboard/section-summary/?section_id=1`

---

## Catálogos

### AlertTypes (`/api/analytics/alert-types/`)

```json
{"code": "low_attendance", "name": "Baja Asistencia"}
{"code": "failing_grades", "name": "Calificaciones Bajas"}
{"code": "behavioral", "name": "Problemas de Conducta"}
{"code": "dropout_risk", "name": "Riesgo de Deserción"}
{"code": "socioemotional", "name": "Problemas Socioemocionales"}
```

### UrgencyLevels (`/api/analytics/urgency-levels/`)

```json
{"code": "low", "name": "Baja"}
{"code": "medium", "name": "Media"}
{"code": "high", "name": "Alta"}
{"code": "critical", "name": "Crítica"}
```
