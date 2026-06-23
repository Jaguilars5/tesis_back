# API — Módulo Behavior

Gestiona incidentes de conducta, habilidades socioemocionales, evaluaciones comportamentales y evaluaciones diagnósticas.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `conduct-incidents/` | GET | `behavior.view_conduct_incident` |
| `conduct-incidents/` | POST | `behavior.create_conduct_incident` |
| `conduct-incidents/{id}/` | GET | `behavior.view_conduct_incident` |
| `conduct-incidents/{id}/` | PUT/PATCH | `behavior.update_conduct_incident` |
| `conduct-incidents/{id}/` | DELETE | `behavior.delete_conduct_incident` |
| `incident-types/` | GET | `behavior.view_incident_type` |
| `incident-types/` | POST | `behavior.create_incident_type` |
| `incident-types/{id}/` | GET/PUT/PATCH/DEL | `behavior.view/update/delete_incident_type` |
| `socioemotional-skills/` | GET | `behavior.view_socioemotional_skill` |
| `socioemotional-skills/` | POST | `behavior.create_socioemotional_skill` |
| `socioemotional-skills/{id}/` | GET/PUT/PATCH/DEL | `behavior.view/update/delete_socioemotional_skill` |
| `skill-evaluations/` | GET | `behavior.view_skill_evaluation` |
| `skill-evaluations/` | POST | `behavior.create_skill_evaluation` |
| `skill-evaluations/{id}/` | GET/PUT/PATCH/DEL | `behavior.view/update/delete_skill_evaluation` |
| `behavior-evaluations/` | GET | `behavior.view_behavior_evaluation` |
| `behavior-evaluations/` | POST | `behavior.create_behavior_evaluation` |
| `behavior-evaluations/{id}/` | GET/PUT/PATCH/DEL | `behavior.view/update/delete_behavior_evaluation` |
| `diagnostic-evaluations/` | GET | `behavior.view_diagnostic_evaluation` |
| `diagnostic-evaluations/` | POST | `behavior.create_diagnostic_evaluation` |
| `diagnostic-evaluations/{id}/` | GET/PUT/PATCH/DEL | `behavior.view/update/delete_diagnostic_evaluation` |

---

## Incidentes de Conducta (`/api/behavior/conduct-incidents/`)

### POST — Registrar incidente

```json
{
  "enrollment": 1,
  "reported_by_user": 1,
  "academic_period": 1,
  "incident_date": "2025-02-01",
  "incident_type": 1,
  "severity": 1,
  "description": "Llegó tarde a clase sin justificación",
  "actions_taken": "Llamada al representante",
  "family_notified": true
}
```

**Response (201):**
```json
{
  "id": 1,
  "enrollment": 1,
  "enrollment_name": "Juan Perez - 7mo A (Activa)",
  "reported_by_user": 1,
  "reported_by_user_name": "Ana Lopez",
  "academic_period": 1,
  "academic_period_name": "Primer Trimestre",
  "incident_type": 1,
  "incident_type_name": "Disciplina",
  "incident_date": "2025-02-01",
  "severity": 1,
  "description": "Llegó tarde",
  "actions_taken": "Llamada al representante",
  "family_notified": true,
  "uuid": "550e8400-...",
  "sync_status": "PENDING",
  "sync_version": 1
}
```

### GET — Listar con filtros disponibles

- `?enrollment=1` — Por matrícula
- `?academic_period=1` — Por período académico

---

## Evaluaciones de Conducta (`/api/behavior/behavior-evaluations/`)

### POST — Crear evaluación

```json
{
  "enrollment": 1,
  "academic_period": 1,
  "calculated_scale": 1,
  "evaluation_date": "2025-03-15",
  "general_observation": "El estudiante ha mejorado su comportamiento"
}
```

---

## Evaluaciones de Habilidad Socioemocional (`/api/behavior/skill-evaluations/`)

### POST — Registrar evaluación

```json
{
  "enrollment": 1,
  "academic_period": 1,
  "socioemotional_skill": 1,
  "qualitative_scale": 1,
  "observation": "Muestra empatía con sus compañeros"
}
```

---

## Evaluaciones Diagnósticas (`/api/behavior/diagnostic-evaluations/`)

### POST — Registrar evaluación

```json
{
  "enrollment": 1,
  "academic_period": 1,
  "applied_by_user": 1,
  "socioemotional_area": 1,
  "findings_description": "El estudiante presenta buena autoestima",
  "development_level": 1,
  "application_date": "2025-02-20",
  "recommendations": "Continuar con el acompañamiento actual"
}
```

---

## Catálogos

### Tipos de Incidente (`/api/behavior/incident-types/`)

```json
{"code": "LEVE", "name": "Leve", "is_active": true}
{"code": "MODERADO", "name": "Moderado", "is_active": true}
{"code": "GRAVE", "name": "Grave", "is_active": true}
```

### Habilidades Socioemocionales (`/api/behavior/socioemotional-skills/`)

```json
{"code": "EMPATIA", "name": "Empatía", "is_active": true}
{"code": "AUTORREGULACION", "name": "Autorregulación", "is_active": true}
{"code": "RESPONSABILIDAD", "name": "Responsabilidad", "is_active": true}
```

> Los catálogos `Severity`, `SocioemotionalArea` y `DevelopmentLevel` **no tienen API pública**. Se usan internamente como FK en los modelos transaccionales.

### Severidades (catálogo interno)

| code | name | numeric_level |
|------|------|---------------|
| LEVE | Falta leve | 1 |
| MODERADA | Falta moderada | 2 |
| GRAVE | Falta grave | 3 |
| MUY_GRAVE | Falta muy grave | 4 |

---

## Características Comunes

### Paginación

Usa `StandardResultsSetPagination`. Respuesta paginada: `{ count, next, previous, results }`.
