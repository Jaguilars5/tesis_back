# Módulo `integration` — Sincronización Offline-First

> Gestiona la cola de sincronización entre dispositivos offline y el servidor central, resolución de conflictos y versionado de esquemas.

## Modelos (1 concreto + 1 mixin abstracto)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `SyncQueue` | Cola de operaciones de sincronización | `uuid`, `idempotency_key` (unique, SHA-256), `user` (FK), `source_table`, `record_uuid`, `operation` (choices: CREATE/UPDATE/DELETE), `payload` (JSON), `previous_state` (JSON), `attempts`, `max_attempts` (default 5), `last_error`, `last_attempt_at`, `status` (choices: PENDING/PROCESSING/SYNCED/ERROR/CONFLICT), `conflict_detected`, `resolution_strategy`, `processed_by`, `processed_at`, `resolved_by`, `resolution_notes`. Hereda `TimeStampedModel` |
| `SyncableModel` | Mixin abstracto para modelos sincronizables | `uuid`, `sync_status`, `sync_version`, `synced_at`, `device_origin`, `conflict_resolved`, `conflict_notes` |

> **Nota:** `SyncOperation` y `SyncStatus` **no existen como modelos**. Son `TextChoices` dentro de `syncable_mixin.py` (`SyncOperationChoices`, `SyncStatusChoices`). `SyncSchemaVersion` fue eliminado (migración 0004).

## Repositorios (1)

| Repositorio | Métodos adicionales |
|-------------|---------------------|
| `SyncQueueRepository` | `get_all()` con `select_related("user")`; `get_pending()`, `get_failed()` |

## Servicios (2)

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `SyncQueueService` | `queue_operation()`, `mark_processing()`, `mark_completed()`, `mark_failed()` | Encola operación con idempotencia; gestión de ciclo de vida |
| `ConflictResolutionStrategy` | `resolve(source_table, local, remote)` | Resuelve conflictos por tabla con estrategias: `LAST_WRITE_WINS`, `SERVER_WINS`, `MANUAL` |

### Estrategias de resolución

| Tabla | Estrategia |
|-------|-----------|
| student_note, attendance, conduct_incident, project_note, behavior_evaluation, skill_evaluation, diagnostic_evaluation | `LAST_WRITE_WINS` |
| early_alert, evaluative_activity, recovery_process, learning_report | `SERVER_WINS` |
| enrollment | `MANUAL` |

## Handlers de Sincronización (13 registrados via `@register_sync_handler`)

| App | Handler | source_table |
|-----|---------|-------------|
| grading | `StudentNoteSyncHandler` | `student_note` |
| grading | `ProjectNoteSyncHandler` | `project_note` |
| grading | `EvaluativeActivitySyncHandler` | `evaluative_activity` |
| grading | `RecoveryProcessSyncHandler` | `recovery_process` |
| grading | `LearningReportSyncHandler` | `learning_report` |
| attendance | `AttendanceSyncHandler` | `attendance` |
| behavior | `ConductIncidentSyncHandler` | `conduct_incident` |
| behavior | `BehaviorEvaluationSyncHandler` | `behavior_evaluation` |
| behavior | `SkillEvaluationSyncHandler` | `skill_evaluation` |
| behavior | `DiagnosticEvaluationSyncHandler` | `diagnostic_evaluation` |
| students | `EnrollmentSyncHandler` | `enrollment` |
| analytics | `EarlyAlertSyncHandler` | `early_alert` |

## API — Endpoints

| Método | Endpoint | Tipo | Permiso |
|--------|----------|------|---------|
| GET/POST | `/api/integration/sync-queue/` | SyncQueueViewSet | `integration.view/create_syncqueue` |
| GET/PUT/PATCH/DEL | `/api/integration/sync-queue/{id}/` | SyncQueueViewSet | `integration.view/update/delete_syncqueue` |
| POST | `/api/integration/sync/push/` | `SyncQueueViewSet.push` | `IsAuthenticated` |
| GET | `/api/integration/sync/pull/` | `SyncQueueViewSet.pull` | `IsAuthenticated` |

> **No existen** endpoints para `sync-operations/` ni `sync-statuses/` (no son modelos).

## Tareas Celery (2)

| Tarea | Descripción |
|-------|-------------|
| `process_sync_queue_item` | Procesa un item individual con resolución de conflictos |
| `process_pending_sync_batch` | Dispara procesamiento batch de items pendientes |

## Tests

```bash
python manage.py test apps.integration --settings=config.settings.test
```

## Modelos que heredan `SyncableModel` (12)

- StudentNote, Attendance, ConductIncident, ProjectNote
- EarlyAlert, EvaluativeActivity, Enrollment
- RecoveryProcess, BehaviorEvaluation
- SkillEvaluation, DiagnosticEvaluation, LearningReport

## Idempotencia

`SyncQueue.idempotency_key` = SHA-256 de `source_table:record_uuid:operation_code`. Si ya existe un item con la misma key en estado `SYNCED`, se omite silenciosamente.

## Dependencias

- `iam.User`
