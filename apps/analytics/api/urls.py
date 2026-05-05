from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StudentFeatureSnapshotViewSet, StudentRiskScoreViewSet

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

urlpatterns = [
    path("", include(router.urls)),
]
