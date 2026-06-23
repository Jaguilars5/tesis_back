from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SyncQueueViewSet

router = DefaultRouter()
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
]
