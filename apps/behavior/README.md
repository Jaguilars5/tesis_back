# Módulo `behavior` — Gestión de Conducta y Evaluaciones

## Descripción
Gestión de incidentes de conducta, habilidades socioemocionales, evaluaciones comportamentales y evaluaciones diagnósticas.

## Modelos (6)
- **IncidentType** — Catálogo de tipos de incidente
- **SocioemotionalSkill** — Habilidades socioemocionales evaluables
- **ConductIncident** — Incidentes de conducta reportados
- **SkillEvaluation** — Evaluación de habilidad socioemocional por estudiante
- **BehaviorEvaluation** — Evaluación de conducta con escala calculada/final
- **DiagnosticEvaluation** — Evaluación diagnóstica socioemocional

## API Endpoints (`/api/behavior/`)
- `conduct-incidents/` — CRUD de incidentes
- `incident-types/` — CRUD de tipos de incidente
- `socioemotional-skills/` — CRUD de habilidades
- `skill-evaluations/` — CRUD de evaluaciones de habilidad
- `behavior-evaluations/` — CRUD de evaluaciones de conducta
- `diagnostic-evaluations/` — CRUD de evaluaciones diagnósticas

## Servicios
- `BehaviorEvaluationService.calculate_behavior_evaluation()` — Cálculo automático de escala conductual
- `BehaviorEvaluationService.override_evaluation()` — Asignación manual de escala final

## Repositorios (6)
- `IncidentTypeRepository`, `SocioemotionalSkillRepository`, `ConductIncidentRepository`
- `SkillEvaluationRepository`, `BehaviorEvaluationRepository`, `DiagnosticEvaluationRepository`

## Tests
- 66 tests (modelos, repositorios, API, permisos RBAC)

## Dependencias
- `students.Enrollment`, `academic.AcademicPeriod`, `iam.User`, `grading.QualitativeScale`
