import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.core.repositories.sync_queue_repository import SyncQueueRepository

logger = logging.getLogger(__name__)


SYNC_HANDLERS = {}


def register_sync_handler(source_table):
    def decorator(cls):
        SYNC_HANDLERS[source_table] = cls
        return cls
    return decorator


class BaseSyncHandler:
    model = None
    lookup_field = "uuid"

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        instance = cls.model(**payload)
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    def handle_update(cls, record_uuid, payload):
        instance = cls.model.objects.get(**{cls.lookup_field: record_uuid})
        for key, value in payload.items():
            setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    def handle_delete(cls, record_uuid, payload=None):
        instance = cls.model.objects.get(**{cls.lookup_field: record_uuid})
        instance.delete()
        return instance


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_sync_queue_item(self, sync_id):
    try:
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if not sync_item:
            logger.warning("SyncQueue item %s no encontrado", sync_id)
            return {"ok": False, "error": "not_found"}

        if sync_item.status not in ("PENDIENTE", "ERROR"):
            logger.info("SyncQueue item %s ya procesado (status=%s)", sync_id, sync_item.status)
            return {"ok": True, "status": sync_item.status}

        SyncQueueRepository.update(sync_item.id, status="PROCESANDO", attempts=sync_item.attempts + 1)

        handler = SYNC_HANDLERS.get(sync_item.source_table)
        if not handler:
            raise ValueError(f"No hay handler para source_table='{sync_item.source_table}'")

        operation = sync_item.operation
        record_uuid = sync_item.record_uuid
        payload = sync_item.payload or {}

        with transaction.atomic():
            if operation == "INSERT":
                handler.handle_insert(record_uuid, payload)
            elif operation == "UPDATE":
                handler.handle_update(record_uuid, payload)
            elif operation == "DELETE":
                handler.handle_delete(record_uuid, payload)
            else:
                raise ValueError(f"Operación desconocida: {operation}")

            SyncQueueRepository.update(
                sync_item.id,
                status="PROCESADO",
                processed_at=timezone.now(),
                last_error=None,
            )

        logger.info("SyncQueue item %s procesado exitosamente", sync_id)
        return {"ok": True, "status": "PROCESADO"}

    except Exception as exc:
        logger.exception("Error procesando SyncQueue item %s", sync_id)
        try:
            sync_item = SyncQueueRepository.get_by_id(sync_id)
            if sync_item:
                attempts = sync_item.attempts + 1
                new_status = "ERROR" if attempts >= 3 else "PENDIENTE"
                SyncQueueRepository.update(
                    sync_item.id,
                    status=new_status,
                    last_error=str(exc),
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
