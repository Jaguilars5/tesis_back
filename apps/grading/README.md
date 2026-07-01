# Módulo `grading` — Calificaciones, Evaluación y Recuperación Académica

> Gestión de calificaciones, estructura evaluativa, promedios de período, procesos de recuperación, informes de aprendizaje y auditoría de cambios.

## Modelos (15)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `StudentNote` | Calificación individual por actividad | `enrollment`, `evaluative_activity`, `grade_type`, `grading_mode` (NUMERIC/QUALITATIVE), `numeric_score`, `qualitative_scale`, `manually_overridden`, `teacher_observation`, `created_by`, `modified_by`. Unique: `(enrollment, evaluative_activity)`. Hereda `SyncableModel` |
| `EvaluationBlock` | Bloque evaluativo por período + asignatura | `code`, `academic_period`, `subject_offering`, `name`, `tipo` (choices: FORMATIVA/SUMATIVA/PROJECT), `weight_percentage`, `is_active` |
| `BlockComponent` | Componente dentro de un bloque | `evaluation_block`, `name`, `internal_weight` |
| `ComponentIndicator` | Indicador dentro de un componente | `block_component`, `name`, `internal_weight`, `code` |
| `EvaluativeActivity` | Tarea, examen o actividad calificable | `component_indicator`, `teacher_subject_section`, `title`, `activity_type`, `max_score`, `due_date`. Hereda `SyncableModel` |
| `PeriodGradeSummary` | Promedio consolidado por estudiante, asignatura y período | `enrollment`, `subject_offering`, `academic_period`, `formative_avg`, `summative_avg`, `final_avg_truncated`, `qualitative_scale`, `requires_recovery`, `promotion_status` (choices: approved/failed/recovery), `calculated_by`, `approved_by`, `calculated_at`. Unique: `(enrollment, subject_offering, academic_period)` |
| `GradeChangeHistory` | Auditoría de cambios en notas | `student_note`, `modified_by_user`, `previous_score`, `new_score`, `previous_qualitative`, `new_qualitative`, `reason`, `reason_code`, `origin`, `device_origin`, `modified_at` |
| `RecoveryProcess` | Proceso de recuperación académica | `period_grade_summary`, `subject_offering`, `managed_by_user`, `process_type`, `initial_grade`, `reinforcement_grade`, `improvement_eval_grade`, `final_calculated_grade`, `family_notified`, `start_date`, `end_date`. Hereda `SyncableModel` |
| `RecoverySession` | Sesión de refuerzo dentro de un proceso | `recovery_process`, `session_date`, `duration_minutes`, `topics_covered`, `student_present`, `teacher_observation`. Hereda `SyncableModel` |
| `RecoveryProcessHistory` | Historial de cambios en procesos de recuperación | `recovery_process`, `action`, `previous_grade`, `new_grade`, `previous_status`, `new_status`, `notes`, `changed_by` |
| `LearningReport` | Informe de aprendizaje consolidado | `enrollment`, `academic_period`, `formative_avg`, `summative_avg`, `final_avg`, `attendance_rate`, `general_observations`, `recommendations`, `created_by`, `evaluated_by`, `approved_by`, `is_final`. Unique: `(enrollment, academic_period)` |
| `GradeType` | **No existe como modelo** — referenciado en código pero sin archivo de modelo. `GradeTypeRepository` y `GradeTypeViewSet` existen pero fallarían al importar `GradeType` |
| `QualitativeScale` | Catálogo: SE, SA, AC, NA | `code` (unique), `name`, `description`, `numeric_equivalence`, `is_active` |
| `ActivityType` | Catálogo: TAREA, EXAMEN, PROYECTO, etc. | `code` (unique), `name`, `is_active` |
| `RecoveryProcessType` | Catálogo de tipos de recuperación | `code` (unique), `name`, `allows_improvement_eval`, `allows_suppletorio`, `min_grade_to_access`, `max_recovery_attempts`, `is_active` |

