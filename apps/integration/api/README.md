# API - Módulo Integration

Esta API gestiona la cola de sincronización offline-servidor, operaciones, estados, push/pull batch y versionado de esquemas.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `sync-queue/` | GET/POST | `integration.view/create_syncqueue` |
| `sync-queue/{id}/` | GET/PATCH/DELETE | `integration.view/update/delete_syncqueue` |
| `sync-operations/` | GET/POST | `integration.view/create_sync_operation` |
| `sync-operations/{id}/` | GET/PATCH/DELETE | `integration.view/update/delete_sync_operation` |
| `sync-statuses/` | GET/POST | `integration.view/create_sync_status` |
| `sync-statuses/{id}/` | GET/PATCH/DELETE | `integration.view/update/delete_sync_status` |
| `sync/push/` | POST | Requiere autenticación |
| `sync/pull/` | GET | Requiere autenticación |

---

## Push Batch (`POST /api/integration/sync/push/`)

El cliente envía un lote de operaciones realizadas offline. El servidor encola cada operación con validación de idempotencia y compatibilidad de schema.

### Request

```json
{
  "operations": [
    {
      "source_table": "student_note",
      "operation": "INSERT",
      "record_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "payload": {
        "enrollment": 1,
        "evaluative_activity": 1,
        "numeric_score": 8.5,
        "grading_mode": "NUMERIC",
        "sync_version": 1,
        "device_origin": "tablet-001"
      },
      "client_version": "1.2.0"
    },
    {
      "source_table": "attendance",
      "operation": "UPDATE",
      "record_uuid": "660e8400-e29b-41d4-a716-446655440001",
      "payload": {
        "attendance_status": 1,
        "sync_version": 2
      },
      "client_version": "1.2.0"
    }
  ]
}
```

### Response

```json
{
  "ok": true,
  "data": {
    "accepted": 2,
    "rejected": 0,
    "conflicts": 0,
    "results": [
      {
        "record_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "status": "QUEUED",
        "queue_id": 101
      },
      {
        "record_uuid": "660e8400-e29b-41d4-a716-446655440001",
        "status": "QUEUED",
        "queue_id": 102
      }
    ]
  },
  "msg": ""
}
```

### Posibles estados de resultado

| status | Significado |
|--------|-------------|
| `QUEUED` | Operación encolada exitosamente |
| `SYNCED` | Operación duplicada ya procesada (idempotencia) |
| `INCOMPATIBLE` | Versión de cliente incompatible con el schema del servidor |
| `REJECTED` | Operación rechazada por validación |
| `ERROR` | Error interno al procesar |

---

## Pull (`GET /api/integration/sync/pull/`)

El cliente consulta los cambios procesados por el servidor desde un timestamp.

### Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `since` | datetime | Timestamp ISO 8601 de última consulta |
| `source_table` | string | Filtrar por tabla (opcional) |

### Request

```
GET /api/integration/sync/pull/?since=2025-06-01T00:00:00Z&source_table=student_note
```

### Response

```json
{
  "ok": true,
  "data": {
    "count": 1,
    "results": [
      {
        "uuid": "770e8400-e29b-41d4-a716-446655440002",
        "source_table": "student_note",
        "operation": "INSERT",
        "record_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "payload": {"numeric_score": 8.5, "sync_version": 1},
        "status": "PROCESADO",
        "processed_at": "2025-06-08T12:00:00Z"
      }
    ]
  },
  "msg": ""
}
```

---

## Cola de Sincronización (`/api/integration/sync-queue/`)

### POST — Crear item

```json
{
  "user": 1,
  "source_table": "student_note",
  "record_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "operation": 1,
  "payload": {"numeric_score": 8.5, "grade_type": 1}
}
```

**Nota:** El campo `idempotency_key` se genera automáticamente al guardar.

---

## Catálogos

### Operaciones (`/api/integration/sync-operations/`)

```json
{"code": "INSERT", "name": "Insertar"}
{"code": "UPDATE", "name": "Actualizar"}
{"code": "DELETE", "name": "Eliminar"}
```

### Estados (`/api/integration/sync-statuses/`)

| code | name |
|------|------|
| PENDIENTE | Pendiente |
| PROCESANDO | En procesamiento |
| PROCESADO | Procesado |
| SYNCED | Sincronizado |
| ERROR | Error |
| CONFLICT | Conflicto detectado |

---

## Versionado de Payload

El modelo `SyncSchemaVersion` permite registrar y validar la versión del schema de payload por tabla:

```json
{
  "model_name": "student_note",
  "schema_version": 2,
  "fields_hash": "a1b2c3d4e5f6...",
  "min_client_version": "1.0.0"
}
```

Durante el push, si `client_version < min_client_version`, la operación es rechazada con `status: INCOMPATIBLE`.
