# Módulo `configuration` — Configuración del Sistema

> Almacena pares clave-valor para opciones globales del sistema.

## Modelos

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `SystemConfig` | Configuración clave-valor del sistema | `key` (unique), `value`, `description`, `created_at`, `updated_at` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `ConfigService` | `get(key, default=None)` | Obtener valor de configuración por clave |
| `ConfigService` | `set(key, value, description="")` | Establecer o actualizar configuración |
| `ConfigService` | `get_all()` | Obtener todas las configuraciones como diccionario |

## API

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| GET | `/api/configuration/system-config/` | Listar configuraciones | `configuration.view_systemconfig` |
| POST | `/api/configuration/system-config/` | Crear configuración | `configuration.create_systemconfig` |
| GET | `/api/configuration/system-config/{key}/` | Obtener por clave | `configuration.view_systemconfig` |
| PATCH | `/api/configuration/system-config/{key}/` | Actualizar | `configuration.update_systemconfig` |
| DELETE | `/api/configuration/system-config/{key}/` | Eliminar | `configuration.delete_systemconfig` |

## Respuestas Enriquecidas

Todas las respuestas siguen el formato `{"ok": true, "data": {...}, "msg": ""}`.

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

Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Tests

```bash
python manage.py test apps.configuration --settings=config.settings.test
```

## Dependencias

- Ninguna (app independiente)