> **Nota:** `EvaluationType`, `PromotionStatus` y `ProjectNote` **no existen como modelos**. Son `TextChoices` internos (`EvaluationBlockTypeChoices` en `evaluation_block.py`, `PromotionStatusChoices` en `period_grade_summary.py`). `ProjectNote` fue eliminado (migración 0004). Los endpoints `evaluation-types/`, `promotion-statuses/` y `project-notes/` **no existen**.

## Repositorios (14 en 4 archivos)

| Archivo | Repositorios |
|---------|-------------|
| `grading_repo.py` | StudentNote, GradeType, QualitativeScale, EvaluationBlock, BlockComponent, ComponentIndicator, EvaluativeActivity, GradeChangeHistory, ActivityType, RecoveryProcessType |
| `period_grade_summary_repository.py` | PeriodGradeSummaryRepository |
| `recovery_process_repository.py` | RecoveryProcessRepository |
| `evaluation_repo.py` | EvaluationBlockRepository adicional |

## Servicios (4)

| Servicio | Descripción |
|----------|-------------|
| `GradingService` | CRUD de notas, creación de asistencia/incidentes desde grading |
| `EvaluationService` | Cálculo de promedios por bloque, jerarquía evaluativa, historial de cambios |
| `GradeCalculationService` | Cálculo automático de promedios ponderados y finales |
| `RecoveryProcessService` | Lógica de recuperación (supletorias, recálculo) |

## API — Endpoints Registrados (12)

| Método | Endpoint | ViewSet |
|--------|----------|---------|
| GET/POST | `/api/grading/student-notes/` | StudentNoteViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/student-notes/{id}/` | StudentNoteViewSet |
| GET/POST | `/api/grading/evaluation-blocks/` | EvaluationBlockViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/evaluation-blocks/{id}/` | EvaluationBlockViewSet |
| GET/POST | `/api/grading/block-components/` | BlockComponentViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/block-components/{id}/` | BlockComponentViewSet |
| GET/POST | `/api/grading/component-indicators/` | ComponentIndicatorViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/component-indicators/{id}/` | ComponentIndicatorViewSet |
| GET/POST | `/api/grading/evaluative-activities/` | EvaluativeActivityViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/evaluative-activities/{id}/` | EvaluativeActivityViewSet |
| GET | `/api/grading/grade-history/` | GradeChangeHistoryViewSet (read-only) |
| GET/POST | `/api/grading/period-grade-summaries/` | PeriodGradeSummaryViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/period-grade-summaries/{id}/` | PeriodGradeSummaryViewSet |
| GET/POST | `/api/grading/recovery-processes/` | RecoveryProcessViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/recovery-processes/{id}/` | RecoveryProcessViewSet |
| GET/POST | `/api/grading/grade-types/` | GradeTypeViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/grade-types/{id}/` | GradeTypeViewSet |
| GET/POST | `/api/grading/qualitative-scales/` | QualitativeScaleViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/qualitative-scales/{id}/` | QualitativeScaleViewSet |
| GET/POST | `/api/grading/activity-types/` | ActivityTypeViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/activity-types/{id}/` | ActivityTypeViewSet |
| GET/POST | `/api/grading/recovery-process-types/` | RecoveryProcessTypeViewSet |
| GET/PUT/PATCH/DEL | `/api/grading/recovery-process-types/{id}/` | RecoveryProcessTypeViewSet |

> **Nota:** `LearningReport` y `RecoverySession` tienen serializers pero **no tienen ViewSets**. No existen endpoints para `evaluation-types/`, `promotion-statuses/` ni `project-notes/`.

## Sincronización

Modelos que heredan `SyncableModel`: `StudentNote`, `EvaluativeActivity`, `RecoveryProcess`, `RecoverySession`, `LearningReport`.

Handlers registrados (5): `StudentNoteSyncHandler`, `EvaluativeActivitySyncHandler`, `RecoveryProcessSyncHandler`, `RecoverySessionSyncHandler`, `LearningReportSyncHandler`.

## Tests

```bash
python manage.py test apps.grading --settings=config.settings.test
```
