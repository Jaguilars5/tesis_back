import logging

from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.utils import ok_response, error_response
from .base import BaseIntegrationViewSet
from ..application.serializers import SyncQueueSerializer
from ..domain.services import SyncQueueService
from ..infrastructure.repositories import SyncBatchRepository, SyncQueueRepository
from ..permissions import ACTION_PERMISSIONS

from ..infrastructure.models import BatchStatusChoices

logger = logging.getLogger("apps.integration.sync")


@extend_schema_view(
    list=extend_schema(summary="Listar cola de sincronización", tags=["integration"]),
    retrieve=extend_schema(summary="Obtener elemento de cola", tags=["integration"]),
    create=extend_schema(summary="Crear elemento en cola", tags=["integration"]),
    update=extend_schema(summary="Actualizar elemento en cola", tags=["integration"]),
    partial_update=extend_schema(summary="Actualizar elemento parcialmente", tags=["integration"]),
    destroy=extend_schema(summary="Eliminar elemento de cola", tags=["integration"]),
    push=extend_schema(summary="Recibir lote de operaciones del cliente", tags=["integration"]),
    pull=extend_schema(summary="Entregar cambios pendientes al cliente", tags=["integration"]),
    rollback=extend_schema(summary="Revertir un lote de sincronización", tags=["integration"]),
)
class SyncQueueViewSet(BaseIntegrationViewSet):
    serializer_class = SyncQueueSerializer
    action_permissions = ACTION_PERMISSIONS

    def get_queryset(self):
        return SyncQueueRepository.get_all(active_only=False)

    def get_permissions(self):
        if self.action in ("push", "pull"):
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        instance = serializer.save()
        from ..tasks.sync_tasks import process_sync_queue_item
        transaction.on_commit(
            lambda id=instance.id: process_sync_queue_item.delay(id)
        )

    def push(self, request):
        operations = request.data.get("operations", [])
        client_batch_id = request.data.get("client_batch_id")
        logger.info(
            "[VIEW] POST push de user=%s: %d operacion(es) en el body. "
            "client_batch_id=%s. Claves del body=%s",
            getattr(request.user, "id", None),
            len(operations) if isinstance(operations, list) else "N/A",
            client_batch_id,
            sorted(request.data.keys()) if hasattr(request.data, "keys") else "N/A",
        )
        if not operations:
            logger.warning(
                "[VIEW] POST push SIN operaciones. Verifica que el cliente envie "
                "{'operations': [...]} y no otra estructura. body_keys=%s",
                sorted(request.data.keys()) if hasattr(request.data, "keys") else "N/A",
            )
        summary = SyncQueueService.process_push(
            user=request.user,
            operations=operations,
            client_batch_id=client_batch_id,
        )
        if summary.get("rejected", 0) > 0:
            from apps.core.utils import error_response
            return error_response(
                f"{summary['rejected']} operación(es) rechazada(s). "
                "El lote fue revertido. Corrija los errores y re-envíe.",
                status=422,
            )
        return ok_response(summary)

    def pull(self, request):
        since = request.query_params.get("since")
        source_table = request.query_params.get("source_table")
        logger.info(
            "[VIEW] GET pull de user=%s: since=%r source_table=%r",
            getattr(request.user, "id", None),
            since,
            source_table,
        )
        results = SyncQueueService.pull_changes(
            since=since,
            source_table=source_table,
        )
        return ok_response({"count": len(results), "results": results})

    def rollback(self, request):
        batch_id = request.data.get("batch_id")
        if not batch_id:
            return ok_response({"ok": False, "msg": "batch_id es requerido"})

        batch = SyncBatchRepository.get_by_client_batch_id(batch_id)
        if not batch:
            batch = SyncBatchRepository.get_by_uuid(batch_id)

        if not batch:
            return ok_response({"ok": False, "msg": "Lote no encontrado"})

        if batch.status == BatchStatusChoices.ROLLED_BACK:
            return ok_response({"ok": True, "msg": "Lote ya fue revertido", "batch_id": str(batch.uuid)})

        result = SyncQueueService.rollback_batch(str(batch.uuid))
        logger.info(
            "[VIEW] Rollback ejecutado para batch=%s por user=%s",
            batch_id,
            getattr(request.user, "id", None),
        )
        return ok_response(result)
