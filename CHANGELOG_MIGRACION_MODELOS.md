# CHANGELOG - Migración de Modelos

Fecha: 2026-06-14
Referencia: README_migracion_modelos.md

## Resumen

Se ejecutó una corrección estructural completa del sistema siguiendo el plan de migración documentado. Todas las migraciones fueron recreadas desde cero.

## Modelos Eliminados del MVP

| Modelo | Archivo | Notas |
|--------|---------|-------|
| `LearningReport` | `apps/grading/models/learning_report.py` | Eliminado - métricas ya derivadas de PeriodGradeSummary |
| `DiagnosticEvaluation` | `apps/behavior/models/diagnostic_evaluation.py` | Eliminado del MVP |
| `SocioemotionalArea` | `apps/behavior/models/socioemotional_area.py` | Eliminado del MVP |
| `DevelopmentLevel` | `apps/behavior/models/development_level.py` | Eliminado del MVP |
| `SocioemotionalSkill` | `apps/behavior/models/socioemotional_skill.py` | Eliminado del MVP |
| `SkillEvaluation` | `apps/behavior/models/skill_evaluation.py` | Eliminado del MVP |

### Referencias eliminadas

- **apps/grading/models/__init__.py**: Removido import de `LearningReport`
- **apps/grading/api/serializers.py**: Removido `LearningReportSerializer`
- **apps/grading/tasks.py**: Removido `LearningReportSyncHandler`
- **apps/behavior/models/__init__.py**: Removido imports de SocioemotionalArea, DevelopmentLevel, SocioemotionalSkill, SkillEvaluation, DiagnosticEvaluation
- **apps/behavior/api/serializers.py**: Removido SocioemotionalSkillSerializer, SkillEvaluationSerializer, DiagnosticEvaluationSerializer
- **apps/behavior/api/views.py**: Removido SocioemotionalSkillViewSet, SkillEvaluationViewSet, DiagnosticEvaluationViewSet
- **apps/behavior/api/urls.py**: Removido registro de routers para los ViewSets eliminados
- **apps/behavior/admin.py**: Removido Admin para SocioemotionalSkill, SkillEvaluation, DiagnosticEvaluation
- **apps/behavior/tasks.py**: Removido SkillEvaluationSyncHandler, DiagnosticEvaluationSyncHandler
- **apps/behavior/repositories/__init__.py**: Removido SocioemotionalSkillRepository, SkillEvaluationRepository, DiagnosticEvaluationRepository
- **apps/core/api/role_handlers.py**: Removido SkillEvaluation de ALLOWED_MODELS en todos los RoleHandlers
- **apps/core/api/filters.py**: Removido SocioemotionalSkill de PUBLIC_CATALOGS
- **apps/core/management/commands/seed_catalogs.py**: Removido seeding de socioemotional_skills, socioemotional_areas, development_levels
- **apps/core/management/commands/seed_test_data.py**: Removido _create_socioemotional_skills() y datos relacionados

## Cambios en Modelos Existentes

### Enrollment (`apps/students/models/enrollment.py`)
- Campo `school_year`: Eliminado (se deriva de `section.school_year` via property)
- `unique_together`: Reemplazado por `UniqueConstraint(fields=['student', 'section'], name='unique_student_section')`
- Índices que usaban `school_year`: Eliminados
- Agregada property `school_year` para compatibilidad hacia atrás

### SubjectOffering (`apps/academic/models/subject_offering.py`)
- Campo `school_year`: Eliminado (se deriva de `section.school_year` via property)
- `unique_together`: Reemplazado por `UniqueConstraint(fields=['section', 'subject_academic_config'], name='unique_section_subject_config')`
- Índice `(section, school_year)`: Eliminado
- Agregada property `school_year` para compatibilidad hacia atrás

### RecoveryProcess (`apps/grading/models/recovery_process.py`)
- Campo `subject_offering`: Eliminado (se obtiene de `period_grade_summary.subject_offering` via property)
- Índice `(subject_offering, start_date)`: Eliminado
- Agregada property `subject_offering` para compatibilidad hacia atrás

### StudentNote (`apps/grading/models/student_note.py`)
- Campo `evaluative_activity`: Ahora obligatorio (removido `null=True, blank=True`)
- Agregada validación en `clean()` para coherencia de matrícula (enrollment.section debe coincidir con activity section)
- Validaciones existentes reforzadas:
  - NUMERIC requiere numeric_score
  - QUALITATIVE requiere qualitative_scale
  - numeric_score debe estar entre 0 y max_score

### EvaluativeActivity (`apps/grading/models/evaluative_activity.py`)
- Agregada validación en `clean()` para coherencia estructural:
  - `teacher_subject_section` debe pertenecer a la misma oferta que `component_indicator`
- Agregada validación de `due_date`:
  - Debe estar dentro del período académico del bloque relacionado

### EvaluationBlock (`apps/grading/models/evaluation_block.py`)
- Agregada validación en `clean()`:
  - La suma de `weight_percentage` por materia y período no puede exceder 100%

### BlockComponent (`apps/grading/models/block_component.py`)
- Agregada validación en `clean()`:
  - La suma de `internal_weight` dentro del bloque no puede exceder 100%

### ComponentIndicator (`apps/grading/models/component_indicator.py`)
- Agregada validación en `clean()`:
  - La suma de `internal_weight` dentro del componente no puede exceder 100%

### Attendance (`apps/attendance/models/attendance.py`)
- Agregadas validaciones cruzadas en `clean()`:
  - `teacher_subject_section.section` debe coincidir con `enrollment.section`
  - `attendance_date` debe estar dentro del período académico

### BehaviorEvaluation (`apps/behavior/models/behavior_evaluation.py`)
- Agregada validación condicional en `clean()`:
  - `override_reason` es obligatorio cuando `final_scale != calculated_scale`

