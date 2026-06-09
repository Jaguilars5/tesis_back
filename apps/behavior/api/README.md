# API - Módulo Behavior

Esta API gestiona incidentes de conducta, habilidades socioemocionales, evaluaciones comportamentales y diagnósticas.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `conduct-incidents/` | GET | `behavior.view_conduct_incident` |
| `conduct-incidents/` | POST | `behavior.create_conduct_incident` |
| `conduct-incidents/{id}/` | GET/PATCH/DELETE | `behavior.view/update/delete_conduct_incident` |
| `incident-types/` | GET/POST | `behavior.view/create_incident_type` |
| `incident-types/{id}/` | GET/PATCH/DELETE | `behavior.view/update/delete_incident_type` |
| `socioemotional-skills/` | GET/POST | `behavior.view/create_socioemotional_skill` |
| `socioemotional-skills/{id}/` | GET/PATCH/DELETE | `behavior.view/update/delete_socioemotional_skill` |
| `skill-evaluations/` | GET/POST | `behavior.view/create_skill_evaluation` |
| `skill-evaluations/{id}/` | GET/PATCH/DELETE | `behavior.view/update/delete_skill_evaluation` |
| `behavior-evaluations/` | GET/POST | `behavior.view/create_behavior_evaluation` |
| `behavior-evaluations/{id}/` | GET/PATCH/DELETE | `behavior.view/update/delete_behavior_evaluation` |
| `diagnostic-evaluations/` | GET/POST | `behavior.view/create_diagnostic_evaluation` |
| `diagnostic-evaluations/{id}/` | GET/PATCH/DELETE | `behavior.view/update/delete_diagnostic_evaluation` |

## Incidentes de Conducta (`/api/behavior/conduct-incidents/`)

### Registrar

**POST** `/api/behavior/conduct-incidents/`

```json
{
  "enrollment": 1,
  "reported_by_user": 1,
  "academic_period": 1,
  "incident_date": "2025-02-01",
  "incident_type": 1,
  "severity": 3,
  "description": "Descripción del incidente"
}
```

Response incluye `enrollment_name`, `reported_by_user_name`, `academic_period_name`, `incident_type_name`.
