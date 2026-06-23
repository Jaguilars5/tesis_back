# Módulo `behavior` — Gestión de Conducta y Evaluaciones

> Gestión de incidentes de conducta, habilidades socioemocionales, evaluaciones comportamentales y evaluaciones diagnósticas.

## Modelos (9)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `ConductIncident` | Incidentes de conducta reportados | `enrollment` (FK, nullable), `reported_by_user` (FK), `academic_period` (FK), `incident_type` (FK), `incident_date`, `severity` (FK), `description`, `actions_taken`, `family_notified`, `created_by`, `modified_by`, `approved_by`. Hereda `TimeStampedModel` + `SyncableModel` |
| `BehaviorEvaluation` | Evaluación de conducta con escala calculada/final | `enrollment` (FK), `academic_period` (FK), `calculated_scale` (FK), `final_scale` (FK), `general_observation`, `override_reason`, `created_by`, `evaluated_by`, `approved_by`, `evaluation_date`, `approval_date`. Unique: `(enrollment, academic_period)`. Hereda `TimeStampedModel` + `SyncableModel` |
| `SkillEvaluation` | Evaluación de habilidad socioemocional | `enrollment` (FK), `academic_period` (FK), `socioemotional_skill` (FK), `qualitative_scale` (FK), `observation`, `evaluation_date`. Unique: `(enrollment, academic_period, socioemotional_skill)`. Hereda `TimeStampedModel` + `SyncableModel` |
| `DiagnosticEvaluation` | Evaluación diagnóstica socioemocional | `enrollment` (FK), `academic_period` (FK), `applied_by_user` (FK), `socioemotional_area` (FK), `findings_description`, `development_level` (FK), `application_date`, `recommendations`. Hereda `TimeStampedModel` + `SyncableModel` |
| `IncidentType` | Catálogo de tipos de incidente | `code` (unique), `name`, `description`, `is_active`. Ordenado por `name` |
| `SocioemotionalSkill` | Habilidades socioemocionales evaluables | `code` (unique), `name`, `description`, `is_active`. Ordenado por `name` |
| `Severity` | Catálogo de niveles de severidad | `code` (unique), `name`, `numeric_level` (1-4), `description`, `is_active`. Ordenado por `numeric_level`. **No hereda `TimeStampedModel`** |
| `SocioemotionalArea` | Catálogo de áreas socioemocionales | `code` (unique), `name`, `description`, `is_active`. Ordenado por `name`. **No hereda `TimeStampedModel`** |
| `DevelopmentLevel` | Catálogo de niveles de desarrollo | `code` (unique), `name`, `description`, `is_active`. Ordenado por `name`. **No hereda `TimeStampedModel`** |

> Solo `ConductIncident`, `BehaviorEvaluation`, `SkillEvaluation` y `DiagnosticEvaluation` heredan de `SyncableModel`. `Severity`, `SocioemotionalArea` y `DevelopmentLevel` no tienen API endpoints.

## Repositorios (6)

| Repositorio | Métodos adicionales |
|-------------|---------------------|
| `ConductIncidentRepository` | `get_all()` ordenado por `-id`; `get_by_enrollment_and_period()`, `get_severe_by_enrollment()`, `list_by_filters()` (student_id, academic_period_id, category, severity, family_notified), `list_for_risk_snapshot()` |
| `BehaviorEvaluationRepository` | `get_all()` ordenado por `-id` |
| `SocioemotionalSkillRepository` | — |
| `SkillEvaluationRepository` | `get_all()` ordenado por `-id` |
| `IncidentTypeRepository` | `get_all()` ordenado por `name` |
| `DiagnosticEvaluationRepository` | — |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `BehaviorEvaluationService` | `calculate_behavior_evaluation(enrollment, academic_period)` | Cálculo automático de escala conductual basado en incidentes del período. Reglas: sin incidentes → SE, 1+ leves → SA, severidad ≥2 o ≥3 incidentes → AC, ≥3 graves o severidad ≥3 con ≥2 incidentes → NA |
| `BehaviorEvaluationService` | `override_evaluation(evaluation, new_scale, reason)` | Asignación manual de escala final con justificación |

## API — Endpoints Registrados

| Método | Endpoint | ViewSet |
|--------|----------|---------|
| GET/POST | `/api/behavior/conduct-incidents/` | ConductIncidentViewSet |
| GET/PUT/PATCH/DEL | `/api/behavior/conduct-incidents/{id}/` | ConductIncidentViewSet |
| GET/POST | `/api/behavior/incident-types/` | IncidentTypeViewSet |
| GET/PUT/PATCH/DEL | `/api/behavior/incident-types/{id}/` | IncidentTypeViewSet |
| GET/POST | `/api/behavior/socioemotional-skills/` | SocioemotionalSkillViewSet |
| GET/PUT/PATCH/DEL | `/api/behavior/socioemotional-skills/{id}/` | SocioemotionalSkillViewSet |
| GET/POST | `/api/behavior/skill-evaluations/` | SkillEvaluationViewSet |
| GET/PUT/PATCH/DEL | `/api/behavior/skill-evaluations/{id}/` | SkillEvaluationViewSet |
| GET/POST | `/api/behavior/behavior-evaluations/` | BehaviorEvaluationViewSet |
| GET/PUT/PATCH/DEL | `/api/behavior/behavior-evaluations/{id}/` | BehaviorEvaluationViewSet |
| GET/POST | `/api/behavior/diagnostic-evaluations/` | DiagnosticEvaluationViewSet |
| GET/PUT/PATCH/DEL | `/api/behavior/diagnostic-evaluations/{id}/` | DiagnosticEvaluationViewSet |

> Los modelos `Severity`, `SocioemotionalArea` y `DevelopmentLevel` **no tienen API pública**. Son catálogos internos usados como FK.

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `ConductIncidentSerializer` | `enrollment_name`, `reported_by_user_name`, `academic_period_name`, `incident_type_name`, `uuid`, `created_at`, `updated_at`, `sync_version` |
| `BehaviorEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `calculated_scale_name`, `final_scale_name` |
| `SkillEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `socioemotional_skill_name`, `qualitative_scale_name` |
| `DiagnosticEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `applied_by_user_name` |
| `IncidentTypeSerializer` | — |
| `SocioemotionalSkillSerializer` | — |

## Tests

```bash
python manage.py test apps.behavior --settings=config.settings.test
```

## Sincronización

`ConductIncident`, `BehaviorEvaluation`, `SkillEvaluation` y `DiagnosticEvaluation` heredan de `SyncableModel`. Handlers registrados en `tasks.py`:
- `ConductIncidentSyncHandler` (con resolución de conflictos personalizada)
- `BehaviorEvaluationSyncHandler`, `SkillEvaluationSyncHandler`, `DiagnosticEvaluationSyncHandler`
