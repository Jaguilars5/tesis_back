# Módulo `integration` — Sincronización Offline-First — Estructura

## Árbol de archivos

```
integration/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # → api/urls.py (sync-queue, sync/push, sync/pull)
├── README.md
│
├── models/
│   ├── __init__.py             # SyncQueue, SyncableModel (abstracto), SyncStatusChoices, SyncOperationChoices
│   ├── sync_queue.py           # SyncQueue (TimeStampedModel)
│   └── syncable_mixin.py       # SyncableModel (abstracto) + SyncStatusChoices + SyncOperationChoices
│
├── repositories/
│   ├── __init__.py             # SyncQueueRepository
│   └── sync_repository.py      # SyncQueueRepository (get_pending, get_failed)
│
├── services/
│   ├── __init__.py             # SyncQueueService
│   ├── sync_service.py         # SyncQueueService (queue_operation con idempotencia)
│   └── conflict_resolver.py    # ConflictResolutionStrategy
│
├── tasks/
│   ├── __init__.py
│   └── sync_tasks.py           # BaseSyncHandler, register_sync_handler, process_sync_queue_item, process_pending_sync_batch
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers/
│   │   ├── __init__.py         # SyncQueueSerializer
│   │   ├── sync_serializer.py
│   │   └── catalog_serializers.py  # VACÍO
│   ├── urls.py                 # Router: solo sync-queue + sync/push/ + sync/pull/
│   └── views/
│       ├── __init__.py
│       ├── sync_viewset.py     # SyncQueueViewSet (CRUD + acciones push/pull)
│       └── catalog_views.py    # VACÍO
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_permissions.py
    ├── test_models.py
    └── test_repositories.py
```

## Workflow

```
Dispositivo offline → POST /sync/push/ (batch de operaciones)
    ↓
SyncQueueService.queue_operation() — validación idempotencia
    ↓
SyncQueue.create(idempotency_key, status=PENDING)
    ↓
Celery: process_sync_queue_item()
    ↓
BaseSyncHandler.handle_insert/update/delete() — con ConflictResolutionStrategy
    ↓
SyncQueue.status = SYNCED
```

## Guía de imports

```python
from apps.integration.models import SyncQueue, SyncableModel, SyncStatusChoices, SyncOperationChoices

from apps.integration.services.sync_service import SyncQueueService, IncompatibleSchemaError
from apps.integration.services.conflict_resolver import ConflictResolutionStrategy

from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler, process_sync_queue_item
```
