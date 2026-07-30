import logging

import uuid

from celery import shared_task
from django.db import models, transaction
from django.utils import timezone

from ..infrastructure.repositories import SyncBatchRepository, SyncQueueRepository
from ..domain.services import ConflictResolutionStrategy
from ..infrastructure.models import BatchStatusChoices, SyncStatusChoices

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
    business_key_fields = []
    update_allowed = None  # Set of field names; None = allow all (except internal)

    @classmethod
    def _find_by_business_key(cls, payload):
        if not cls.business_key_fields:
            return None
        filters = {}
        for field in cls.business_key_fields:
            value = payload.get(field)
            if value is None:
                return None
            filters[field] = value
        return cls.model.objects.filter(**filters).first()

    @classmethod
    def handle_insert(cls, record_uuid, payload):
        logger.info(
            "[INSERT] tabla_destino=%s record_uuid=%s payload_keys=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
            sorted((payload or {}).keys()),
        )

        # Buscar por clave de negocio para evitar duplicados
        existing = cls._find_by_business_key(payload)
        if existing is not None:
            logger.info(
                "[INSERT] Registro existente encontrado por clave de negocio en %s uuid=%s. "
                "Se actualiza en lugar de insertar.",
                getattr(cls.model, "__name__", None),
                str(existing.uuid),
            )
            return cls.handle_update(str(existing.uuid), {**payload, "uuid": str(existing.uuid)})

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
    def _get_instance(cls, record_uuid):
        qs = cls.model.objects.select_for_update().filter(**{cls.lookup_field: record_uuid})
        return qs.get()

    @classmethod
    def handle_update(cls, record_uuid, payload):
        logger.info(
            "[UPDATE] tabla_destino=%s lookup=%s=%s payload_keys=%s",
            getattr(cls.model, "__name__", None),
            cls.lookup_field,
            record_uuid,
            sorted((payload or {}).keys()),
        )
        instance = cls._get_instance(record_uuid)
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

        allowed = cls.update_allowed
        for field, value in payload.items():
            if field in ("uuid", "sync_version", "id"):
                continue
            if allowed is not None and field not in allowed:
                continue
            if hasattr(instance, field):
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
        instance = cls._get_instance(record_uuid)
        instance.delete()
        logger.info(
            "[DELETE] OK eliminado de %s uuid=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
        )
        return {"status": "DELETED", "uuid": str(record_uuid)}

    # --- Rollback methods ---

    @classmethod
    def handle_rollback_create(cls, record_uuid, previous_state):
        logger.info(
            "[ROLLBACK_CREATE] Eliminando registro creado en %s uuid=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
        )
        cls.model.objects.filter(**{cls.lookup_field: record_uuid}).delete()
        return {"status": "ROLLED_BACK", "uuid": str(record_uuid)}

    @classmethod
    def handle_rollback_update(cls, record_uuid, previous_state):
        logger.info(
            "[ROLLBACK_UPDATE] Restaurando estado anterior en %s uuid=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
        )
        if previous_state:
            cls.model.objects.filter(**{cls.lookup_field: record_uuid}).update(**previous_state)
        return {"status": "ROLLED_BACK", "uuid": str(record_uuid)}

    @classmethod
    def handle_rollback_delete(cls, record_uuid, previous_state):
        logger.info(
            "[ROLLBACK_DELETE] Reinsertando registro eliminado en %s uuid=%s",
            getattr(cls.model, "__name__", None),
            record_uuid,
        )
        if previous_state:
            data = dict(previous_state)
            if cls.lookup_field not in data:
                data[cls.lookup_field] = record_uuid
            cls.model.objects.create(**data)
        return {"status": "ROLLED_BACK", "uuid": str(record_uuid)}


def _check_batch_rollback(batch_id):
    try:
        from ..infrastructure.models import SyncBatch
        batch = SyncBatch.objects.filter(id=batch_id).first()
        if not batch:
            return
        if batch.status in (BatchStatusChoices.ROLLED_BACK, BatchStatusChoices.COMPLETED):
            return
        synced_count = SyncQueue.objects.filter(
            batch_id=batch.id, status=SyncStatusChoices.SYNCED
        ).count()
        total_failed = (batch.failed_operations or 0)
        if (total_failed + synced_count) >= batch.total_operations and total_failed > 0:
            rollback_batch.delay(str(batch.uuid))
    except Exception:
        logger.exception("Error checking batch rollback for batch_id=%s", batch_id)


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

        if sync_item.status == SyncStatusChoices.ROLLED_BACK:
            logger.info("[TASK] SyncQueue item %s fue revertido (ROLLED_BACK), se omite", sync_id)
            return {"ok": True, "status": "ROLLED_BACK"}

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
            # Capturar previous_state antes de modificar
            previous_state = {}
            if operation in ("UPDATE",):
                try:
                    existing = handler.model.objects.get(**{handler.lookup_field: record_uuid})
                    previous_state = {f.name: getattr(existing, f.name) for f in handler.model._meta.fields if f.name not in ("id",)}
                    for k, v in previous_state.items():
                        if isinstance(v, (uuid.UUID,)):
                            previous_state[k] = str(v)
                except handler.model.DoesNotExist:
                    logger.warning("[TASK] No se encontró registro existente para UPDATE uuid=%s", record_uuid)
            elif operation == "DELETE":
                try:
                    existing = handler.model.objects.get(**{handler.lookup_field: record_uuid})
                    previous_state = {f.name: getattr(existing, f.name) for f in handler.model._meta.fields if f.name not in ("id",)}
                    for k, v in previous_state.items():
                        if isinstance(v, (uuid.UUID,)):
                            previous_state[k] = str(v)
                except handler.model.DoesNotExist:
                    logger.warning("[TASK] No se encontró registro existente para DELETE uuid=%s", record_uuid)

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
                previous_state=previous_state,
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

                if sync_item.batch_id and new_status == SyncStatusChoices.ERROR:
                    SyncBatchRepository.update(
                        sync_item.batch_id,
                        failed_operations=models.F("failed_operations") + 1,
                    )
                    _check_batch_rollback(sync_item.batch_id)
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


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def rollback_batch(self, batch_uuid):
    from ..domain.services import SyncQueueService
    logger.info("[ROLLBACK] Iniciando rollback del batch %s", batch_uuid)
    try:
        SyncQueueService.rollback_batch(batch_uuid)
        logger.info("[ROLLBACK] Batch %s revertido exitosamente", batch_uuid)
        return {"ok": True, "batch_uuid": batch_uuid, "status": "ROLLED_BACK"}
    except Exception as exc:
        logger.exception("[ROLLBACK] Error revirtiendo batch %s", batch_uuid)
        raise self.retry(exc=exc)
