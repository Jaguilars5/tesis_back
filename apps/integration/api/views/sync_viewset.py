from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...repositories import SyncQueueRepository
from ..serializers import SyncQueueSerializer
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import integration as perm


@extend_schema_view(
    list=extend_schema(summary="Listar cola de sincronización", tags=["integration"]),
    retrieve=extend_schema(summary="Obtener elemento de cola", tags=["integration"]),
    create=extend_schema(summary="Crear elemento en cola", tags=["integration"]),
    update=extend_schema(summary="Actualizar elemento en cola", tags=["integration"]),
    partial_update=extend_schema(summary="Actualizar elemento parcialmente", tags=["integration"]),
    destroy=extend_schema(summary="Eliminar elemento de cola", tags=["integration"]),
)
class SyncQueueViewSet(viewsets.ModelViewSet):
    serializer_class = SyncQueueSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_SYNC_QUEUE,
        "retrieve": perm.VIEW_SYNC_QUEUE,
        "create": perm.CREATE_SYNC_QUEUE,
        "update": perm.UPDATE_SYNC_QUEUE,
        "partial_update": perm.UPDATE_SYNC_QUEUE,
        "destroy": perm.DELETE_SYNC_QUEUE,
    }

    def get_queryset(self):
        return SyncQueueRepository.get_all()

    def perform_create(self, serializer):
        instance = serializer.save()
        from apps.integration.tasks.sync_tasks import process_sync_queue_item
        process_sync_queue_item.delay(instance.id)
