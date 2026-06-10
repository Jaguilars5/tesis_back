# API - Módulo Behavior

Esta API gestiona incidentes de conducta, habilidades socioemocionales, evaluaciones comportamentales y evaluaciones diagnósticas.

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

**Response (201 Created):**
```json
{
  "ok": true,
  "data": {
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
    "description": "Llegó tarde a clase sin justificación",
    "actions_taken": "Llamada al representante",
    "family_notified": true,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "sync_status": "PENDING",
    "sync_version": 1
  },
  "msg": ""
}
```

### GET — Listar incidentes

**Filtros disponibles:**
- `?enrollment=1` — Filtrar por matrícula
- `?academic_period=1` — Filtrar por período académico

**Response (200 OK):**
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
        "enrollment_name": "Juan Perez - 7mo A (Activa)",
        "reported_by_user_name": "Ana Lopez",
        "incident_type_name": "Disciplina",
        "incident_date": "2025-02-01",
        "severity": 1,
        "description": "Llegó tarde",
        "family_notified": true
      }
    ]
  },
  "msg": ""
}
```

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

**Response (201 Created):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "enrollment": 1,
    "enrollment_name": "Juan Perez - 7mo A (Activa)",
    "academic_period": 1,
    "academic_period_name": "Primer Trimestre",
    "calculated_scale": 1,
    "calculated_scale_name": "Superior",
    "final_scale": null,
    "general_observation": "El estudiante ha mejorado su comportamiento",
    "evaluation_date": "2025-03-15"
  },
  "msg": ""
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
  "findings_description": "El estudiante presenta buena autoestima y habilidades sociales",
  "development_level": 1,
  "application_date": "2025-02-20",
  "recommendations": "Continuar con el acompañamiento actual"
}
```

**Campos FK normalizados:**
- `socioemotional_area` — ID del catálogo `SocioemotionalArea` (Autoconocimiento, Autocontrol, Relaciones, Autonomía, Empatía)
- `development_level` — ID del catálogo `DevelopmentLevel` (En proceso, Logrado, Por lograr)

---

## Catálogos

### Tipos de Incidente (`/api/behavior/incident-types/`)

```json
{"code": "LEVE", "name": "Leve", "description": "Falta disciplinaria menor"}
{"code": "MODERADO", "name": "Moderado", "description": "Falta disciplinaria moderada"}
{"code": "GRAVE", "name": "Grave", "description": "Falta disciplinaria grave"}
```

### Habilidades Socioemocionales (`/api/behavior/socioemotional-skills/`)

```json
{"code": "EMPATIA", "name": "Empatía", "is_active": true}
{"code": "AUTORREGULACION", "name": "Autorregulación", "is_active": true}
{"code": "RESPONSABILIDAD", "name": "Responsabilidad", "is_active": true}
```

### Severidades (catálogo interno, usado como FK en ConductIncident)

| code | name | numeric_level |
|------|------|---------------|
| LEVE | Falta leve | 1 |
| MODERADA | Falta moderada | 2 |
| GRAVE | Falta grave | 3 |
| MUY_GRAVE | Falta muy grave | 4 |

---

## Sincronización Offline

Los modelos `ConductIncident`, `BehaviorEvaluation`, `SkillEvaluation` y `DiagnosticEvaluation` heredan de `SyncableModel`, por lo que incluyen:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `uuid` | UUID | Identificador único global |
| `sync_status` | CharField | PENDING, PROCESSING, SYNCED, ERROR, CONFLICT |
| `sync_version` | Integer | Versión para control de conflictos |
| `synced_at` | DateTime | Última sincronización |
| `device_origin` | String | Dispositivo de origen |
| `conflict_resolved` | Boolean | Indica si un conflicto fue resuelto |

Los handlers de sincronización registrados:
- `conduct_incident` → `ConductIncidentSyncHandler`
- `behavior_evaluation` → `BehaviorEvaluationSyncHandler`
- `skill_evaluation` → `SkillEvaluationSyncHandler`
- `diagnostic_evaluation` → `DiagnosticEvaluationSyncHandler`
