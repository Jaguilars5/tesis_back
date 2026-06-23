# Módulo `analytics` — Estructura

## Árbol de archivos

```
analytics/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py
├── tasks.py                    # Cálculo de riesgo, clustering, auto-alertas, refresh vistas
├── tasks_handlers.py           # EarlyAlertSyncHandler
├── README.md
│
├── models/
│   ├── __init__.py             # 5 modelos exportados
│   ├── student_risk_score.py   # StudentRiskScore
│   ├── student_risk_factor.py  # StudentRiskFactor
│   ├── student_feature_snapshot.py  # StudentFeatureSnapshot
│   ├── risk_factor.py          # RiskFactor
│   └── early_alert.py          # EarlyAlert (AlertTypeChoices, UrgencyLevelChoices internos)
│
├── repositories/
│   ├── __init__.py             # 5 repositorios exportados
│   ├── analytics_repo.py       # StudentRiskScoreRepository, StudentFeatureSnapshotRepository
│   ├── early_alert_repository.py   # EarlyAlertRepository
│   ├── risk_factor_repository.py   # RiskFactorRepository
│   └── student_risk_factor_repository.py  # StudentRiskFactorRepository
│
├── services/
│   ├── __init__.py
│   ├── analytics_service.py    # AnalyticsService
│   ├── early_alert_service.py  # EarlyAlertService (3 reglas)
│   ├── feature_builder.py      # AcademicRiskFeatureBuilder
│   ├── dashboard_service.py    # DashboardService
│   ├── csv_export_service.py   # CSVExportService
│   └── clustering_service.py   # StudentClusteringService (KMeans)
│
├── api/
│   ├── README.md
│   ├── serializers.py          # 5 serializers
│   ├── views.py                # 6 ViewSets (4 ModelViewSet + 2 ReadOnly + 1 ViewSet)
│   └── urls.py                 # Router con 6 registros
│
├── ml/
│   ├── __init__.py
│   ├── train_model.py          # RiskModelTrainer (GradientBoostingClassifier)
│   └── risk_model.joblib       # Artefacto entrenado (opcional)
│
├── management/
│   └── commands/
│       ├── __init__.py
│       └── train_risk_model.py # Management command
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_gaps.py
    ├── test_api_permissions.py
    ├── test_models.py
    ├── test_repositories.py
    ├── test_risk_model.py
    ├── test_services.py
    └── test_viewsets.py
```

## Serializers (5)

| Serializer | Modelo | Campos readonly |
|------------|--------|-----------------|
| `StudentRiskScoreSerializer` | StudentRiskScore | `enrollment_name`, `academic_period_name`, `risk_factors` (anidado) |
| `StudentRiskFactorSerializer` | StudentRiskFactor | `risk_factor_name` |
| `StudentFeatureSnapshotSerializer` | StudentFeatureSnapshot | `enrollment_name`, `academic_period_name` |
| `RiskFactorSerializer` | RiskFactor | — |
| `EarlyAlertSerializer` | EarlyAlert | `enrollment_name`, `academic_period_name`, `attended_by_user_name` |

## ViewSets (6 registrados en router)

| ViewSet | Endpoint | Tipo |
|---------|----------|------|
| `StudentRiskScoreViewSet` | `student-risk-scores/` | Read + actions (calculate, batch_calculate) |
| `StudentFeatureSnapshotViewSet` | `feature-snapshots/` | Read-only |
| `RiskFactorViewSet` | `risk-factors/` | Read-only |
| `StudentRiskFactorViewSet` | `student-risk-factors/` | Read-only |
| `EarlyAlertViewSet` | `early-alerts/` | CRUD + mark_attended |
| `DashboardViewSet` | `dashboard/` | 5 actions (overview, risk_distribution, students_at_risk, export_csv, section_summary) |

## Workflow

```
Transaccional (asistencia, notas, conducta)
    ↓
AcademicRiskFeatureBuilder.build()
    → snapshot JSON (conducta, asistencia, calificaciones)
    ↓
build_persistence_metrics() → StudentFeatureSnapshot.create()
    ↓
calculate_academic_risk() → reglas semáforo o ML opcional
    ↓
StudentRiskScore.create() + _populate_risk_factors()
    ↓
EarlyAlertService.evaluate_student() → 3 reglas → EarlyAlert.create()
    ↓
DashboardService.get_overview() / clustering / CSV export
```

## Guía de imports

```python
from apps.analytics.models import StudentRiskScore, StudentFeatureSnapshot, EarlyAlert, RiskFactor

from apps.analytics.repositories import StudentRiskScoreRepository, EarlyAlertRepository

from apps.analytics.services.analytics_service import AnalyticsService
from apps.analytics.services.early_alert_service import EarlyAlertService
from apps.analytics.services.dashboard_service import DashboardService
from apps.analytics.services.csv_export_service import CSVExportService
from apps.analytics.services.clustering_service import StudentClusteringService
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder

from apps.analytics.tasks import calculate_student_academic_risk_task, auto_generate_early_alerts
```
