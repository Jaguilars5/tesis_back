# Módulo `grading` — Calificaciones, Evaluación y Recuperación Académica

> Gestión de calificaciones, estructura evaluativa (bloques → componentes → indicadores → actividades), promedios de período, procesos de recuperación, informes de aprendizaje y auditoría de cambios.

## Modelos (19)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `StudentNote` | Calificación individual por actividad | `enrollment`, `evaluative_activity`, `grade_type`, `grading_mode` (NUMERIC/QUALITATIVE), `numeric_score`, `qualitative_scale`, `manually_overridden`, `teacher_observation`, `created_by`, `modified_by`. Hereda `SyncableModel`. Unique: `(enrollment, evaluative_activity)` |
| `EvaluationBlock` | Bloque evaluativo por período + asignatura | `academic_period`, `subject_offering`, `name`, `evaluation_type`, `weight_percentage`, `is_active` |
| `BlockComponent` | Componente dentro de un bloque | `evaluation_block`, `name`, `internal_weight` |
| `ComponentIndicator` | Indicador dentro de un componente | `block_component`, `name`, `internal_weight`, `code` |
| `EvaluativeActivity` | Tarea, examen o actividad calificable | `component_indicator`, `teacher_subject_section`, `title`, `activity_type`, `max_score`, `due_date`, `is_interdisciplinary_project`. Hereda `SyncableModel` |
| `PeriodGradeSummary` | Promedio consolidado por estudiante, asignatura y período | `enrollment`, `subject_offering`, `academic_period`, `formative_avg`, `summative_avg`, `final_avg_truncated`, `qualitative_scale`, `requires_recovery`, `promotion_status`, `calculated_by`, `approved_by`, `calculated_at`. Unique: `(enrollment, subject_offering, academic_period)` |
| `GradeChangeHistory` | Auditoría de cambios en notas (Fase 4 extendido) | `student_note`, `modified_by_user`, `created_by`, `previous_score`, `new_score`, `previous_qualitative`, `new_qualitative`, `reason`, `reason_code` (ERROR_CAPTURA, CORRECCION_DOCENTE, RECUPERACION, etc.), `origin` (MANUAL/RECOVERY/IMPORT/SYNC), `device_origin`, `modified_at` |
| `RecoveryProcess` | Proceso de recuperación académica | `period_grade_summary`, `subject_offering`, `managed_by_user`, `process_type`, `initial_grade`, `reinforcement_grade`, `improvement_eval_grade`, `final_calculated_grade`, `family_notified`, `family_notification_date`, `start_date`, `end_date`, `reinforcement_plan`, `objectives`, `observations`. Hereda `SyncableModel` |
| `RecoverySession` | Sesión de refuerzo dentro de un proceso | `recovery_process`, `session_date`, `duration_minutes`, `topics_covered`, `student_present`, `teacher_observation`. Hereda `SyncableModel` |
| `LearningReport` | Informe de aprendizaje consolidado | `enrollment`, `academic_period`, `formative_avg`, `summative_avg`, `final_avg`, `attendance_rate`, `behavior_scale`, `general_observations`, `recommendations`, `created_by`, `evaluated_by`, `approved_by`, `is_final`. Unique: `(enrollment, academic_period)` |
| `ProjectNote` | Nota de proyecto interdisciplinario | `enrollment`, `interdisciplinary_project`, `product_score`, `presentation_score`, `final_score`, `observation`. Hereda `SyncableModel`. Unique: `(enrollment, interdisciplinary_project)` |
| `RecoveryProcessHistory` | Historial de cambios en procesos de recuperación | `recovery_process`, `action` (STARTED/GRADE_UPDATED/SESSION_COMPLETED/COMPLETED/CANCELLED), `previous_grade`, `new_grade`, `previous_status`, `new_status`, `notes`, `changed_by` |
| `GradeType` | Catálogo: NUM, CUAL, RECUP | `code` (unique), `name`, `applicable_sublevels` (M2M a AcademicSublevel) |
| `QualitativeScale` | Catálogo: SE, SA, AC, NA | `code` (unique), `name`, `description`, `numeric_equivalence` |
| `QualitativeScaleSublevel` | Puente: escala ↔ subnivel | `scale`, `sublevel`. Unique: `(scale, sublevel)` |
| `EvaluationType` | Catálogo: DIAGNOSTICA, FORMATIVA, SUMATIVA | `code` (unique), `name`, `is_active` |
| `ActivityType` | Catálogo: TAREA, EXAMEN, PROYECTO, etc. | `code` (unique), `name`, `is_active` |
| `PromotionStatus` | Catálogo: approved, failed, recovery | `code` (unique), `name`, `is_active` |
| `RecoveryProcessType` | Catálogo extendido (Fase 3) | `code` (unique), `name`, `allows_improvement_eval`, `allows_suppletorio`, `min_grade_to_access`, `max_recovery_attempts`, `is_active` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `GradingService` | `create_student_note()`, `get_student_note()`, `list_student_notes()` | CRUD de notas con normalización a base 10 |
| `GradingService` | `create_attendance()`, `create_conduct_incident()` | Creación de asistencia/incidentes desde grading |
| `EvaluationService` | `calculate_block_grade()`, `get_grade_hierarchy()`, `create_grade_change_history()` | Cálculo de promedios por bloque, jerarquía evaluativa, historial de cambios |
| `GradeCalculationService` | Cálculo automático de promedios | Promedios ponderados y finales truncados para PeriodGradeSummary |
| `RecoveryProcessService` | Lógica de recuperación | Aplicación de notas supletorias y recálculo de promedios |

