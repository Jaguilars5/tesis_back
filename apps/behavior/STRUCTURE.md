# Módulo `behavior` — Estructura

## Árbol de archivos

```
behavior/
├── __init__.py
├── apps.py
├── urls.py                     # Router: 6 ViewSets
├── tasks.py                    # Handlers sync: ConductIncident, BehaviorEvaluation, SkillEvaluation, DiagnosticEvaluation
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── incident_type.py        # IncidentType (código, nombre)
│   ├── socioemotional_skill.py # SocioemotionalSkill (habilidad evaluable)
│   ├── conduct_incident.py     # ConductIncident (TimeStampedModel, SyncableModel)
│   ├── skill_evaluation.py     # SkillEvaluation (TimeStampedModel, SyncableModel)
│   ├── behavior_evaluation.py  # BehaviorEvaluation (TimeStampedModel, SyncableModel)
│   ├── diagnostic_evaluation.py# DiagnosticEvaluation (TimeStampedModel, SyncableModel)
│   ├── severity.py             # Severity (catálogo: LEVE=1, MODERADA=2, GRAVE=3, MUY_GRAVE=4)
│   ├── socioemotional_area.py  # SocioemotionalArea (catálogo)
│   └── development_level.py    # DevelopmentLevel (catálogo)
│
├── repositories/
│   ├── __init__.py             # 6 repositorios exportados
│   ├── incident_type_repository.py
│   ├── socioemotional_skill_repository.py
│   ├── conduct_incident_repository.py
│   ├── skill_evaluation_repository.py
│   ├── behavior_evaluation_repository.py
│   └── diagnostic_evaluation_repository.py
│
├── services/
│   ├── __init__.py
│   └── behavior_service.py     # BehaviorEvaluationService (calculate, override)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 6 serializers con nombres enriquecidos
│   └── views.py                # 6 ViewSets con action_permissions
│
└── tests/
    ├── __init__.py
    ├── test_api_gaps.py
    ├── test_behavior.py
    ├── test_models.py
    └── test_repositories.py
```

## Serializers

| Serializer | Campos readonly |
|------------|-----------------|
| `ConductIncidentSerializer` | `enrollment_name`, `reported_by_user_name`, `academic_period_name`, `incident_type_name` |
| `BehaviorEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `calculated_scale_name`, `final_scale_name` |
| `SkillEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `socioemotional_skill_name`, `qualitative_scale_name` |
| `DiagnosticEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `applied_by_user_name` |

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

## Modelos sync (heredan SyncableModel)

- `ConductIncident`, `BehaviorEvaluation`, `SkillEvaluation`, `DiagnosticEvaluation`

## Guía de imports

```python
from apps.behavior.models import ConductIncident, BehaviorEvaluation, Severity
from apps.behavior.repositories import ConductIncidentRepository
from apps.behavior.services.behavior_service import BehaviorEvaluationService
from apps.behavior.api.serializers import ConductIncidentSerializer
from apps.behavior.api.views import ConductIncidentViewSet
```
