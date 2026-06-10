# API - Módulo Configuration

Esta API gestiona las configuraciones clave-valor del sistema.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `system-config/` | GET | `configuration.view_systemconfig` |
| `system-config/` | POST | `configuration.create_systemconfig` |
| `system-config/{key}/` | GET | `configuration.view_systemconfig` |
| `system-config/{key}/` | PATCH | `configuration.update_systemconfig` |
| `system-config/{key}/` | DELETE | `configuration.delete_systemconfig` |

---

## Configuraciones del Sistema (`/api/configuration/system-config/`)

### GET — Listar configuraciones

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "key": "SITE_NAME",
        "value": "Mi Colegio",
        "description": "Nombre del sitio",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-06-01T12:00:00Z"
      },
      {
        "id": 2,
        "key": "ACADEMIC_YEAR",
        "value": "2025-2026",
        "description": "Año lectivo vigente",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      }
    ]
  },
  "msg": ""
}
```

### POST — Crear configuración

```json
{
  "key": "SITE_NAME",
  "value": "Mi Colegio",
  "description": "Nombre del sitio"
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "key": "SITE_NAME",
    "value": "Mi Colegio",
    "description": "Nombre del sitio",
    "created_at": "2025-06-08T12:00:00Z",
    "updated_at": "2025-06-08T12:00:00Z"
  },
  "msg": ""
}
```

### GET — Obtener por clave

**GET** `/api/configuration/system-config/SITE_NAME/`

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "key": "SITE_NAME",
    "value": "Mi Colegio",
    "description": "Nombre del sitio",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-06-01T12:00:00Z"
  },
  "msg": ""
}
```

### PATCH — Actualizar configuración

**PATCH** `/api/configuration/system-config/SITE_NAME/`

```json
{
  "value": "Nuevo Nombre del Colegio"
}
```

**Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "key": "SITE_NAME",
    "value": "Nuevo Nombre del Colegio",
    "description": "Nombre del sitio",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-06-08T12:00:00Z"
  },
  "msg": ""
}
```

### DELETE — Eliminar configuración

**DELETE** `/api/configuration/system-config/SITE_NAME/`

**Response (204 No Content):**
```json
{
  "ok": true,
  "data": null,
  "msg": "Configuración eliminada exitosamente"
}
```

## Formato de Clave-Valor

- `key`: Identificador único (máx. 255 caracteres). Se recomienda usar `UPPER_SNAKE_CASE`.
- `value`: Texto libre con el valor de la configuración.
- `description`: Texto opcional que describe el propósito de la configuración.
