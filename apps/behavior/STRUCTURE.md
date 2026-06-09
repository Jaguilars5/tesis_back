# Estructura de Behavior

## models/ (6)
- `incident_type.py`, `socioemotional_skill.py`, `conduct_incident.py`
- `skill_evaluation.py`, `behavior_evaluation.py`, `diagnostic_evaluation.py`

## api/ (6 ViewSets)
- `ConductIncidentViewSet`, `IncidentTypeViewSet`, `SocioemotionalSkillViewSet`
- `SkillEvaluationViewSet`, `BehaviorEvaluationViewSet`, `DiagnosticEvaluationViewSet`

## services/
- `behavior_service.py` — `BehaviorEvaluationService` (cálculo y override de evaluación conductual)

## repositories/ (6)
- `IncidentTypeRepository`, `SocioemotionalSkillRepository`, `ConductIncidentRepository`
- `SkillEvaluationRepository`, `BehaviorEvaluationRepository`, `DiagnosticEvaluationRepository`
