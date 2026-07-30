import hashlib
import logging
import uuid as uuid_lib

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from ..infrastructure.repositories import SyncBatchRepository, SyncQueueRepository
from ..infrastructure.models import BatchStatusChoices, SyncStatusChoices

logger = logging.getLogger("apps.integration.sync")


class ConflictResolutionStrategy:
    STRATEGIES = {
        "student_note": "LAST_WRITE_WINS",
        "attendance": "LAST_WRITE_WINS",
        "conduct_incident": "LAST_WRITE_WINS",
        "project_note": "LAST_WRITE_WINS",
        "early_alert": "SERVER_WINS",
        "evaluative_activity": "SERVER_WINS",
        "enrollment": "MANUAL",
        "behavior_evaluation": "LAST_WRITE_WINS",
    }

    @classmethod
    def resolve(cls, source_table, local_record, remote_payload):
        strategy = cls.STRATEGIES.get(source_table, "LAST_WRITE_WINS")

        if strategy == "LAST_WRITE_WINS":
            return cls._last_write_wins(local_record, remote_payload)
        elif strategy == "SERVER_WINS":
            return cls._server_wins(local_record, remote_payload)
        elif strategy == "MANUAL":
            return cls._manual_resolution_required(local_record, remote_payload)
        return "KEEP_LOCAL"

    @classmethod
    def _last_write_wins(cls, local, remote):
        remote_version = remote.get("sync_version", 0)
        if remote_version <= local.sync_version:
            return "KEEP_LOCAL"
        return "ACCEPT_REMOTE"

    @classmethod
    def _server_wins(cls, local, remote):
        return "KEEP_LOCAL"

    @classmethod
    def _manual_resolution_required(cls, local, remote):
        local.mark_conflict()
        local.save()
        return "MANUAL"


