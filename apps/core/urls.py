from rest_framework.routers import DefaultRouter
from apps.core.api.views import SyncQueueViewSet

router = DefaultRouter()
router.register(r"sync-queue", SyncQueueViewSet, basename="sync-queue")

urlpatterns = router.urls