## API

| Método | Endpoint | ViewSet | Permiso requerido |
|--------|----------|---------|-------------------|
| GET/POST | `/api/grading/student-notes/` | StudentNoteViewSet | `grading.view/create_note` |
| GET/PATCH/DEL | `/api/grading/student-notes/{id}/` | StudentNoteViewSet | `grading.view/update/delete_note` |
| GET/POST | `/api/grading/evaluation-blocks/` | EvaluationBlockViewSet | `grading.view/create_evaluation_macro` |
| GET/PATCH/DEL | `/api/grading/evaluation-blocks/{id}/` | EvaluationBlockViewSet | `grading.view/update/delete_evaluation_macro` |
| GET/POST | `/api/grading/block-components/` | BlockComponentViewSet | `grading.view/create_evaluation_criteria` |
| GET/PATCH/DEL | `/api/grading/block-components/{id}/` | BlockComponentViewSet | `grading.view/update/delete_evaluation_criteria` |
| GET/POST | `/api/grading/component-indicators/` | ComponentIndicatorViewSet | `grading.view/create_evaluation_subcriteria` |
| GET/PATCH/DEL | `/api/grading/component-indicators/{id}/` | ComponentIndicatorViewSet | `grading.view/update/delete_evaluation_subcriteria` |
| GET/POST | `/api/grading/evaluative-activities/` | EvaluativeActivityViewSet | `grading.view/create_class_assignment` |
| GET/PATCH/DEL | `/api/grading/evaluative-activities/{id}/` | EvaluativeActivityViewSet | `grading.view/update/delete_class_assignment` |
| GET | `/api/grading/grade-history/` | GradeChangeHistoryViewSet (r/o) | `grading.view_grade_history` |
| GET/POST | `/api/grading/period-grade-summaries/` | PeriodGradeSummaryViewSet | `grading.view/create_gradesummary` |
| GET/PATCH/DEL | `/api/grading/period-grade-summaries/{id}/` | PeriodGradeSummaryViewSet | `grading.view/update/delete_gradesummary` |
| GET/POST | `/api/grading/recovery-processes/` | RecoveryProcessViewSet | `grading.view/create_recoveryprocess` |
| GET/PATCH/DEL | `/api/grading/recovery-processes/{id}/` | RecoveryProcessViewSet | `grading.view/update/delete_recoveryprocess` |
| GET/POST | `/api/grading/project-notes/` | ProjectNoteViewSet | `grading.view/create_projectnote` |
| GET/PATCH/DEL | `/api/grading/project-notes/{id}/` | ProjectNoteViewSet | `grading.view/update/delete_projectnote` |
| GET/POST | `/api/grading/grade-types/` | GradeTypeViewSet | `grading.view/create_grade_type` |
| GET/POST | `/api/grading/qualitative-scales/` | QualitativeScaleViewSet | `grading.view/create_qualitative_scale` |
| GET/POST | `/api/grading/evaluation-types/` | EvaluationTypeViewSet | `grading.view/create_evaluation_type` |
| GET/POST | `/api/grading/activity-types/` | ActivityTypeViewSet | `grading.view/create_activity_type` |
| GET/POST | `/api/grading/promotion-statuses/` | PromotionStatusViewSet | `grading.view/create_promotion_status` |
| GET/POST | `/api/grading/recovery-process-types/` | RecoveryProcessTypeViewSet | `grading.view/create_recovery_process_type` |

