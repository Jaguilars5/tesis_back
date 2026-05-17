from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RiskFactorViewSet, StudentFeatureSnapshotViewSet, StudentRiskFactorViewSet, StudentRiskScoreViewSet

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

urlpatterns = [
    path("", include(router.urls)),
]
