from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlertTypeViewSet, EarlyAlertViewSet, RiskFactorViewSet, StudentFeatureSnapshotViewSet, StudentRiskFactorViewSet, StudentRiskScoreViewSet, UrgencyLevelViewSet

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
router.register(r"alert-types", AlertTypeViewSet, basename="alert-type")
router.register(r"urgency-levels", UrgencyLevelViewSet, basename="urgency-level")

urlpatterns = [
    path("", include(router.urls)),
]
