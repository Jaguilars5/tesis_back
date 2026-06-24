"""
URLs para el módulo de riesgo estudiantil.

Registra los ViewSets con AnalyticsRouter.
"""

from apps.analytics.api.routers import AnalyticsRouter

from .api.views import (
    RiskFactorViewSet,
    StudentRiskScoreViewSet,
    StudentRiskFactorViewSet,
    StudentFeatureSnapshotViewSet,
    RiskScoringConfigViewSet,
)

router = AnalyticsRouter()
router.register(r"risk-factors", RiskFactorViewSet, basename="risk-factor")
router.register(
    r"student-risk-scores", StudentRiskScoreViewSet, basename="student-risk-score"
)
router.register(
    r"student-risk-factors",
    StudentRiskFactorViewSet,
    basename="student-risk-factor",
)
router.register(
    r"feature-snapshots",
    StudentFeatureSnapshotViewSet,
    basename="feature-snapshot",
)
router.register(r"scoring-config", RiskScoringConfigViewSet, basename="scoring-config")

urlpatterns = router.urls
