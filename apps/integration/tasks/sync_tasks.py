import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from ..infrastructure.repositories import SyncQueueRepository
from ..domain.services import ConflictResolutionStrategy
from ..infrastructure.models import SyncStatusChoices

logger = logging.getLogger("apps.integration.sync")

SYNC_HANDLERS = {}


def register_sync_handler(source_table):
    def decorator(cls):
        SYNC_HANDLERS[source_table] = cls
        return cls
    return decorator


# Modulos que definen handlers via @register_sync_handler. El worker de Celery
# autodescubre solo "<app>/tasks.py"; el proceso web NO hace autodiscover y
# "apps.analytics.tasks_handlers" no se autodescubre por su nombre. Por eso los
# cargamos explicitamente desde IntegrationConfig.ready() para tener el registro
# completo en TODOS los procesos (web, worker, beat).
HANDLER_MODULES = (
    "apps.attendance.attendance_core.tasks",
    "apps.behavior.conduct_incident.tasks",
    "apps.behavior.behavior_evaluation.tasks",
    "apps.grading.student_note.tasks",
    "apps.grading.evaluation.tasks",
    "apps.analytics.tasks_handlers",
    "apps.students.tasks",
)


def load_sync_handlers():
    import importlib

    for module_path in HANDLER_MODULES:
        try:
            importlib.import_module(module_path)
        except Exception:
            logger.exception(
                "[REGISTRO] No se pudo importar el modulo de handlers %r", module_path
            )
    return SYNC_HANDLERS


class BaseSyncHandler:
    source_table = None
    model = None
    lookup_field = "uuid"

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        logger.info(
            "[INSERT] tabla_destino=%s record_uuid=%s payload_keys=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
            sorted((payload or {}).keys()),
        )
        instance = cls.model(**payload)
        instance.uuid = record_uuid
        instance.sync_status = "SYNCED"
        instance.synced_at = timezone.now()
        instance.sync_version = 1
        instance.full_clean()
        instance.save()
        logger.info(
            "[INSERT] OK guardado en %s pk=%s uuid=%s",
            getattr(cls.model, "__name__", None),
            instance.pk,
            record_uuid,
        )
        return instance

    @classmethod
    def handle_update(cls, record_uuid, payload):
        logger.info(
            "[UPDATE] tabla_destino=%s lookup=%s=%s payload_keys=%s",
            getattr(cls.model, "__name__", None),
            cls.lookup_field,
            record_uuid,
            sorted((payload or {}).keys()),
        )
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
        logger.info(
            "[UPDATE] OK actualizado en %s pk=%s uuid=%s nueva_version=%s",
            getattr(cls.model, "__name__", None),
            instance.pk,
            str(instance.uuid),
            instance.sync_version,
        )
        return {"status": "SYNCED", "uuid": str(instance.uuid)}

    @classmethod
    def handle_delete(cls, record_uuid, payload=None):
        logger.info(
            "[DELETE] tabla_destino=%s lookup=%s=%s",
            getattr(cls.model, "__name__", None),
            cls.lookup_field,
            record_uuid,
        )
        instance = cls.model.objects.get(**{cls.lookup_field: record_uuid})
        instance.delete()
        logger.info(
            "[DELETE] OK eliminado de %s uuid=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
        )
        return {"status": "DELETED", "uuid": str(record_uuid)}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_sync_queue_item(self, sync_id):
    logger.info("[TASK] Iniciando process_sync_queue_item sync_id=%s", sync_id)
    try:
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if not sync_item:
            logger.warning(
                "[TASK] SyncQueue item %s no encontrado; reintento en 2s",
                sync_id,
            )
            raise self.retry(countdown=2, max_retries=5)

        logger.info(
            "[TASK] item id=%s source_table=%r operation=%r record_uuid=%r status=%s attempts=%s",
            sync_item.id,
            sync_item.source_table,
            sync_item.operation,
            sync_item.record_uuid,
            sync_item.status,
            sync_item.attempts,
        )

        if sync_item.status != SyncStatusChoices.PENDING:
            logger.info("[TASK] SyncQueue item %s ya procesado (status=%s), se omite", sync_id, sync_item.status)
            return {"ok": True, "status": str(sync_item.status)}

        SyncQueueRepository.update(sync_item.id, status=SyncStatusChoices.PROCESSING, attempts=sync_item.attempts + 1, last_attempt_at=timezone.now())

        handler = SYNC_HANDLERS.get(sync_item.source_table)
        if not handler:
            logger.error(
                "[TASK] NO hay handler para source_table=%r. "
                "Por esto la tabla destino NO se actualiza. "
                "Handlers registrados=%s. "
                "Revisa que el modulo que define @register_sync_handler(%r) sea importado "
                "por el worker (Celery autodiscover solo importa <app>/tasks.py).",
                sync_item.source_table,
                sorted(SYNC_HANDLERS.keys()),
                sync_item.source_table,
            )
            raise ValueError(f"No hay handler para source_table='{sync_item.source_table}'")

        operation = sync_item.operation or ""
        record_uuid = sync_item.record_uuid
        payload = sync_item.payload or {}

        logger.info(
            "[TASK] Handler resuelto %s -> modelo=%s. Aplicando operation=%r",
            handler.__name__,
            getattr(getattr(handler, "model", None), "__name__", None),
            operation,
        )

        with transaction.atomic():
            if operation in ("INSERT", "CREATE"):
                result = handler.handle_insert(record_uuid, payload)
            elif operation == "UPDATE":
                result = handler.handle_update(record_uuid, payload)
            elif operation == "DELETE":
                result = handler.handle_delete(record_uuid, payload)
            else:
                logger.error(
                    "[TASK] Operacion desconocida=%r para item id=%s. "
                    "Se esperaba INSERT/CREATE/UPDATE/DELETE.",
                    operation,
                    sync_item.id,
                )
                raise ValueError(f"Operación desconocida: {operation}")

            SyncQueueRepository.update(
                sync_item.id,
                status=SyncStatusChoices.SYNCED,
                processed_at=timezone.now(),
                last_error="",
            )

        logger.info("[TASK] SyncQueue item %s procesado exitosamente -> SYNCED", sync_id)
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
