# Módulo `integration` — Sincronización Offline-First — Estructura

## Árbol de archivos

```
integration/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py                     # Router: sync-queue, sync-operations, sync-statuses + push/pull
├── README.md
│
├── models/
│   ├── __init__.py             # SyncQueue, SyncOperation, SyncStatus, SyncableModel, SyncSchemaVersion
│   ├── sync_queue.py           # SyncQueue (idempotency_key, conflict_detected, resolution_strategy)
│   ├── sync_operation.py       # SyncOperation (INSERT, UPDATE, DELETE)
│   ├── sync_status.py          # SyncStatus (PENDIENTE, PROCESANDO, PROCESADO, SYNCED, ERROR, CONFLICT)
│   ├── syncable_mixin.py       # SyncableModel (abstracto — mixin para modelos sincronizables)
│   └── sync_schema.py          # SyncSchemaVersion (versionado de payload)
│
├── repositories/
│   ├── __init__.py
│   ├── sync_queue_repository.py
│   ├── sync_operation_repository.py
│   └── sync_status_repository.py
│
├── services/
│   ├── __init__.py
│   ├── sync_service.py         # SyncQueueService (queue_operation con idempotencia + schema validation)
│   └── conflict_resolver.py    # ConflictResolutionStrategy (LAST_WRITE_WINS, SERVER_WINS, MANUAL)
│
├── tasks/
│   └── sync_tasks.py           # BaseSyncHandler, process_sync_queue_item, process_pending_sync_batch
│
├── api/
│   ├── __init__.py
│   ├── README.md
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── sync_serializers.py
│   ├── urls.py
│   └── views/
│       ├── __init__.py
│       ├── catalog_views.py    # SyncOperationViewSet, SyncStatusViewSet
│       ├── sync_viewset.py     # SyncQueueViewSet
│       └── sync_bulk_view.py   # sync_push(), sync_pull() (endpoints bulk)
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_api_permissions.py
    ├── test_models.py
    └── test_repositories.py
```

## Modelos sync (15 handlers registrados)

Los handlers se registran via decorador `@register_sync_handler(source_table)` en cada app:

| App | source_table | Handler |
|-----|-------------|---------|
| grading | student_note | StudentNoteSyncHandler |
| grading | project_note | ProjectNoteSyncHandler |
| grading | evaluative_activity | EvaluativeActivitySyncHandler |
| grading | recovery_process | RecoveryProcessSyncHandler |
| grading | recovery_session | RecoverySessionSyncHandler |
| grading | learning_report | LearningReportSyncHandler |
| attendance | attendance | AttendanceSyncHandler |
| behavior | conduct_incident | ConductIncidentSyncHandler |
| behavior | behavior_evaluation | BehaviorEvaluationSyncHandler |
| behavior | skill_evaluation | SkillEvaluationSyncHandler |
| behavior | diagnostic_evaluation | DiagnosticEvaluationSyncHandler |
| students | enrollment | EnrollmentSyncHandler |
| analytics | early_alert | EarlyAlertSyncHandler |

## Workflow

```
Dispositivo offline → POST /sync/push/ (batch de operaciones)
    ↓
SyncQueueService.queue_operation() — validación idempotencia + schema
    ↓
SyncQueue.create(idempotency_key, status=PENDIENTE)
    ↓
Celery: process_sync_queue_item()
    ↓
BaseSyncHandler.handle_insert/update/delete() — con ConflictResolutionStrategy
    ↓
SyncQueue.status = PROCESADO
```

## Guía de imports

```python
from apps.integration.models import SyncQueue, SyncableModel, SyncStatusChoices, SyncSchemaVersion
from apps.integration.services.sync_service import SyncQueueService, IncompatibleSchemaError
from apps.integration.services.conflict_resolver import ConflictResolutionStrategy
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler, process_sync_queue_item
```
