from apps.grading.api.routers import GradingRouter

from .api.views import EvaluationBlockViewSet, BlockComponentViewSet, EvaluativeActivityViewSet

router = GradingRouter()
router.register(r"evaluation-blocks", EvaluationBlockViewSet, basename="evaluation-block")
router.register(r"block-components", BlockComponentViewSet, basename="block-component")
router.register(r"evaluative-activities", EvaluativeActivityViewSet, basename="evaluative-activity")

urlpatterns = router.urls
