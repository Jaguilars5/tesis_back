# Módulo `grading` — Estructura

## Árbol de archivos

```
grading/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py
├── tasks.py                    # Handlers sync: 5 handlers
├── README.md
│
├── models/
│   ├── __init__.py             # 15 modelos exportados
│   ├── student_note.py         # StudentNote (TimeStampedModel, SyncableModel)
│   ├── evaluation_block.py     # EvaluationBlock + EvaluationBlockTypeChoices
│   ├── block_component.py      # BlockComponent
│   ├── component_indicator.py  # ComponentIndicator
│   ├── evaluative_activity.py  # EvaluativeActivity (TimeStampedModel, SyncableModel)
│   ├── grade_change_history.py # GradeChangeHistory
│   ├── period_grade_summary.py # PeriodGradeSummary + PromotionStatusChoices
│   ├── recovery_process.py     # RecoveryProcess (TimeStampedModel, SyncableModel)
│   ├── recovery_session.py     # RecoverySession (TimeStampedModel, SyncableModel)
│   ├── recovery_process_history.py  # RecoveryProcessHistory
│   ├── learning_report.py      # LearningReport
│   ├── qualitative_scale.py    # QualitativeScale
│   ├── qualitative_scale_sublevel.py  # QualitativeScaleSublevel
│   ├── activity_type.py        # ActivityType
│   └── recovery_process_type.py # RecoveryProcessType
│
├── repositories/
│   ├── __init__.py             # 14 repositorios exportados (incluye BaseRepository)
│   ├── grading_repo.py         # 10 repositorios (StudentNote, GradeType, QualitativeScale, etc.)
│   ├── evaluation_repo.py      # repositorio adicional
│   ├── period_grade_summary_repository.py
│   └── recovery_process_repository.py
│
├── services/
│   ├── __init__.py
│   ├── grading_service.py      # GradingService
│   ├── evaluation_service.py   # EvaluationService
│   ├── grade_calculation_service.py  # GradeCalculationService
│   └── recovery_process_service.py   # RecoveryProcessService
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers.py          # 14 serializers (sin EvaluationType, PromotionStatus, ProjectNote)
│   ├── views.py                # 12 ViewSets (sin EvaluationType, PromotionStatus, ProjectNote, LearningReport, RecoverySession)
│   └── urls.py                 # Router con 12 registros
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_gaps.py
    ├── test_evaluation.py
    ├── test_models.py
    ├── test_services.py
    └── test_viewsets.py
```

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

from apps.grading.repositories import StudentNoteRepository, GradeTypeRepository

from apps.grading.api.serializers import StudentNoteSerializer, GradeTypeSerializer
from apps.grading.api.views import StudentNoteViewSet, GradeTypeViewSet
```
