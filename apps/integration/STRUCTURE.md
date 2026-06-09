# Estructura de Integration

## models/ (3)
- `sync_queue.py`, `sync_operation.py`, `sync_status.py`

## api/ (3 ViewSets)
- `SyncQueueViewSet`, `SyncOperationViewSet`, `SyncStatusViewSet`

## services/
- `sync_service.py` — SyncQueueService (encolar, marcar procesado/fallido)

## repositories/ (3)
- `SyncQueueRepository`, `SyncOperationRepository`, `SyncStatusRepository`

## tasks/
- `sync_tasks.py` — Tareas Celery para procesamiento asíncrono

## tests/ (31 tests)
- `test_models.py`, `test_api.py`, `test_api_permissions.py`
