# Módulo `grading` — Estructura

## Árbol de archivos

```
grading/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py
├── tasks.py                    # Handlers sync: 6 handlers
├── README.md
│
├── models/
│   ├── __init__.py             # 19 modelos exportados
│   ├── student_note.py         # StudentNote (TimeStampedModel, SyncableModel)
│   ├── evaluation_block.py     # EvaluationBlock (+ subject_offering FK)
│   ├── block_component.py      # BlockComponent
│   ├── component_indicator.py  # ComponentIndicator
│   ├── evaluative_activity.py  # EvaluativeActivity (TimeStampedModel, SyncableModel)
│   ├── grade_change_history.py # GradeChangeHistory (extendido Fase 4)
│   ├── period_grade_summary.py # PeriodGradeSummary (+ calculated_by, approved_by)
│   ├── recovery_process.py     # RecoveryProcess (TimeStampedModel, SyncableModel)
│   ├── recovery_session.py     # RecoverySession (TimeStampedModel, SyncableModel)
│   ├── recovery_process_history.py  # RecoveryProcessHistory
│   ├── learning_report.py      # LearningReport
│   ├── project_note.py         # ProjectNote (TimeStampedModel, SyncableModel)
│   ├── grade_type.py           # GradeType (+ M2M a AcademicSublevel)
│   ├── qualitative_scale.py    # QualitativeScale
│   ├── qualitative_scale_sublevel.py  # QualitativeScaleSublevel
│   ├── evaluation_type.py      # EvaluationType
│   ├── activity_type.py        # ActivityType
│   ├── promotion_status.py     # PromotionStatus
│   └── recovery_process_type.py # RecoveryProcessType (+ campos Fase 3)
│
├── repositories/
│   ├── __init__.py             # 14 repositorios
│   ├── grading_repo.py         # StudentNoteRepository, GradeTypeRepository, QualitativeScaleRepository,
│                               #   EvaluationTypeRepository, ActivityTypeRepository,
│                               #   PromotionStatusRepository, RecoveryProcessTypeRepository,
│                               #   EvaluationBlockRepository, BlockComponentRepository,
│                               #   ComponentIndicatorRepository, EvaluativeActivityRepository
│   ├── evaluation_repo.py      # EvaluationBlockRepository adicional
│   ├── period_grade_summary_repository.py
│   └── recovery_process_repository.py
│
├── services/
│   ├── __init__.py
│   ├── grading_service.py          # GradingService (notas, asistencia, incidentes)
│   ├── evaluation_service.py       # EvaluationService (bloques, jerarquía)
│   ├── grade_calculation_service.py # GradeCalculationService (promedios)
│   └── recovery_process_service.py # RecoveryProcessService (recuperación)
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 17 serializers
│   ├── views.py                # 14 ViewSets sobre BaseGradingViewSet
│   └── urls.py                 # Router con 16 registros
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_gaps.py
    ├── test_api_permissions.py
    ├── test_evaluation.py
    ├── test_models.py
    ├── test_repositories.py
    ├── test_services.py
    └── test_viewsets.py
```

## Serializers (17)

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `StudentNoteSerializer` | StudentNote | `enrollment_name`, `evaluative_activity_title`, `grade_type_name`, `qualitative_scale_name` |
| `EvaluationBlockSerializer` | EvaluationBlock | `academic_period_name` |
| `BlockComponentSerializer` | BlockComponent | `evaluation_block_name` |
| `ComponentIndicatorSerializer` | ComponentIndicator | `block_component_name` |
| `EvaluativeActivitySerializer` | EvaluativeActivity | `component_indicator_name`, `teacher_subject_section_name` |
| `GradeChangeHistorySerializer` | GradeChangeHistory | `student_note_name`, `modified_by_user_name` |
| `PeriodGradeSummarySerializer` | PeriodGradeSummary | `enrollment_name`, `subject_offering_name`, `academic_period_name`, `qualitative_scale_name` |
| `RecoveryProcessSerializer` | RecoveryProcess | `period_grade_summary_name`, `managed_by_user_name` |
| `ProjectNoteSerializer` | ProjectNote | `enrollment_name`, `interdisciplinary_project_title` |
| `LearningReportSerializer` | LearningReport | `enrollment_name`, `academic_period_name`, `created_by_name`, `evaluated_by_name` |
| `RecoverySessionSerializer` | RecoverySession | `recovery_process_name` |
| `GradeTypeSerializer` | GradeType | — |
| `QualitativeScaleSerializer` | QualitativeScale | — |
| `EvaluationTypeSerializer` | EvaluationType | — |
| `ActivityTypeSerializer` | ActivityType | — |
| `PromotionStatusSerializer` | PromotionStatus | — |
| `RecoveryProcessTypeSerializer` | RecoveryProcessType | — |

