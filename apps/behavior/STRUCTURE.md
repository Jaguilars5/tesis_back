# Módulo `behavior` — Estructura

## Árbol de archivos

```
behavior/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py (Router: 6 ViewSets)
├── tasks.py                    # Handlers sync: ConductIncident, BehaviorEvaluation, SkillEvaluation, DiagnosticEvaluation
├── README.md
│
├── models/
│   ├── __init__.py             # 9 modelos exportados
│   ├── incident_type.py        # IncidentType (TimeStampedModel)
│   ├── socioemotional_skill.py # SocioemotionalSkill (TimeStampedModel)
│   ├── severity.py             # Severity (models.Model, sin TimeStamped)
│   ├── socioemotional_area.py  # SocioemotionalArea (models.Model, sin TimeStamped)
│   ├── development_level.py    # DevelopmentLevel (models.Model, sin TimeStamped)
│   ├── conduct_incident.py     # ConductIncident (TimeStampedModel, SyncableModel)
│   ├── skill_evaluation.py     # SkillEvaluation (TimeStampedModel, SyncableModel)
│   ├── behavior_evaluation.py  # BehaviorEvaluation (TimeStampedModel, SyncableModel)
│   └── diagnostic_evaluation.py# DiagnosticEvaluation (TimeStampedModel, SyncableModel)
│
├── repositories/
│   ├── __init__.py             # 6 repositorios exportados
│   ├── conduct_incident_repository.py
│   ├── behavior_repository.py  # BehaviorEvaluationRepository
│   ├── incident_type_repository.py
│   ├── socioemotional_skill_repository.py
│   ├── skill_evaluation_repository.py
│   └── diagnostic_evaluation_repository.py
│
├── services/
│   ├── __init__.py
│   └── behavior_service.py     # BehaviorEvaluationService (calculate, override)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 6 serializers
│   ├── views.py                # 6 ViewSets (ConductIncident, BehaviorEvaluation, SocioemotionalSkill, SkillEvaluation, DiagnosticEvaluation, IncidentType)
│   └── urls.py                 # Router con 6 registros
│
└── tests/
    ├── __init__.py
    ├── test_api_gaps.py
    ├── test_api_permissions.py
    ├── test_behavior.py
    └── test_repositories.py
```

## Serializers (6)

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `ConductIncidentSerializer` | ConductIncident | `enrollment_name`, `reported_by_user_name`, `academic_period_name`, `incident_type_name`, `uuid`, `created_at`, `updated_at`, `sync_version` |
| `BehaviorEvaluationSerializer` | BehaviorEvaluation | `enrollment_name`, `academic_period_name`, `calculated_scale_name`, `final_scale_name` |
| `SkillEvaluationSerializer` | SkillEvaluation | `enrollment_name`, `academic_period_name`, `socioemotional_skill_name`, `qualitative_scale_name` |
| `DiagnosticEvaluationSerializer` | DiagnosticEvaluation | `enrollment_name`, `academic_period_name`, `applied_by_user_name` |
| `IncidentTypeSerializer` | IncidentType | — |
| `SocioemotionalSkillSerializer` | SocioemotionalSkill | — |

## ViewSets (6 registrados en router)

| ViewSet | Endpoint | Tipo |
|---------|----------|------|
| `ConductIncidentViewSet` | `conduct-incidents/` | CRUD |
| `BehaviorEvaluationViewSet` | `behavior-evaluations/` | CRUD |
| `SocioemotionalSkillViewSet` | `socioemotional-skills/` | CRUD |
| `SkillEvaluationViewSet` | `skill-evaluations/` | CRUD |
| `DiagnosticEvaluationViewSet` | `diagnostic-evaluations/` | CRUD |
| `IncidentTypeViewSet` | `incident-types/` | CRUD |

## Workflow

```
ConductIncident.create()
    ↓
BehaviorEvaluationService.calculate_behavior_evaluation(enrollment, period)
    → Reglas: SE(0 incidentes) → SA(leves) → AC(severidad≥2) → NA(≥3 graves)
    → get_or_create en BehaviorEvaluation
    ↓
AcademicRiskFeatureBuilder (en analytics) consume incidentes vía repository
```

## Guía de imports

```python
from apps.behavior.models import ConductIncident, BehaviorEvaluation, Severity, IncidentType

from apps.behavior.repositories import ConductIncidentRepository, IncidentTypeRepository

from apps.behavior.services.behavior_service import BehaviorEvaluationService

from apps.behavior.api.serializers import ConductIncidentSerializer, IncidentTypeSerializer
from apps.behavior.api.views import ConductIncidentViewSet, IncidentTypeViewSet

from apps.behavior.tasks import ConductIncidentSyncHandler
```
