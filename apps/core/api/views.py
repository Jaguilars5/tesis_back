from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.models import SyncQueue
from apps.core.api.serializers import SyncQueueSerializer
from .permissions import HasPermission
from .pagination import StandardResultsSetPagination


class SyncQueueViewSet(viewsets.ModelViewSet):
    queryset = SyncQueue.objects.all()
    serializer_class = SyncQueueSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": "core.view_syncqueue",
        "retrieve": "core.view_syncqueue",
        "create": "core.create_syncqueue",
        "update": "core.update_syncqueue",
        "partial_update": "core.update_syncqueue",
        "destroy": "core.delete_syncqueue",
    }

    def perform_create(self, serializer):
        instance = serializer.save()
        from apps.core.tasks import process_sync_queue_item
        process_sync_queue_item.delay(instance.id)
