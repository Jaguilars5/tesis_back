from ..domain.repositories import SyncBatchRepositoryInterface, SyncQueueRepositoryInterface
from ..infrastructure.models import SyncBatch, SyncQueue, SyncStatusChoices
from apps.core.repositories.base import BaseRepository


class SyncBatchRepository(BaseRepository, SyncBatchRepositoryInterface):
    model = SyncBatch

    @classmethod
    def get_by_client_batch_id(cls, client_batch_id):
        return cls.model.objects.filter(client_batch_id=client_batch_id).first()

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.model.objects.filter(uuid=uuid).first()

    @classmethod
    def count_failed_in_batch(cls, batch_id):
        return cls.model.objects.filter(
            batch_id=batch_id,
            status=SyncStatusChoices.ERROR,
        ).count()

    @classmethod
    def count_pending_in_batch(cls, batch_id):
        from ..infrastructure.models import SyncStatusChoices
        return SyncQueue.objects.filter(
            batch_id=batch_id,
            status=SyncStatusChoices.PENDING,
        ).count()


class SyncQueueRepository(BaseRepository, SyncQueueRepositoryInterface):
    model = SyncQueue

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("user").order_by("-created_at")

    @classmethod
    def get_pending(cls):
        return cls.model.objects.filter(
            status=SyncStatusChoices.PENDING
        ).order_by("created_at")

    @classmethod
    def get_failed(cls):
        return cls.model.objects.filter(
            status=SyncStatusChoices.ERROR
        ).order_by("-created_at")

    @classmethod
    def is_synced(cls, idempotency_key):
        return cls.model.objects.filter(
            idempotency_key=idempotency_key,
            status=SyncStatusChoices.SYNCED,
        ).exists()

    @classmethod
    def get_by_idempotency_key(cls, idempotency_key):
        return cls.model.objects.filter(idempotency_key=idempotency_key).first()

    @classmethod
    def get_for_pull(cls, since=None, source_table=None, limit=100):
        queryset = cls.model.objects.all()
        if since is not None:
            queryset = queryset.filter(processed_at__gte=since)
        if source_table:
            queryset = queryset.filter(source_table=source_table)
        return queryset.order_by("-created_at")[:limit]

    @classmethod
    def get_by_batch(cls, batch_id):
        return cls.model.objects.filter(batch_id=batch_id).order_by("-created_at")
