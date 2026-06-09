# API - Módulo Integration

Esta API gestiona la cola de sincronización offline-servidor, operaciones y estados de sincronización.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `sync-queue/` | GET | `integration.view_syncqueue` |
| `sync-queue/` | POST | `integration.create_syncqueue` |
| `sync-queue/{id}/` | GET | `integration.view_syncqueue` |
| `sync-queue/{id}/` | PATCH | `integration.update_syncqueue` |
| `sync-queue/{id}/` | DELETE | `integration.delete_syncqueue` |
| `sync-operations/` | GET/POST | `integration.view/create_sync_operation` |
| `sync-operations/{id}/` | GET/PATCH/DELETE | `integration.view/update/delete_sync_operation` |
| `sync-statuses/` | GET/POST | `integration.view/create_sync_status` |
| `sync-statuses/{id}/` | GET/PATCH/DELETE | `integration.view/update/delete_sync_status` |

## Cola de Sincronización (`/api/integration/sync-queue/`)

### Crear item

**POST** `/api/integration/sync-queue/`

```json
{
  "user": 1,
  "source_table": "students.Student",
  "record_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "operation": 1,
  "payload": {"names": "Juan", "last_names": "Pérez"}
}
```

Al crear un item, se dispara automáticamente una tarea Celery para procesarlo.

## Catálogos

### Operaciones (`/api/integration/sync-operations/`)

Catálogo de tipos de operación: `INSERT`, `UPDATE`, `DELETE`.

### Estados (`/api/integration/sync-statuses/`)

Catálogo de estados: `PENDIENTE`, `PROCESADO`, `ERROR`.