class SyncQueueService:

    @staticmethod
    def queue_operation(user, source_table, record_uuid, operation, payload=None, client_version=None, batch=None):
        payload = payload or {}
        idempotency_key = SyncQueueService._build_idempotency_key(
            source_table, record_uuid, operation, payload
        )
        payload_keys = sorted(payload.keys())

        logger.info(
            "[QUEUE] Encolando operacion source_table=%r record_uuid=%r operation=%r "
            "payload_keys=%s idempotency_key=%s user=%s",
            source_table,
            record_uuid,
            operation,
            payload_keys,
            idempotency_key,
            getattr(user, "id", None),
        )

        existing = SyncQueueRepository.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            if existing.status == SyncStatusChoices.SYNCED:
                existing_version = (existing.payload or {}).get("sync_version")
                incoming_version = payload.get("sync_version")
                if (
                    incoming_version is not None
                    and existing_version is not None
                    and int(incoming_version) > int(existing_version)
                ):
                    logger.info(
                        "[QUEUE] Item id=%s ya SYNCED pero llega sync_version=%s > %s; "
                        "se crea un ítem nuevo.",
                        existing.id,
                        incoming_version,
                        existing_version,
                    )
                else:
                    logger.info(
                        "[QUEUE] DEDUP omitido: item id=%s ya SYNCED con idempotency_key=%s "
                        "(source_table=%r record_uuid=%r sync_version=%s). NO se vuelve a procesar.",
                        existing.id,
                        idempotency_key,
                        source_table,
                        record_uuid,
                        existing_version,
                    )
                    return {
                        "dedup": True,
                        "server_version": existing_version or incoming_version or 1,
                    }

            logger.info(
                "[QUEUE] Item existente id=%s en estado=%s (attempts=%s) con idempotency_key=%s. "
                "Se actualiza payload, se resetea attempts y se re-encola a PENDING "
                "(LAST_WRITE_WINS) en lugar de insertar duplicado.",
                existing.id,
                existing.status,
                existing.attempts,
                idempotency_key,
            )
            return SyncQueueRepository.update(
                existing.id,
                payload=payload or {},
                status=SyncStatusChoices.PENDING,
                attempts=0,
                last_attempt_at=None,
                last_error="",
            )

        instance = SyncQueueRepository.create(
            user=user,
            source_table=source_table,
            record_uuid=record_uuid,
            operation=operation,
            payload=payload or {},
            status=SyncStatusChoices.PENDING,
            idempotency_key=idempotency_key,
            attempts=0,
            batch=batch,
        )
        logger.info(
            "[QUEUE] Item creado id=%s status=PENDING source_table=%r record_uuid=%r operation=%r batch=%s",
            instance.id,
            source_table,
            record_uuid,
            operation,
            batch.id if batch else None,
        )
        return instance

    @staticmethod
    def _build_idempotency_key(source_table, record_uuid, operation_code, payload=None):
        """Clave única por cambio, no solo por registro+operación.

        Incluye ``sync_version`` del payload cuando viene del cliente, de modo que
        una segunda edición offline del mismo registro genera un ítem nuevo en
        cola en lugar de deduplicarse contra la sincronización anterior.
        """
        sync_version = (payload or {}).get("sync_version")
        if sync_version is not None:
            raw = f"{source_table}:{record_uuid}:{operation_code}:{sync_version}"
        else:
            raw = f"{source_table}:{record_uuid}:{operation_code}"
        return hashlib.sha256(raw.encode()).hexdigest()[:64]

    @staticmethod
    @transaction.atomic
    def process_push(user, operations, client_batch_id=None):
        from ..tasks.sync_tasks import process_sync_queue_item, SYNC_HANDLERS

        logger.info(
            "[PUSH] Recibido lote de %d operacion(es) de user=%s. "
            "source_tables=%s. Handlers registrados=%s. client_batch_id=%s",
            len(operations),
            getattr(user, "id", None),
            [op.get("source_table") for op in operations],
            sorted(SYNC_HANDLERS.keys()),
            client_batch_id,
        )

        # Idempotencia de batch: si ya se commitió, retornar respuesta cacheada
        if client_batch_id:
            existing_batch = SyncBatchRepository.get_by_client_batch_id(client_batch_id)
            if existing_batch and existing_batch.committed:
                logger.info(
                    "[PUSH] Batch %s ya fue commiteado anteriormente. "
                    "Retornando respuesta cacheada.",
                    client_batch_id,
                )
                cached = existing_batch.cached_response
                if cached and isinstance(cached, dict) and "results" in cached:
                    return cached
                return {
                    "accepted": 0,
                    "rejected": 0,
                    "conflicts": 0,
                    "results": [],
                    "batch_id": str(existing_batch.uuid),
                    "cached": True,
                }

        # Crear lote
        batch_id_str = client_batch_id or str(uuid_lib.uuid4())
        batch = SyncBatchRepository.create(
            client_batch_id=batch_id_str,
            user=user,
            total_operations=len(operations),
            status=BatchStatusChoices.RECEIVED,
        )

        results = []
        accepted = 0
        rejected = 0
        conflicts = 0
        queued_ids = []

        for index, op in enumerate(operations):
            record_uuid = op.get("record_uuid")
            source_table = op.get("source_table")

            if source_table not in SYNC_HANDLERS:
                logger.warning(
                    "[PUSH] op[%d] source_table=%r NO tiene handler registrado. "
                    "Se encolara pero el worker NO podra escribir en la tabla destino. "
                    "Handlers disponibles=%s",
                    index,
                    source_table,
                    sorted(SYNC_HANDLERS.keys()),
                )

            try:
                result = SyncQueueService.queue_operation(
                    user=user,
                    source_table=source_table,
                    record_uuid=record_uuid,
                    operation=op.get("operation"),
                    payload=op.get("payload", {}),
                    client_version=op.get("client_version"),
                    batch=batch,
                )

                if isinstance(result, dict) and result.get("dedup"):
                    accepted += 1
                    results.append({
                        "record_uuid": record_uuid,
                        "status": "DEDUP",
                        "server_version": result.get("server_version", 1),
                        "deduplicated": True,
                    })
                elif hasattr(result, "id"):
                    accepted += 1
                    queued_ids.append(result.id)
                    results.append({
                        "record_uuid": record_uuid,
                        "status": "QUEUED",
                        "queue_id": result.id,
                    })
                else:
                    rejected += 1
                    results.append({
                        "record_uuid": record_uuid,
                        "status": "REJECTED",
                        "message": str(result),
                    })
            except IncompatibleSchemaError as exc:
                rejected += 1
                logger.warning("[PUSH] op[%d] esquema incompatible: %s", index, exc)
                results.append({
                    "record_uuid": record_uuid,
                    "status": "INCOMPATIBLE",
                    "message": str(exc),
                })
            except Exception as exc:
                rejected += 1
                logger.exception("[PUSH] op[%d] error encolando record_uuid=%r", index, record_uuid)
                results.append({
                    "record_uuid": record_uuid,
                    "status": "ERROR",
                    "message": str(exc),
                })

        response_data = {
            "batch_id": str(batch.uuid),
            "accepted": accepted,
            "rejected": rejected,
            "conflicts": conflicts,
            "results": results,
        }

        # Si hay al menos un error, revertir todo el batch
        if rejected > 0:
            logger.warning(
                "[PUSH] Batch %s tiene %d operaciones rechazadas. "
                "Haciendo ROLLBACK de todo el lote.",
                batch_id_str,
                rejected,
            )
            SyncBatchRepository.update(
                batch.id,
                status=BatchStatusChoices.FAILED,
                committed=False,
                failed_operations=rejected,
                completed_operations=accepted,
                cached_response=response_data,
            )
            # La transacción hará ROLLBACK automático al salir
            transaction.set_rollback(True)
            return response_data

        # Todo ok — marcar batch como commiteado
        SyncBatchRepository.update(
            batch.id,
            status=BatchStatusChoices.QUEUED,
            committed=True,
            completed_operations=accepted,
            cached_response=response_data,
        )

        # Disparar Celery tasks SOLO después del commit
        transaction.on_commit(
            lambda ids=queued_ids: [
                process_sync_queue_item.delay(qid) for qid in ids
            ]
        )

        logger.info(
            "[PUSH] Batch %s: %d aceptadas, %d rechazadas, %d conflictos. "
            "%d tareas Celery encoladas via on_commit.",
            batch_id_str,
            accepted,
            rejected,
            conflicts,
            len(queued_ids),
        )
        return response_data

    @staticmethod
    def pull_changes(since=None, source_table=None, limit=100):
        parsed_since = parse_datetime(since) if since else None
        if since and parsed_since is None:
            logger.warning(
                "[PULL] No se pudo parsear since=%r (formato invalido). "
                "Se ignorara el filtro de fecha.",
                since,
            )
        items = SyncQueueRepository.get_for_pull(
            since=parsed_since,
            source_table=source_table,
            limit=limit,
        )
        items = list(items)
        logger.info(
            "[PULL] since=%r (parsed=%s) source_table=%r -> %d item(s). "
            "NOTA: pull filtra por processed_at>=since; items PENDING (processed_at=NULL) "
            "NO se devuelven hasta que el worker los procese.",
            since,
            parsed_since.isoformat() if parsed_since else None,
            source_table,
            len(items),
        )
        return [
            {
                "uuid": str(item.uuid),
                "source_table": item.source_table,
                "operation": item.operation or "",
                "record_uuid": item.record_uuid,
                "payload": item.payload,
                "status": item.status or "",
                "processed_at": item.processed_at.isoformat() if item.processed_at else None,
            }
            for item in items
        ]

    @staticmethod
    @transaction.atomic
    def mark_processing(sync_id):
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if sync_item:
            SyncQueueRepository.update(
                sync_item.id,
                status=SyncStatusChoices.PROCESSING,
                attempts=sync_item.attempts + 1,
                last_attempt_at=timezone.now(),
            )
        return sync_item

    @staticmethod
    @transaction.atomic
    def mark_completed(sync_id):
        return SyncQueueRepository.update(
            sync_id,
            status=SyncStatusChoices.SYNCED,
            processed_at=timezone.now(),
            last_error="",
        )

    @staticmethod
    @transaction.atomic
    def rollback_batch(batch_uuid):
        from ..tasks.sync_tasks import SYNC_HANDLERS

        logger.info("[ROLLBACK] Revirtiendo batch uuid=%s", batch_uuid)
        batch = SyncBatchRepository.get_by_uuid(batch_uuid)
        if not batch:
            logger.error("[ROLLBACK] Batch %s no encontrado", batch_uuid)
            return
        if batch.status == BatchStatusChoices.ROLLED_BACK:
            logger.info("[ROLLBACK] Batch %s ya fue revertido", batch_uuid)
            return

        items = SyncQueueRepository.get_by_batch(batch.id)
        rolled_back_count = 0

        for item in items:
            if item.status == SyncStatusChoices.ROLLED_BACK:
                continue

            handler = SYNC_HANDLERS.get(item.source_table)
            if not handler:
                logger.warning("[ROLLBACK] No hay handler para source_table=%s", item.source_table)
                SyncQueueRepository.update(item.id, status=SyncStatusChoices.ROLLED_BACK)
                rolled_back_count += 1
                continue

            try:
                if item.status == SyncStatusChoices.SYNCED:
                    op = item.operation or ""
                    if op in ("INSERT", "CREATE"):
                        handler.handle_rollback_create(item.record_uuid, item.previous_state or {})
                    elif op == "UPDATE":
                        handler.handle_rollback_update(item.record_uuid, item.previous_state or {})
                    elif op == "DELETE":
                        handler.handle_rollback_delete(item.record_uuid, item.previous_state or {})

                SyncQueueRepository.update(item.id, status=SyncStatusChoices.ROLLED_BACK)
                rolled_back_count += 1
            except Exception:
                logger.exception("[ROLLBACK] Error revirtiendo item %s del batch %s", item.id, batch_uuid)

        SyncBatchRepository.update(
            batch.id,
            status=BatchStatusChoices.ROLLED_BACK,
        )
        logger.info(
            "[ROLLBACK] Batch %s revertido: %d items procesados",
            batch_uuid,
            rolled_back_count,
        )
        return {
            "batch_uuid": batch_uuid,
            "rolled_back": rolled_back_count,
            "total": items.count(),
        }



