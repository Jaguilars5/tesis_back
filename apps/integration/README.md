# Módulo `integration` — Sincronización Offline-Servidor

## Descripción
Gestiona cola de operaciones de sincronización entre dispositivos offline y el servidor central.

## Modelos (3)
- **SyncQueue** — Cola de operaciones de sincronización
- **SyncOperation** — Catálogo de tipos de operación (INSERT, UPDATE, DELETE)
- **SyncStatus** — Catálogo de estados (PENDIENTE, PROCESADO, ERROR)

## API Endpoints (`/api/integration/`)
- `sync-queue/` — CRUD de items de sincronización
- `sync-operations/` — CRUD de tipos de operación
- `sync-statuses/` — CRUD de estados de sincronización

## Servicios
- `SyncQueueService` — Encolar, marcar procesado/fallido

## Repositorios (3)
- `SyncQueueRepository`, `SyncOperationRepository`, `SyncStatusRepository`

## Tareas Celery
- `process_sync_queue_item` — Procesa un item individual
- `process_pending_sync_batch` — Dispara procesamiento batch

## Tests
- 31 tests (modelos, API, permisos RBAC)

## Dependencias
- `iam.User`, `integration.SyncOperation`, `integration.SyncStatus`
