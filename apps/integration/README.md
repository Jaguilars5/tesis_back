# Módulo `integration` — Sincronización Offline-First

> Gestiona la cola de sincronización entre dispositivos offline y el servidor central, resolución de conflictos y versionado de esquemas.

## Modelos

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `SyncQueue` | Cola de operaciones de sincronización | `idempotency_key` (unique), `user`, `source_table`, `record_uuid`, `operation`, `payload`, `previous_state`, `attempts`, `max_attempts` (default 5), `status`, `conflict_detected`, `resolution_strategy`, `processed_by`, `resolved_by` |
| `SyncOperation` | Catálogo de operaciones | `code` (INSERT/UPDATE/DELETE), `name` |
| `SyncStatus` | Catálogo de estados | `code` (PENDIENTE/PROCESANDO/PROCESADO/SYNCED/ERROR/CONFLICT), `name` |
| `SyncSchemaVersion` | Versionado de esquema de payload | `model_name`, `schema_version`, `fields_hash`, `min_client_version` |
| `SyncableModel` (abstracto) | Mixin base para modelos sincronizables | `uuid`, `sync_status`, `sync_version`, `synced_at`, `device_origin`, `conflict_resolved`, `conflict_notes` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `SyncQueueService` | `queue_operation()` | Encola operación con idempotencia y validación de schema |
| `SyncQueueService` | `mark_processing()`, `mark_completed()`, `mark_failed()` | Gestión de ciclo de vida de items |
| `ConflictResolutionStrategy` | `resolve(source_table, local, remote)` | Resuelve conflictos por estrategia por entidad |
| `ConflictResolutionStrategy` | `_last_write_wins()`, `_server_wins()`, `_manual_resolution_required()` | Estrategias de resolución |

### Estrategias de resolución por entidad

| Modelo | Estrategia | Comportamiento |
|--------|-----------|----------------|
| StudentNote, Attendance, ConductIncident, ProjectNote | `LAST_WRITE_WINS` | Gana la versión con mayor `sync_version` |
| EarlyAlert, EvaluativeActivity, RecoveryProcess, LearningReport | `SERVER_WINS` | El servidor siempre prevalece |
| Enrollment | `MANUAL` | Requiere intervención humana, marca `CONFLICT` |

## Handlers de Sincronización (15 registrados)

| App | Handler | source_table |
|-----|---------|-------------|
| grading | `StudentNoteSyncHandler` | `student_note` |
| grading | `ProjectNoteSyncHandler` | `project_note` |
| grading | `EvaluativeActivitySyncHandler` | `evaluative_activity` |
| grading | `RecoveryProcessSyncHandler` | `recovery_process` |
| grading | `RecoverySessionSyncHandler` | `recovery_session` |
| grading | `LearningReportSyncHandler` | `learning_report` |
| attendance | `AttendanceSyncHandler` | `attendance` |
| behavior | `ConductIncidentSyncHandler` | `conduct_incident` |
| behavior | `BehaviorEvaluationSyncHandler` | `behavior_evaluation` |
| behavior | `SkillEvaluationSyncHandler` | `skill_evaluation` |
| behavior | `DiagnosticEvaluationSyncHandler` | `diagnostic_evaluation` |
| students | `EnrollmentSyncHandler` | `enrollment` |
| analytics | `EarlyAlertSyncHandler` | `early_alert` |

## API

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| GET/POST | `/api/integration/sync-queue/` | Listar/Crear items | `integration.view/create_syncqueue` |
| GET/PATCH/DELETE | `/api/integration/sync-queue/{id}/` | CRUD individual | `integration.view/update/delete_syncqueue` |
| GET/POST | `/api/integration/sync-operations/` | CRUD operaciones | `integration.view/create_sync_operation` |
| GET/POST | `/api/integration/sync-statuses/` | CRUD estados | `integration.view/create_sync_status` |
| POST | `/api/integration/sync/push/` | Push batch desde cliente | `IsAuthenticated` |
| GET | `/api/integration/sync/pull/?since=&source_table=` | Pull cambios desde servidor | `IsAuthenticated` |

## Tareas Celery

| Tarea | Descripción |
|-------|-------------|
| `process_sync_queue_item` | Procesa un item individual con resolución de conflictos |
| `process_pending_sync_batch` | Dispara procesamiento batch de items pendientes |

## Tests

```bash
python manage.py test apps.integration --settings=config.settings.test
```

## Dependencias

- `iam.User`
- `integration.SyncOperation`, `integration.SyncStatus`

## Modelos que heredan SyncableModel (13)

- `StudentNote`, `Attendance`, `ConductIncident`, `ProjectNote`
- `EarlyAlert`, `EvaluativeActivity`, `Enrollment`
- `RecoveryProcess`, `RecoverySession`, `BehaviorEvaluation`
- `SkillEvaluation`, `DiagnosticEvaluation`, `LearningReport`

## Idempotencia

Cada `SyncQueue` genera automáticamente un `idempotency_key` vía SHA-256 de `source_table:record_uuid:operation_code`. Si ya existe un item con la misma clave en estado `PROCESADO`, se rechaza el duplicado silenciosamente.
