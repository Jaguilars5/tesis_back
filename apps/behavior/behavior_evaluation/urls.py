from apps.behavior.api.routers import BehaviorRouter

from .api.views import BehaviorEvaluationViewSet

router = BehaviorRouter()
router.register(r"behavior-evaluations", BehaviorEvaluationViewSet, basename="behavior-evaluation")

urlpatterns = router.urls
