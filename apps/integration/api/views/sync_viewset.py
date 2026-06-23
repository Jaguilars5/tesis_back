from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...repositories import SyncQueueRepository
from ...services.sync_service import SyncQueueService
from ..serializers import SyncQueueSerializer
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import integration as perm
from apps.core.utils import ok_response


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

    def get_permissions(self):
        # push/pull son usados por la app móvil: solo requieren autenticación,
        # no un permiso específico (comportamiento histórico preservado).
        if self.action in ("push", "pull"):
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        instance = serializer.save()
        from apps.integration.tasks.sync_tasks import process_sync_queue_item
        process_sync_queue_item.delay(instance.id)

    @extend_schema(summary="Recibir lote de operaciones del cliente", tags=["integration"])
    def push(self, request):
        summary = SyncQueueService.process_push(
            user=request.user,
            operations=request.data.get("operations", []),
        )
        return ok_response(summary)

    @extend_schema(summary="Entregar cambios pendientes al cliente", tags=["integration"])
    def pull(self, request):
        results = SyncQueueService.pull_changes(
            since=request.query_params.get("since"),
            source_table=request.query_params.get("source_table"),
        )
        return ok_response({"count": len(results), "results": results})
