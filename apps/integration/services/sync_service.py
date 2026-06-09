from django.db import transaction
from django.utils import timezone
from ..repositories import SyncQueueRepository
from ..repositories.sync_status_repository import SyncStatusRepository


class SyncQueueService:
    @staticmethod
    @transaction.atomic
    def queue_operation(user, source_table, record_uuid, operation, payload=None):
        status_pendiente = SyncStatusRepository.get_by_code("PENDIENTE")
        return SyncQueueRepository.create(
            user=user,
            source_table=source_table,
            record_uuid=record_uuid,
            operation=operation,
            payload=payload or {},
            status=status_pendiente,
            attempts=0,
        )

    @staticmethod
    @transaction.atomic
    def mark_processing(sync_id):
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if sync_item:
            status_procesando = SyncStatusRepository.get_by_code("PROCESADO")
            SyncQueueRepository.update(
                sync_item.id,
                status=status_procesando,
                attempts=sync_item.attempts + 1,
            )
        return sync_item

    @staticmethod
    @transaction.atomic
    def mark_completed(sync_id):
        status_procesado = SyncStatusRepository.get_by_code("PROCESADO")
        return SyncQueueRepository.update(
            sync_id,
            status=status_procesado,
            processed_at=timezone.now(),
            last_error=None,
        )

    @staticmethod
    @transaction.atomic
    def mark_failed(sync_id, error_message):
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if not sync_item:
            return None
        status = SyncStatusRepository.get_by_code("PENDIENTE" if sync_item.attempts < 3 else "ERROR")
        return SyncQueueRepository.update(
            sync_item.id,
            status=status,
            last_error=error_message,
        )
