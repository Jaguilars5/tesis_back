from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.analytics.early_alert.api.views import EarlyAlertViewSet
from .views import DashboardViewSet, RiskFactorViewSet, RiskScoringConfigViewSet, StudentFeatureSnapshotViewSet, StudentRiskFactorViewSet, StudentRiskScoreViewSet

router = DefaultRouter()
router.register(
    r"student-risk-scores",
    StudentRiskScoreViewSet,
    basename="student-risk-score",
)
router.register(
    r"feature-snapshots",
    StudentFeatureSnapshotViewSet,
    basename="feature-snapshot",
)

router.register(r"risk-factors", RiskFactorViewSet, basename="risk-factor")
router.register(r"student-risk-factors", StudentRiskFactorViewSet, basename="student-risk-factor")
router.register(r"early-alerts", EarlyAlertViewSet, basename="early-alert")

router.register(r"dashboard", DashboardViewSet, basename="dashboard")
router.register(r"scoring-config", RiskScoringConfigViewSet, basename="scoring-config")

urlpatterns = [
    path("", include(router.urls)),
]
