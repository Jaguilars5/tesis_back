from django.db import transaction
from django.utils import timezone
from apps.core.repositories.sync_queue_repository import SyncQueueRepository


class SyncQueueService:
    """
    Servicio para gestionar la cola de sincronización offline.
    """

    @staticmethod
    @transaction.atomic
    def queue_operation(user, source_table, record_uuid, operation, payload=None):
        """Encola una nueva operación de sincronización."""
        return SyncQueueRepository.create(
            user=user,
            source_table=source_table,
            record_uuid=record_uuid,
            operation=operation,
            payload=payload or {},
            status="pending",
            attempts=0,
        )

    @staticmethod
    @transaction.atomic
    def mark_processing(sync_id):
        """Marca un elemento como en proceso."""
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if sync_item:
            SyncQueueRepository.update(
                sync_item.id,
                status="processing",
                attempts=sync_item.attempts + 1,
            )
        return sync_item

    @staticmethod
    @transaction.atomic
    def mark_completed(sync_id):
        """Marca un elemento como completado con éxito."""
        return SyncQueueRepository.update(
            sync_id,
            status="completed",
            processed_at=timezone.now(),
            last_error=None,
        )

    @staticmethod
    @transaction.atomic
    def mark_failed(sync_id, error_message):
        """Marca un elemento como fallido y registra el error."""
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if not sync_item:
            return None
        status = "failed" if sync_item.attempts >= 3 else "pending"
        return SyncQueueRepository.update(
            sync_item.id,
            status=status,
            last_error=error_message,
        )
