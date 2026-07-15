from abc import ABC, abstractmethod


class SyncBatchRepositoryInterface(ABC):

    @classmethod
    @abstractmethod
    def get_by_client_batch_id(cls, client_batch_id):
        ...

    @classmethod
    @abstractmethod
    def create(cls, **data):
        ...

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        ...

    @classmethod
    @abstractmethod
    def get_by_uuid(cls, uuid):
        ...


class SyncQueueRepositoryInterface(ABC):

    @classmethod
    @abstractmethod
    def get_all(cls, active_only=True):
        ...

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk):
        ...

    @classmethod
    @abstractmethod
    def create(cls, **data):
        ...

    @classmethod
    @abstractmethod
    def update(cls, pk, **data):
        ...

    @classmethod
    @abstractmethod
    def delete(cls, pk):
        ...

    @classmethod
    @abstractmethod
    def get_pending(cls):
        ...

    @classmethod
    @abstractmethod
    def get_failed(cls):
        ...

    @classmethod
    @abstractmethod
    def is_synced(cls, idempotency_key):
        ...

    @classmethod
    @abstractmethod
    def get_for_pull(cls, since=None, source_table=None, limit=100):
        ...
