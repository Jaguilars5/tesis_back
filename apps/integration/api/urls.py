from django.urls import path
from .routers import IntegrationRouter
from .views import SyncQueueViewSet

router = IntegrationRouter()
router.register(r"sync-queue", SyncQueueViewSet, basename="sync-queue")

urlpatterns = router.urls + [
    path(
        "sync/push/",
        SyncQueueViewSet.as_view({"post": "push"}),
        name="sync-push",
    ),
    path(
        "sync/pull/",
        SyncQueueViewSet.as_view({"get": "pull"}),
        name="sync-pull",
    ),
    path(
        "sync/rollback/",
        SyncQueueViewSet.as_view({"post": "rollback"}),
        name="sync-rollback",
    ),
]
