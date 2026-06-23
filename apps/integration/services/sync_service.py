import hashlib

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from ..repositories import SyncQueueRepository
from ..models.syncable_mixin import SyncStatusChoices


class IncompatibleSchemaError(ValueError):
    pass


class SyncQueueService:
    @staticmethod
    @transaction.atomic
    def queue_operation(user, source_table, record_uuid, operation, payload=None, client_version=None):
        idempotency_key = SyncQueueService._build_idempotency_key(source_table, record_uuid, operation)

        if SyncQueueRepository.is_synced(idempotency_key):
            return None

        return SyncQueueRepository.create(
            user=user,
            source_table=source_table,
            record_uuid=record_uuid,
            operation=operation,
            payload=payload or {},
            status=SyncStatusChoices.PENDING,
            idempotency_key=idempotency_key,
            attempts=0,
        )

    @staticmethod
    def _build_idempotency_key(source_table, record_uuid, operation_code):
        raw = f"{source_table}:{record_uuid}:{operation_code}"
        return hashlib.sha256(raw.encode()).hexdigest()[:64]

    @staticmethod
    def process_push(user, operations):
        """Encola un lote de operaciones de sincronización del cliente.

        Devuelve un resumen con conteos y el resultado por operación. Las
        operaciones aceptadas que generan un nuevo item de cola se procesan
        de forma asíncrona vía Celery.
        """
        from ..tasks.sync_tasks import process_sync_queue_item

        results = []
        accepted = 0
        rejected = 0
        conflicts = 0

        for op in operations:
            record_uuid = op.get("record_uuid")
            try:
                result = SyncQueueService.queue_operation(
                    user=user,
                    source_table=op.get("source_table"),
                    record_uuid=record_uuid,
                    operation=op.get("operation"),
                    payload=op.get("payload", {}),
                    client_version=op.get("client_version"),
                )

                if result is None:
                    accepted += 1
                    results.append({
                        "record_uuid": record_uuid,
                        "status": "SYNCED",
                        "server_version": 1,
                    })
                elif hasattr(result, "id"):
                    accepted += 1
                    process_sync_queue_item.delay(result.id)
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
                results.append({
                    "record_uuid": record_uuid,
                    "status": "INCOMPATIBLE",
                    "message": str(exc),
                })
            except Exception as exc:  # noqa: BLE001 - se reporta por operación
                rejected += 1
                results.append({
                    "record_uuid": record_uuid,
                    "status": "ERROR",
                    "message": str(exc),
                })

        return {
            "accepted": accepted,
            "rejected": rejected,
            "conflicts": conflicts,
            "results": results,
        }

    @staticmethod
    def pull_changes(since=None, source_table=None, limit=100):
        """Devuelve los items de cola para que el cliente sincronice."""
        parsed_since = parse_datetime(since) if since else None
        items = SyncQueueRepository.get_for_pull(
            since=parsed_since,
            source_table=source_table,
            limit=limit,
        )
        return [
            {
                "uuid": str(item.uuid),
                "source_table": item.source_table,
                "operation": item.operation or None,
                "record_uuid": item.record_uuid,
                "payload": item.payload,
                "status": item.status or None,
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
            last_error=None,
        )

    @staticmethod
    @transaction.atomic
    def mark_failed(sync_id, error_message):
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if not sync_item:
            return None
        status = SyncStatusChoices.PENDING if sync_item.attempts < 3 else SyncStatusChoices.ERROR
        return SyncQueueRepository.update(
            sync_item.id,
            status=status,
            last_error=error_message,
        )


def _is_incompatible(client_version, min_version):
    try:
        client_parts = [int(x) for x in client_version.split(".")]
        min_parts = [int(x) for x in min_version.split(".")]
        for i in range(max(len(client_parts), len(min_parts))):
            c = client_parts[i] if i < len(client_parts) else 0
            m = min_parts[i] if i < len(min_parts) else 0
            if c < m:
                return True
        return False
    except (ValueError, IndexError):
        return True
