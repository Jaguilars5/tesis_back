import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from ..repositories import SyncQueueRepository
from ..services.conflict_resolver import ConflictResolutionStrategy
from ..models.syncable_mixin import SyncStatusChoices

logger = logging.getLogger(__name__)

SYNC_HANDLERS = {}


def register_sync_handler(source_table):
    def decorator(cls):
        SYNC_HANDLERS[source_table] = cls
        return cls
    return decorator


class BaseSyncHandler:
    source_table = None
    model = None
    lookup_field = "uuid"

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        instance = cls.model(**payload)
        instance.uuid = record_uuid
        instance.sync_status = "SYNCED"
        instance.synced_at = timezone.now()
        instance.sync_version = 1
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    def handle_update(cls, record_uuid, payload):
        instance = cls.model.objects.get(**{cls.lookup_field: record_uuid})
        incoming_version = payload.get("sync_version", 1)

        if incoming_version < instance.sync_version:
            resolution = ConflictResolutionStrategy.resolve(
                cls.source_table, instance, payload
            )
            if resolution == "MANUAL":
                instance.mark_conflict()
                instance.save()
                return {"status": "CONFLICT", "local_version": instance.sync_version, "uuid": str(instance.uuid)}
            elif resolution == "KEEP_LOCAL":
                return {"status": "REJECTED", "reason": "Server version is newer", "uuid": str(instance.uuid)}

        for field, value in payload.items():
            if hasattr(instance, field) and field not in ["uuid", "sync_version", "id"]:
                setattr(instance, field, value)
        instance.sync_version = max(instance.sync_version, incoming_version) + 1
        instance.mark_synced()
        instance.full_clean()
        instance.save()
        return {"status": "SYNCED", "uuid": str(instance.uuid)}

    @classmethod
    def handle_delete(cls, record_uuid, payload=None):
        instance = cls.model.objects.get(**{cls.lookup_field: record_uuid})
        instance.delete()
        return {"status": "DELETED", "uuid": str(record_uuid)}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_sync_queue_item(self, sync_id):
    try:
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if not sync_item:
            logger.warning("SyncQueue item %s no encontrado", sync_id)
            return {"ok": False, "error": "not_found"}

        if sync_item.status != SyncStatusChoices.PENDING:
            logger.info("SyncQueue item %s ya procesado (status=%s)", sync_id, sync_item.status)
            return {"ok": True, "status": str(sync_item.status)}

        SyncQueueRepository.update(sync_item.id, status=SyncStatusChoices.PROCESSING, attempts=sync_item.attempts + 1, last_attempt_at=timezone.now())

        handler = SYNC_HANDLERS.get(sync_item.source_table)
        if not handler:
            raise ValueError(f"No hay handler para source_table='{sync_item.source_table}'")

        operation = sync_item.operation or ""
        record_uuid = sync_item.record_uuid
        payload = sync_item.payload or {}

        with transaction.atomic():
            if operation in ("INSERT", "CREATE"):
                result = handler.handle_insert(record_uuid, payload)
            elif operation == "UPDATE":
                result = handler.handle_update(record_uuid, payload)
            elif operation == "DELETE":
                result = handler.handle_delete(record_uuid, payload)
            else:
                raise ValueError(f"Operación desconocida: {operation}")

            SyncQueueRepository.update(
                sync_item.id,
                status=SyncStatusChoices.SYNCED,
                processed_at=timezone.now(),
                last_error=None,
            )

        logger.info("SyncQueue item %s procesado exitosamente", sync_id)
        return {"ok": True, "status": "PROCESADO", "result": result}

    except Exception as exc:
        logger.exception("Error procesando SyncQueue item %s", sync_id)
        try:
            sync_item = SyncQueueRepository.get_by_id(sync_id)
            if sync_item:
                attempts = sync_item.attempts + 1
                new_status = SyncStatusChoices.ERROR if attempts >= 3 else SyncStatusChoices.PENDING
                SyncQueueRepository.update(
                    sync_item.id,
                    status=new_status,
                    last_error=str(exc),
                    last_attempt_at=timezone.now(),
                )
        except Exception:
            logger.exception("Error al actualizar estado de SyncQueue item %s", sync_id)
        raise self.retry(exc=exc)


@shared_task
def process_pending_sync_batch():
    pending = SyncQueueRepository.get_pending()
    count = 0
    for item in pending:
        process_sync_queue_item.delay(item.id)
        count += 1
    logger.info("Disparados %d SyncQueue items para procesamiento", count)
    return {"ok": True, "dispatched": count}
