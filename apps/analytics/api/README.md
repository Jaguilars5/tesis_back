# API — Módulo Analytics

API para consultar perfiles de riesgo, snapshots de métricas, alertas tempranas, catálogos analíticos y KPIs de dashboard.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

| Código | Descripción |
| ------ | ----------- |
| 200 | Éxito (listar, obtener) |
| 201 | Creación exitosa |
| 400 | Error de validación/solicitud |
| 401 | No autenticado |
| 403 | Sin permisos |
| 404 | No encontrado |

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
| `risk-factors/` | GET | `analytics.view_risk_factor` |
| `risk-factors/{id}/` | GET | `analytics.view_risk_factor` |
| `student-risk-factors/` | GET | `analytics.view_student_risk_factor` |
| `student-risk-factors/{id}/` | GET | `analytics.view_student_risk_factor` |
| `early-alerts/` | GET/POST | `analytics.view/create_early_alert` |
| `early-alerts/{id}/` | GET/PUT/PATCH/DEL | `analytics.view/update/delete_early_alert` |
| `early-alerts/{id}/mark_attended/` | POST | `analytics.update_early_alert` |
| `dashboard/overview/` | GET | `analytics.view_risk_score` |
| `dashboard/risk-distribution/` | GET | `analytics.view_risk_score` |
| `dashboard/students-at-risk/` | GET | `analytics.view_risk_score` |
| `dashboard/export-csv/` | GET | `analytics.view_risk_score` |
| `dashboard/section-summary/` | GET | `analytics.view_risk_score` |

> No existen endpoints para `alert-types/` ni `urgency-levels/` (no son modelos, son `TextChoices` dentro de `EarlyAlert`).

---

## Riesgo Estudiantil (`/api/analytics/student-risk-scores/`)

### GET — Listar / Obtener

```json
{
  "ok": true,
  "data": [
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
  ],
  "msg": ""
}
```

### POST — Calcular riesgo de un estudiante

**POST** `/api/analytics/student-risk-scores/calculate/`

```json
{"student_id": 1, "academic_period_id": 1}
```

Response: `{"task_id": "uuid...", "status": "PENDING"}`

### POST — Cálculo batch

**POST** `/api/analytics/student-risk-scores/batch_calculate/`

```json
{"academic_period_id": 1, "student_ids": [1, 2, 3]}
```

---

## Snapshots de Métricas (`/api/analytics/feature-snapshots/`)

### GET — Listar / Obtener

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
  "alert_type": "low_attendance",
  "description": "Tasa de asistencia por debajo del 70%",
  "urgency_level": "high"
}
```

### POST — Marcar como atendida

**POST** `/api/analytics/early-alerts/{id}/mark_attended/`

```json
{"response_actions": "Contacto telefónico con representante."}
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

Response: `Content-Type: text/csv`

### GET — Resumen de sección

**GET** `/api/analytics/dashboard/section-summary/?section_id=1`

---

## Características Comunes

### Paginación

Usa `StandardResultsSetPagination`. Respuesta paginada: `{ count, next, previous, results }`.