### ConductIncident (`apps/behavior/models/conduct_incident.py`)
- Campo `enrollment`: Ahora obligatorio (removido `null=True`)
- Campo `incident_type`: Ahora obligatorio (removido `null=True`)

### StudentRepresentative (`apps/students/models/student_representative.py`)
- Agregado `UniqueConstraint` condicional: `UniqueConstraint(fields=['student'], condition=Q(is_primary=True), name='unique_primary_representative_per_student')`
- Esto asegura que solo un representante por estudiante pueda ser primario

### StudentFeatureSnapshot (`apps/analytics/models/student_feature_snapshot.py`)
- `unique_together`: Eliminado para permitir histórico de snapshots
- Agregada lógica en `save()` para marcar el snapshot anterior como no actual cuando se crea uno nuevo
- Nuevo índice compuesto: `(enrollment, academic_period, is_current)`

### StudentRiskScore (`apps/analytics/models/student_risk_score.py`)
- `unique_together`: Reemplazado por `UniqueConstraint(fields=['enrollment', 'academic_period', 'model_version'], name='unique_enrollment_period_model_version')`
- Esto permite múltiples versiones del score por estudiante/período

## Archivos Eliminados

| Archivo | Razón |
|---------|-------|
| `apps/grading/models/learning_report.py` | Modelo eliminado del MVP |
| `apps/behavior/models/diagnostic_evaluation.py` | Modelo eliminado del MVP |
| `apps/behavior/models/socioemotional_area.py` | Modelo eliminado del MVP |
| `apps/behavior/models/development_level.py` | Modelo eliminado del MVP |
| `apps/behavior/models/socioemotional_skill.py` | Modelo eliminado del MVP |
| `apps/behavior/models/skill_evaluation.py` | Modelo eliminado del MVP |
| `apps/behavior/repositories/diagnostic_evaluation_repository.py` | Repository eliminada |
| `apps/behavior/repositories/socioemotional_skill_repository.py` | Repository eliminada |
| `apps/behavior/repositories/skill_evaluation_repository.py` | Repository eliminada |

## Archivos Modificados (limpieza post-migración)

| Archivo | Cambio |
|---------|--------|
| `apps/grading/models/__init__.py` | Removido import de LearningReport |
| `apps/grading/api/serializers.py` | Removido LearningReportSerializer |
| `apps/grading/tasks.py` | Removido LearningReportSyncHandler |
| `apps/behavior/models/__init__.py` | Removido imports de modelos eliminados |
| `apps/behavior/api/serializers.py` | Removido SocioemotionalSkillSerializer, SkillEvaluationSerializer, DiagnosticEvaluationSerializer |
| `apps/behavior/api/views.py` | Removido SocioemotionalSkillViewSet, SkillEvaluationViewSet, DiagnosticEvaluationViewSet |
| `apps/behavior/api/urls.py` | Removido registro de routers eliminados |
| `apps/behavior/admin.py` | Removido Admin para SocioemotionalSkill, SkillEvaluation, DiagnosticEvaluation |
| `apps/behavior/tasks.py` | Removido SkillEvaluationSyncHandler, DiagnosticEvaluationSyncHandler |
| `apps/behavior/repositories/__init__.py` | Removido imports de repositories eliminados |
| `apps/core/api/role_handlers.py` | Removido SkillEvaluation de ALLOWED_MODELS |
| `apps/core/api/filters.py` | Removido SocioemotionalSkill de PUBLIC_CATALOGS |
| `apps/core/management/commands/seed_catalogs.py` | Removido seeding de modelos eliminados |
| `apps/core/management/commands/seed_test_data.py` | Removido _create_socioemotional_skills(), limpiado school_year de Enrollment/SubjectOffering |
| `apps/core/constants/permissions.py` | Removido 12 permisos de BehaviorPermissions |
| `apps/iam/management/commands/seed_permissions.py` | Removido description_overrides y ROLES_CONFIG de modelos eliminados |
| `apps/integration/services/conflict_resolver.py` | Removido STRATEGIES de modelos eliminados |
| `apps/core/tests/test_seed_catalogs.py` | Removido imports y counts de modelos eliminados |
| `apps/core/tests/test_integration_workflows.py` | Renombrado de test_phase8_functional.py, removido LearningReport, limpiado school_year |
| `apps/behavior/tests/test_api_gaps.py` | Removido tests de modelos eliminados |
| `apps/behavior/tests/test_repositories.py` | Removido tests de repositories eliminados |
| `apps/behavior/tests/test_api_permissions.py` | Removido tests de permisos eliminados |

## Archivos Creados

| Archivo | Propósito |
|---------|----------|
| `apps/core/utils/responses.py` | Helper functions `ok_response()` y `error_response()` |
| `CHANGELOG_MIGRACION_MODELOS.md` | Este documento |

## Migraciones

Todas las migraciones fueron recreadas desde cero (`makemigrations`). No hay migraciones intermedias.

```
apps/institutions/migrations/0001_initial.py
apps/people/migrations/0001_initial.py
apps/iam/migrations/0001_initial.py
apps/integration/migrations/0001_initial.py
apps/students/migrations/0001_initial.py
apps/academic/migrations/0001_initial.py
apps/analytics/migrations/0001_initial.py
apps/attendance/migrations/0001_initial.py
apps/core/migrations/0001_initial.py
apps/grading/migrations/0001_initial.py
apps/behavior/migrations/0001_initial.py
```

## Próximos Pasos

1. Ejecutar `python manage.py migrate` para aplicar las migraciones
2. Ejecutar tests de consistencia para verificar las validaciones
3. Verificar que seed_catalogs y seed_test_data funcionen correctamente