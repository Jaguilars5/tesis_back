from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.utils import ok_response
from ..application.serializers import SyncQueueSerializer
from ..domain.services import SyncQueueService
from ..infrastructure.repositories import SyncQueueRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar cola de sincronización", tags=["integration"]),
    retrieve=extend_schema(summary="Obtener elemento de cola", tags=["integration"]),
    create=extend_schema(summary="Crear elemento en cola", tags=["integration"]),
    update=extend_schema(summary="Actualizar elemento en cola", tags=["integration"]),
    partial_update=extend_schema(summary="Actualizar elemento parcialmente", tags=["integration"]),
    destroy=extend_schema(summary="Eliminar elemento de cola", tags=["integration"]),
    push=extend_schema(summary="Recibir lote de operaciones del cliente", tags=["integration"]),
    pull=extend_schema(summary="Entregar cambios pendientes al cliente", tags=["integration"]),
)
class SyncQueueViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SyncQueueSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = ACTION_PERMISSIONS

    def get_queryset(self):
        return SyncQueueRepository.get_all()

    def get_permissions(self):
        if self.action in ("push", "pull"):
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        instance = serializer.save()
        from ..tasks.sync_tasks import process_sync_queue_item
        process_sync_queue_item.delay(instance.id)

    def push(self, request):
        summary = SyncQueueService.process_push(
            user=request.user,
            operations=request.data.get("operations", []),
        )
        return ok_response(summary)

    def pull(self, request):
        results = SyncQueueService.pull_changes(
            since=request.query_params.get("since"),
            source_table=request.query_params.get("source_table"),
        )
        return ok_response({"count": len(results), "results": results})
