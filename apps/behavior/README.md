# Módulo `behavior` — Gestión de Conducta y Evaluaciones

> Gestión de incidentes de conducta, habilidades socioemocionales, evaluaciones comportamentales y evaluaciones diagnósticas.

## Modelos

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `ConductIncident` | Incidentes de conducta reportados | `enrollment`, `reported_by_user`, `academic_period`, `incident_type`, `incident_date`, `severity` (FK a Severity), `description`, `actions_taken`, `family_notified`, `created_by`, `modified_by`, `approved_by`, `sync_status`, `sync_version` |
| `BehaviorEvaluation` | Evaluación de conducta con escala calculada/final | `enrollment`, `academic_period`, `calculated_scale`, `final_scale`, `general_observation`, `override_reason`, `created_by`, `evaluated_by`, `approved_by`, `evaluation_date`, `approval_date` |
| `SkillEvaluation` | Evaluación de habilidad socioemocional por estudiante | `enrollment`, `academic_period`, `socioemotional_skill`, `qualitative_scale`, `observation`, `evaluation_date` |
| `DiagnosticEvaluation` | Evaluación diagnóstica socioemocional | `enrollment`, `academic_period`, `applied_by_user`, `socioemotional_area` (FK), `findings_description`, `development_level` (FK), `application_date`, `recommendations` |
| `IncidentType` | Catálogo de tipos de incidente | `code`, `name`, `description`, `is_active` |
| `SocioemotionalSkill` | Habilidades socioemocionales evaluables | `code`, `name`, `description`, `is_active` |
| `Severity` | Catálogo de niveles de severidad | `code`, `name`, `numeric_level` (1-4), `description`, `is_active` |
| `SocioemotionalArea` | Catálogo de áreas socioemocionales | `code`, `name`, `description`, `is_active` |
| `DevelopmentLevel` | Catálogo de niveles de desarrollo | `code`, `name`, `description`, `is_active` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `BehaviorEvaluationService` | `calculate_behavior_evaluation(enrollment, academic_period)` | Cálculo automático de escala conductual basado en incidentes del período |
| `BehaviorEvaluationService` | `override_evaluation(evaluation, new_scale, reason)` | Asignación manual de escala final con justificación |

### Reglas de cálculo de conducta
- Sin incidentes → `SE` (Superior)
- 1+ incidentes leves → `SA` (Satisfactorio)
- Severidad ≥ 2 o ≥ 3 incidentes → `AC` (Aceptable)
- ≥ 3 graves o severidad ≥ 3 con ≥ 2 incidentes → `NA` (No Aceptable)

## API

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| GET | `/api/behavior/conduct-incidents/` | Listar incidentes | `behavior.view_conduct_incident` |
| POST | `/api/behavior/conduct-incidents/` | Crear incidente | `behavior.create_conduct_incident` |
| GET/PATCH/DELETE | `/api/behavior/conduct-incidents/{id}/` | CRUD individual | `behavior.view/update/delete_conduct_incident` |
| GET | `/api/behavior/incident-types/` | Listar tipos | `behavior.view_incident_type` |
| POST | `/api/behavior/incident-types/` | Crear tipo | `behavior.create_incident_type` |
| GET/PATCH/DELETE | `/api/behavior/incident-types/{id}/` | CRUD individual | `behavior.view/update/delete_incident_type` |
| GET | `/api/behavior/socioemotional-skills/` | Listar habilidades | `behavior.view_socioemotional_skill` |
| POST | `/api/behavior/socioemotional-skills/` | Crear habilidad | `behavior.create_socioemotional_skill` |
| GET/PATCH/DELETE | `/api/behavior/socioemotional-skills/{id}/` | CRUD individual | `behavior.view/update/delete_socioemotional_skill` |
| GET | `/api/behavior/skill-evaluations/` | Listar evaluaciones | `behavior.view_skill_evaluation` |
| POST | `/api/behavior/skill-evaluations/` | Crear evaluación | `behavior.create_skill_evaluation` |
| GET/PATCH/DELETE | `/api/behavior/skill-evaluations/{id}/` | CRUD individual | `behavior.view/update/delete_skill_evaluation` |
| GET | `/api/behavior/behavior-evaluations/` | Listar evaluaciones | `behavior.view_behavior_evaluation` |
| POST | `/api/behavior/behavior-evaluations/` | Crear evaluación | `behavior.create_behavior_evaluation` |
| GET/PATCH/DELETE | `/api/behavior/behavior-evaluations/{id}/` | CRUD individual | `behavior.view/update/delete_behavior_evaluation` |
| GET | `/api/behavior/diagnostic-evaluations/` | Listar diagnósticos | `behavior.view_diagnostic_evaluation` |
| POST | `/api/behavior/diagnostic-evaluations/` | Crear diagnóstico | `behavior.create_diagnostic_evaluation` |
| GET/PATCH/DELETE | `/api/behavior/diagnostic-evaluations/{id}/` | CRUD individual | `behavior.view/update/delete_diagnostic_evaluation` |

## Respuestas Enriquecidas

Todas las respuestas siguen el formato `{"ok": true, "data": {...}, "msg": ""}`.

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
    "description": "Llegó tarde a clase",
    "family_notified": true,
    "sync_status": "PENDING",
    "sync_version": 1
  },
  "msg": ""
}
```

Los listados paginados devuelven `data` en el formato `{ count, next, previous, results }`.

## Tests

```bash
python manage.py test apps.behavior --settings=config.settings.test
```

## Dependencias

- `students.Enrollment`, `students.Student`
- `academic.AcademicPeriod`
- `iam.User`
- `grading.QualitativeScale`
- `institutions.Section`

## Sincronización

ConductIncident, BehaviorEvaluation, SkillEvaluation y DiagnosticEvaluation heredan de `SyncableModel`, lo que les proporciona `uuid`, `sync_status`, `sync_version`, `synced_at`, `device_origin` y `conflict_resolved` para operación offline-first.