**Nota:** `LearningReport` y `RecoverySession` tienen serializers pero **no tienen ViewSets** en la API actual.

## Respuestas Enriquecidas

| Serializer | Campos readonly |
|------------|-----------------|
| `StudentNoteSerializer` | `enrollment_name`, `evaluative_activity_title`, `grade_type_name`, `qualitative_scale_name` |
| `EvaluationBlockSerializer` | `academic_period_name` |
| `BlockComponentSerializer` | `evaluation_block_name` |
| `ComponentIndicatorSerializer` | `block_component_name` |
| `EvaluativeActivitySerializer` | `component_indicator_name`, `teacher_subject_section_name` |
| `GradeChangeHistorySerializer` | `student_note_name`, `modified_by_user_name` |
| `PeriodGradeSummarySerializer` | `enrollment_name`, `subject_offering_name`, `academic_period_name`, `qualitative_scale_name` |
| `RecoveryProcessSerializer` | `period_grade_summary_name`, `managed_by_user_name` |
| `ProjectNoteSerializer` | `enrollment_name`, `interdisciplinary_project_title` |
| `LearningReportSerializer` | `enrollment_name`, `academic_period_name`, `created_by_name`, `evaluated_by_name` |
| `RecoverySessionSerializer` | `recovery_process_name` |

## Índices (Fase 5)

| Modelo | Índices |
|--------|---------|
| `StudentNote` | `(enrollment, evaluative_activity)`, `(evaluative_activity, numeric_score)`, `(sync_status)`, `(enrollment, sync_status)` |
| `PeriodGradeSummary` | `(academic_period, subject_offering)`, `(enrollment, academic_period)`, `(requires_recovery, academic_period)` |
| `EvaluativeActivity` | `(teacher_subject_section, due_date)`, `(component_indicator, due_date)` |
| `RecoveryProcess` | `(subject_offering, start_date)`, `(managed_by_user, start_date)` |
| `GradeChangeHistory` | `(student_note, modified_at)`, `(modified_by_user, modified_at)` |
| `EvaluationBlock` | `(subject_offering, academic_period)` |
| `ProjectNote` | `(interdisciplinary_project)` |
| `LearningReport` | `(academic_period, is_final)` |

## Sincronización

Modelos que heredan `SyncableModel`: `StudentNote`, `EvaluativeActivity`, `RecoveryProcess`, `RecoverySession`, `ProjectNote`, `LearningReport`.

Handlers registrados: `StudentNoteSyncHandler`, `ProjectNoteSyncHandler`, `EvaluativeActivitySyncHandler`, `RecoveryProcessSyncHandler`, `RecoverySessionSyncHandler`, `LearningReportSyncHandler`.

## Tests

```bash
python manage.py test apps.grading --settings=config.settings.test
```
