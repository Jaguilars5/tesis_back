from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SyncOperationViewSet, SyncQueueViewSet, SyncStatusViewSet
from .views.sync_bulk_view import sync_push, sync_pull

router = DefaultRouter()
router.register(r"sync-queue", SyncQueueViewSet, basename="sync-queue")
router.register(r"sync-operations", SyncOperationViewSet, basename="sync-operation")
router.register(r"sync-statuses", SyncStatusViewSet, basename="sync-status")

urlpatterns = router.urls + [
    path("sync/push/", sync_push, name="sync-push"),
    path("sync/pull/", sync_pull, name="sync-pull"),
]