## ViewSets (14 registrados en router)

| ViewSet | Endpoint | action_permissions |
|---------|----------|-------------------|
| `StudentNoteViewSet` | `student-notes/` | VIEW/CREATE/UPDATE/DELETE_NOTE |
| `EvaluationBlockViewSet` | `evaluation-blocks/` | VIEW/CREATE/UPDATE/DELETE_EVALUATION_MACRO |
| `BlockComponentViewSet` | `block-components/` | VIEW/CREATE/UPDATE/DELETE_EVALUATION_CRITERIA |
| `ComponentIndicatorViewSet` | `component-indicators/` | VIEW/CREATE/UPDATE/DELETE_EVALUATION_SUBCRITERIA |
| `EvaluativeActivityViewSet` | `evaluative-activities/` | VIEW/CREATE/UPDATE/DELETE_CLASS_ASSIGNMENT |
| `GradeChangeHistoryViewSet` | `grade-history/` | VIEW_GRADE_HISTORY (read-only) |
| `PeriodGradeSummaryViewSet` | `period-grade-summaries/` | VIEW/CREATE/UPDATE/DELETE_GRADESUMMARY |
| `RecoveryProcessViewSet` | `recovery-processes/` | VIEW/CREATE/UPDATE/DELETE_RECOVERYPROCESS |
| `ProjectNoteViewSet` | `project-notes/` | VIEW/CREATE/UPDATE/DELETE_PROJECTNOTE |
| `GradeTypeViewSet` | `grade-types/` | VIEW/CREATE/UPDATE/DELETE_GRADE_TYPE |
| `QualitativeScaleViewSet` | `qualitative-scales/` | VIEW/CREATE/UPDATE/DELETE_QUALITATIVE_SCALE |
| `EvaluationTypeViewSet` | `evaluation-types/` | VIEW/CREATE/UPDATE/DELETE_EVALUATION_TYPE |
| `ActivityTypeViewSet` | `activity-types/` | VIEW/CREATE/UPDATE/DELETE_ACTIVITY_TYPE |
| `PromotionStatusViewSet` | `promotion-statuses/` | VIEW/CREATE/UPDATE/DELETE_PROMOTION_STATUS |
| `RecoveryProcessTypeViewSet` | `recovery-process-types/` | VIEW/CREATE/UPDATE/DELETE_RECOVERY_PROCESS_TYPE |

## Workflow

```
AcademicPeriod + SubjectOffering
  └─ EvaluationBlock (weight_percentage)
      └─ BlockComponent (internal_weight)
          └─ ComponentIndicator (internal_weight)
              └─ EvaluativeActivity (max_score)
                  └─ StudentNote (numeric_score, grading_mode)
                      ↓
PeriodGradeSummary (formative_avg, summative_avg, final_avg_truncated)
  ├─ requires_recovery=true → RecoveryProcess → RecoverySession
  └─ LearningReport (consolidado final)
```

## Guía de imports

```python
from apps.grading.models import StudentNote, EvaluationBlock, PeriodGradeSummary, LearningReport
from apps.grading.services.grading_service import GradingService
from apps.grading.repositories.grading_repo import StudentNoteRepository
from apps.grading.api.serializers import StudentNoteSerializer
from apps.grading.api.views import StudentNoteViewSet
```
