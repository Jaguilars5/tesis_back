# Arquitectura y Estructura del Proyecto

Este documento describe la arquitectura técnica y la organización de archivos del backend del sistema de gestión académica.

## Arquitectura del Proyecto

El sistema sigue una arquitectura orientada a dominios, diseñada para ser escalable, mantenible y desacoplada. Se utiliza Django como framework base con Django REST Framework para la API.

### Capas de la Aplicación

Cada módulo (app) del sistema se divide en las siguientes capas funcionales:

1.  **Capa de Modelos (Models)**: Define el esquema de la base de datos utilizando el ORM de Django. Los archivos se nombran en `snake_case` (ej: `student_note.py`, `attendance_status.py`).
2.  **Capa de Repositorios (Repositories)**: Abstrae el acceso a los datos. Todas las consultas ORM complejas se centralizan aquí.
3.  **Capa de Servicios (Services)**: Contiene la lógica de negocio pura. Orquestan operaciones entre repositorios.
4.  **Capa de API (REST API)**: Gestiona la entrada y salida mediante ViewSets de DRF con serializadores.

## Organización del Directorio apps/

```
apps/
├── academic/     # Períodos, secciones, materias, ofertas, asignaciones docente
├── accounts/      # Usuarios, personas, roles, permisos, auth JWT
├── analytics/    # Scores de riesgo, snapshots de métricas, factores
├── core/         # Utilidades transversales, permisos, respuestas estándar
├── grading/      # Notas, asistencia, incidentes, evaluaciones de conducta
├── institutions/ # Instituciones, años escolares, aulas, tipos de sala
├── scheduling/   # Horarios, franjas, disponibilidad, restricciones
└── students/     # Estudiantes, matrículas, representantes
```

El directorio `config/` (fuera de `apps/`) contiene la configuración global de Django.

## Estructura Estándar de un Módulo

```
nombre_modulo/
├── api/
│   ├── serializers.py   # Esquemas JSON de entrada/salida
│   ├── views.py         # ViewSets (list, create, retrieve, update, destroy)
│   ├── filters.py       # Filtros personalizados (django-filter)
│   └── urls.py          # Rutas del módulo (DefaultRouter)
├── models/
│   ├── __init__.py      # Re-exporta todos los modelos
│   ├── modelo_a.py       # Entidad A
│   └── modelo_b.py       # Entidad B
├── repositories/
│   └── modulo_repo.py    # Consultas centralizadas por entidad
├── services/
│   └── modulo_service.py # Lógica de negocio y orquestación
├── tests/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_api.py
├── admin.py
├── apps.py
├── urls.py
└── README.md             # Documentación del módulo
```

## Convenciones de Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Modelos | `Camel_Case` | `StudentNote`, `AcademicPeriod` |
| Archivos de modelos | `snake_case` | `student_note.py`, `academic_period.py` |
| Métodos/variables | `snake_case` | `get_student_notes()`, `active` |
| ViewSets | `Pascal_Case` | `StudentNoteViewSet` |
| Serializers | `Pascal_Case` | `StudentNoteSerializer` |
| Permisos | `modulo.verbo_modelo` | `grading.create_note` |

## Estándares de Respuesta

Todos los endpoints usan el formato estandarizado via `StandardResponseRenderer`:

```json
{
  "ok": boolean,
  "data": object | array,
  "msg": string
}
```

La paginación incluye metadatos dentro de `data`:

```json
{
  "ok": true,
  "data": {
    "count": 100,
    "next": "url",
    "previous": "url",
    "results": [...]
  },
  "msg": ""
}
```

## Reglas de Acceso a Datos

> **IMPORTANTE**: No usar `Model.objects.query()` directamente en vistas o servicios.

```
API View → Service → Repository → Model
```

Todas las consultas ORM deben residir en la capa de repositorios.

## Authentication y Permissions

- **JWT**: Access token (15 min) + Refresh token (7 días)
- **Permisos**: Formato `modulo.accion` (ej: `grading.view_note`)
- **Decoradores**: `@require_permission("modulo.accion")` para `@api_view`
- **ViewSets**: `action_permissions` dict + `HasPermission`

## Campos de Sincronización

Modelos que soportan operación offline incluyen:

| Campo | Propósito |
|-------|-----------|
| `uuid` | Identificador único global |
| `sync_status` | Estado de sincronización |
| `synced_at` | Timestamp de última sincronización |
| `sync_version` | Control de versiones para conflictos |
| `device_origin` | Dispositivo de origen |
| `deleted_at` | Soft delete (fecha de eliminación) |

## API Documentation

- Schema OpenAPI: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`

```bash
# Validar schema
python manage.py spectacular --settings=config.settings.local --validate

# Generar archivo
python manage.py spectacular --settings=config.settings.local --file schema.yml
```