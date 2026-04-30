# Estructura del Módulo Institutions

```
institutions/
├─ api/                          # REST API (DRF)
│  ├─ __init__.py
│  ├─ filters.py                 # Filtros (Institution, SchoolYear, Classroom)
│  ├─ serializers.py             # Validadores (3)
│  ├─ urls.py                    # Router DRF
│  └─ views.py                   # ViewSets (3)
│
├─ models/                       # Capa de datos (3 modelos)
│  ├─ __init__.py                # Re-export de modelos
│  ├─ institution.py             # Institution
│  ├─ school_year.py             # School_Year
│  └─ classroom.py               # Classroom
│
├─ repositories/                 # Capa de acceso a datos (3 repos)
│  ├─ __init__.py
│  └─ institution_repo.py        # BaseRepository + 3 clases específicas
│
├─ services/                     # Capa de lógica de negocio
│  ├─ __init__.py
│  └─ institution_service.py     # InstitutionService (27+ métodos)
│
├─ tests/                        # Tests (3 suites)
│  ├─ __init__.py
│  ├─ test_api.py                # Tests HTTP (12+ casos)
│  ├─ test_models.py             # Tests unitarios (15+ casos)
│  └─ test_services.py           # Tests lógica (20+ casos)
│
├─ __init__.py                   # Paquete Python
├─ admin.py                      # Panel Django (3 ModelAdmin)
├─ apps.py                       # Configuración de app
├─ README.md                     # Documentación principal
├─ STRUCTURE.md                  # Este archivo
├─ urls.py                       # Rutas: path('', include(api.urls))
└─ migrations/                   # (Auto-generadas)
```

## Organización por Responsabilidades

### 🗄️ Capa de Datos

- **models/** — Definiciones de tablas (Institution, SchoolYear, Classroom)
- **repositories/** — Queries complejas, acceso a BD

### 💼 Capa de Lógica

- **services/** — Orquestación de 27+ operaciones, validaciones
- **tests/** — Verificación de comportamiento

### 🌐 Capa HTTP

- **api/** — Serialización, vistas, rutas
- **admin.py** — Interfaz de administración

## ¿Dónde agregar cosas nuevas?

| Necesidad         | Carpeta         | Archivo                    |
| ----------------- | --------------- | -------------------------- |
| Nuevo modelo      | `models/`       | `nuevo_modelo.py`          |
| Query compleja    | `repositories/` | `institution_repo.py`      |
| Lógica de negocio | `services/`     | `institution_service.py`   |
| Endpoint API      | `api/`          | `views.py` (nuevo ViewSet) |
| Serializer        | `api/`          | `serializers.py`           |
| Test              | `tests/`        | `test_{tipo}.py`           |

## Niveles de Importación

### ✅ Correcto

```python
# Desde otra app
from apps.institutions.models import Institution, SchoolYear, Classroom
from apps.institutions.services.institution_service import InstitutionService
from apps.institutions.repositories.institution_repo import InstitutionRepository

# Dentro del módulo
from apps.institutions.models import Institution
from .repositories.institution_repo import InstitutionRepository
from .services.institution_service import InstitutionService
```

### ❌ Incorrecto

```python
# No importes de archivos internos
from apps.institutions.models.institution import Institution  # Usa models/__init__.py
```

## Re-exports

Las siguientes carpetas re-exportan en `__init__.py`:

- **models/** → Institution, SchoolYear, Classroom
- **repositories/** → InstitutionRepository, SchoolYearRepository, ClassroomRepository
- **services/** → InstitutionService

## Métodos del Servicio

### Institution (7)

create, get, get_all, get_details, update, deactivate, search

### SchoolYear (7)

create, get, list, get_current, update, deactivate, (+ validaciones de fechas)

### Classroom (7+)

create, get, list, list_by_type, update, deactivate, get_available

## Orden de Ejecución

Para operaciones complejas:

```python
# 1. Validar institución existe
institution = InstitutionService.get_institution(inst_id)

# 2. Crear año escolar (con validación de fechas)
school_year = InstitutionService.create_school_year(
    institution_id=inst_id,
    name='2024-2025',
    start_date=...,
    end_date=...
)

# 3. Crear aulas (con validación de capacidad)
classroom = InstitutionService.create_classroom(
    institution_id=inst_id,
    name='101',
    room_type='Aula',
    capacity=40
)
```

## Validaciones Importantes

1. **Institution.code** - Debe ser único
2. **School_Year fechas** - start_date < end_date, sin conflictos
3. **Classroom.capacity** - Debe ser > 0
4. **FK constraints** - Usar `on_delete=models.CASCADE` apropiadamente
