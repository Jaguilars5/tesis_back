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

## Configuraciones del Sistema (`/api/configuration/system-config/`)

### Listar

**GET** `/api/configuration/system-config/`

### Crear

**POST** `/api/configuration/system-config/`

```json
{
  "key": "SITE_NAME",
  "value": "Mi Colegio",
  "description": "Nombre del sitio"
}
```

### Actualizar

**PATCH** `/api/configuration/system-config/{key}/`

```json
{
  "value": "Nuevo Nombre"
}
```
