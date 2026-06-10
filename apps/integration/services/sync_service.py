import hashlib

from django.db import transaction
from django.utils import timezone

from ..repositories import SyncQueueRepository
from ..repositories.sync_status_repository import SyncStatusRepository
from ..models import SyncQueue, SyncSchemaVersion


class IncompatibleSchemaError(ValueError):
    pass


class SyncQueueService:
    @staticmethod
    @transaction.atomic
    def queue_operation(user, source_table, record_uuid, operation, payload=None, client_version=None):
        if client_version:
            try:
                schema = SyncSchemaVersion.objects.get(model_name=source_table)
                if _is_incompatible(client_version, schema.min_client_version):
                    raise IncompatibleSchemaError(
                        f"Client v{client_version} requires schema v{schema.min_client_version}"
                    )
            except SyncSchemaVersion.DoesNotExist:
                pass

        idempotency_key = SyncQueueService._build_idempotency_key(source_table, record_uuid, operation.code if hasattr(operation, 'code') else operation)

        procesado_status = SyncStatusRepository.get_by_code("PROCESADO")
        if SyncQueue.objects.filter(idempotency_key=idempotency_key, status=procesado_status).exists():
            return None

        status_pendiente = SyncStatusRepository.get_by_code("PENDIENTE")
        return SyncQueueRepository.create(
            user=user,
            source_table=source_table,
            record_uuid=record_uuid,
            operation=operation,
            payload=payload or {},
            status=status_pendiente,
            idempotency_key=idempotency_key,
            attempts=0,
        )

    @staticmethod
    def _build_idempotency_key(source_table, record_uuid, operation_code):
        raw = f"{source_table}:{record_uuid}:{operation_code}"
        return hashlib.sha256(raw.encode()).hexdigest()[:64]

    @staticmethod
    @transaction.atomic
    def mark_processing(sync_id):
        sync_item = SyncQueueRepository.get_by_id(sync_id)
        if sync_item:
            status_procesando = SyncStatusRepository.get_by_code("PROCESANDO")
            SyncQueueRepository.update(
                sync_item.id,
                status=status_procesando,
                attempts=sync_item.attempts + 1,
                last_attempt_at=timezone.now(),
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
