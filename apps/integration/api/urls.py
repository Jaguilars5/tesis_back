from rest_framework.routers import DefaultRouter
from .views import SyncOperationViewSet, SyncQueueViewSet, SyncStatusViewSet

router = DefaultRouter()
router.register(r"sync-queue", SyncQueueViewSet, basename="sync-queue")
router.register(r"sync-operations", SyncOperationViewSet, basename="sync-operation")
router.register(r"sync-statuses", SyncStatusViewSet, basename="sync-status")

urlpatterns = router.urls
