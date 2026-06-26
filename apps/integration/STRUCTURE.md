# Módulo `integration` — Sincronización Offline-First — Estructura

## Árbol de archivos (Layered Pattern)

```
integration/
├── __init__.py                     # Lazy loader (SyncQueue, SyncableModel, SyncQueueRepository, SyncQueueService, ...)
├── admin.py
├── apps.py
├── urls.py                         # → api/urls.py
├── permissions.py                  # ACTION_PERMISSIONS con constantes tipadas
├── README.md
│
├── domain/                         # Capa de dominio (interfaces + lógica de negocio)
│   ├── __init__.py
│   ├── repositories.py             # SyncQueueRepositoryInterface (ABC)
│   └── services.py                 # SyncQueueService + ConflictResolutionStrategy + IncompatibleSchemaError
│
├── infrastructure/                 # Capa de infraestructura (Django ORM)
│   ├── __init__.py
│   ├── models.py                   # SyncQueue (TimeStampedModel), SyncableModel (abstracto), SyncStatusChoices, SyncOperationChoices
│   └── repositories.py             # SyncQueueRepository (BaseRepository + SyncQueueRepositoryInterface)
│
├── application/                    # Capa de aplicación (serializers + validators)
│   ├── __init__.py
│   ├── serializers.py              # SyncQueueSerializer
│   └── validators.py               # Validaciones de negocio
│
├── api/                            # Capa de presentación (ViewSets, URLs, filtros)
│   ├── __init__.py
│   ├── views.py                    # SyncQueueViewSet (CRUD + push + pull)
│   ├── urls.py                     # Router: sync-queue + sync/push/ + sync/pull/
│   └── README.md
│
├── tasks/                          # Tareas Celery (cross-cutting)
│   ├── __init__.py
│   └── sync_tasks.py               # BaseSyncHandler, register_sync_handler, process_sync_queue_item, process_pending_sync_batch
│
├── models/                         # (shims backward-compat → infrastructure/)
├── repositories/                   # (shims backward-compat → infrastructure/)
├── services/                       # (shims backward-compat → domain/)
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_permissions.py
    └── test_models.py
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
# Desde infraestructura (modelos directos)
from apps.integration.infrastructure.models import SyncQueue, SyncableModel, SyncStatusChoices, SyncOperationChoices

# Desde dominio (servicios)
from apps.integration.domain.services import SyncQueueService, ConflictResolutionStrategy, IncompatibleSchemaError

# Desde aplicación (serializers)
from apps.integration.application.serializers import SyncQueueSerializer

# Tareas Celery
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler, process_sync_queue_item

# Lazy loader (carga bajo demanda)
from apps.integration import SyncQueue, SyncQueueService, SyncQueueRepository
```

## Backward Compatibility

Los paths antiguos (`models/`, `repositories/`, `services/`) se mantienen como shims que re-exportan desde las nuevas ubicaciones canónicas. Cualquier import como `from apps.integration.models.syncable_mixin import SyncableModel` sigue funcionando.
