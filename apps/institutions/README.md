# Módulo Institutions

Gestión de la información institucional base: instituciones, años académicos y aulas físicas.

## Estructura de Carpetas

```
institutions/
├── models/                    # Capa de datos (3 modelos)
│   ├── __init__.py           # Re-export de modelos
│   ├── institution.py        # Modelo Institution
│   ├── school_year.py        # Modelo School_Year
│   └── classroom.py          # Modelo Classroom
│
├── repositories/             # Capa de acceso a datos (3 repos)
│   ├── __init__.py
│   └── institution_repo.py   # 3 repository classes
│
├── services/                 # Capa de lógica de negocio
│   ├── __init__.py
│   └── institution_service.py # InstitutionService con 27+ métodos
│
├── api/                      # Capa HTTP (REST)
│   ├── __init__.py
│   ├── serializers.py        # Serializadores DRF
│   ├── views.py              # ViewSets (3)
│   ├── filters.py            # Filtros
│   └── urls.py               # Router DRF
│
├── tests/                    # Tests (3 suites)
│   ├── __init__.py
│   ├── test_models.py        # Tests de modelos (15+ casos)
│   ├── test_services.py      # Tests de servicios (20+ casos)
│   └── test_api.py           # Tests HTTP (12+ casos)
│
├── admin.py                  # Panel de administración
├── apps.py                   # Configuración de app
├── urls.py                   # Rutas (includes api/urls.py)
├── README.md                 # Este archivo
└── migrations/               # Auto-generadas
```

## Arquitectura de Capas

### 1. Modelos (`models/`)

Tres modelos fundamentales con relaciones y validaciones:

#### Institution

- `name` (CharField, 255)
- `code` (CharField, 100, **unique**)
- `address` (CharField, 255)
- `city` (CharField, 100)
- `active` (BooleanField, default=True)
- `created_at`, `updated_at` (timestamps)

**Métodos:**

- `__str__()` → Retorna nombre

#### School_Year

- `institution` (FK → Institution, cascade)
- `name` (CharField, 255)
- `start_date` (DateField)
- `end_date` (DateField)
- `active` (BooleanField, default=True)
- `created_at`, `updated_at` (timestamps)

**Métodos:**

- `__str__()` → Retorna "Institución - Fecha inicio - Fecha fin"

#### Classroom

- `institution` (FK → Institution, cascade)
- `name` (CharField, 100)
- `room_type` (CharField, 50) - Ej: "Aula", "Laboratorio", "Gimnasio"
- `capacity` (IntegerField)
- `active` (BooleanField, default=True)

**Métodos:**

- `__str__()` → Retorna "Nombre (Tipo)"

### 2. Repositorios (`repositories/`)

Encapsulan todas las queries complejas. Heredan de `BaseRepository`.

#### InstitutionRepository (9 métodos)

- `get_all()` - Todas las instituciones activas
- `get_by_id(pk)` - Por ID
- `get_by_code(code)` - Por código único
- `search(query)` - Búsqueda por nombre o código
- `get_by_city(city)` - Filtra por ciudad

#### SchoolYearRepository (6 métodos)

- `get_all()` - Todos los años
- `get_by_id(pk)` - Por ID
- `get_by_institution(institution_id)` - Años de una institución
- `get_active_in_institution(institution_id)` - Solo activos
- `get_current(institution_id)` - Año actual (por fecha)

#### ClassroomRepository (7 métodos)

- `get_all()` - Todas las aulas
- `get_by_id(pk)` - Por ID
- `get_by_institution(institution_id)` - Aulas de institución
- `get_by_type(institution_id, room_type)` - Por tipo
- `get_by_capacity(institution_id, min_capacity)` - Por capacidad mínima

### 3. Servicios (`services/`)

Implementan lógica de negocio y validaciones. Clase única: `InstitutionService`.

#### InstitutionService (27+ métodos)

**Institution (7 métodos):**

- `create_institution(name, code, address, city)` - Crea con validación de código único
- `get_institution(institution_id)` - Obtiene o lanza error
- `get_all_institutions(active_only=True)` - Lista
- `get_institution_details(institution_id)` - Detalles completos con años y aulas
- `update_institution(institution_id, **kwargs)` - Actualiza con validaciones
- `deactivate_institution(institution_id)` - Soft-delete
- `search_institutions(query)` - Búsqueda por nombre/código

**School_Year (7 métodos):**

- `create_school_year(institution_id, name, start_date, end_date)` - Valida fechas y conflictos
- `get_school_year(school_year_id)` - Obtiene o lanza error
- `list_school_years(institution_id, active_only=True)` - Lista por institución
- `get_current_school_year(institution_id)` - Obtiene año actual por fecha
- `update_school_year(school_year_id, **kwargs)` - Actualiza
- `deactivate_school_year(school_year_id)` - Soft-delete

**Classroom (7+ métodos):**

- `create_classroom(institution_id, name, room_type, capacity)` - Valida capacidad > 0
- `get_classroom(classroom_id)` - Obtiene o lanza error
- `list_classrooms(institution_id, active_only=True)` - Lista por institución
- `list_classrooms_by_type(institution_id, room_type)` - Filtra por tipo
- `update_classroom(classroom_id, **kwargs)` - Actualiza
- `deactivate_classroom(classroom_id)` - Soft-delete
- `get_available_classrooms(institution_id, capacity_min=None)` - Con filtro de capacidad

### 4. API (`api/`)

Endpoints REST con validación y filtrado.

**Serializers (3):**

- `InstitutionSerializer` - id, name, code, address, city, active, timestamps
- `SchoolYearSerializer` - id, institution, name, dates, active, timestamps
- `ClassroomSerializer` - id, institution, name, room_type, capacity, active

**ViewSets (3):**

- `InstitutionViewSet` - CRUD completo
- `SchoolYearViewSet` - CRUD completo
- `ClassroomViewSet` - CRUD completo

**Filtros (3):**

- `InstitutionFilter` - Filtrar por ciudad, código
- `SchoolYearFilter` - Filtrar por institución, estado activo
- `ClassroomFilter` - Filtrar por institución, tipo, capacidad

**Rutas registradas con DRF DefaultRouter:**

```
/api/institutions/institution/           - CRUD Institution
/api/institutions/school-year/           - CRUD SchoolYear
/api/institutions/classroom/             - CRUD Classroom
```

### 5. Tests (`tests/`)

#### test_models.py (15+ casos)

- `InstitutionModelTest` - Creación, unicidad, timestamps
- `SchoolYearModelTest` - Fechas, múltiples años, relaciones
- `ClassroomModelTest` - Tipos, capacidades, múltiples

#### test_services.py (20+ casos)

- `InstitutionServiceTest` - CRUD, búsqueda, validaciones
- `SchoolYearServiceTest` - CRUD, conflictos de fechas, año actual
- `ClassroomServiceTest` - CRUD, filtros, capacidad

#### test_api.py (12+ casos)

- `InstitutionAPITest` - Endpoints HTTP
- `SchoolYearAPITest` - Endpoints HTTP
- `ClassroomAPITest` - Endpoints HTTP

## Ejemplos de Uso

### Crear una institución

```python
from apps.institutions.services.institution_service import InstitutionService

service = InstitutionService()
institution = service.create_institution(
    name='Colegio Santa María',
    code='CSM-001',
    address='Calle Principal 123',
    city='Quito'
)
```

### Crear año escolar con validación de fechas

```python
from datetime import date

school_year = InstitutionService.create_school_year(
    institution_id=1,
    name='2024-2025',
    start_date=date(2024, 9, 1),
    end_date=date(2025, 7, 31)
)
# Lanza ValueError si:
# - start_date >= end_date
# - Conflicta con otro año escolar en esa institución
```

### Obtener aulas disponibles

```python
# Todas las aulas activas
available = InstitutionService.get_available_classrooms(
    institution_id=1
)

# Aulas con capacidad >= 40 estudiantes
large_rooms = InstitutionService.get_available_classrooms(
    institution_id=1,
    capacity_min=40
)
```

### Obtener año escolar actual

```python
current = InstitutionService.get_current_school_year(institution_id=1)
# Retorna el School_Year cuya fecha actual esté entre start_date y end_date
# Lanza ValueError si no existe
```

### Buscar instituciones

```python
results = InstitutionService.search_institutions('Santo')
# Busca por nombre o código (case-insensitive)
```

## Errores Comunes

### ValueError: Conflicto de fechas

```python
# ❌ Incorrecto
InstitutionService.create_school_year(
    institution_id=1,
    name='2024-2025-2',
    start_date=date(2024, 12, 1),
    end_date=date(2025, 3, 31)  # Conflicta con 2024-2025
)
```

### ValueError: Capacidad inválida

```python
# ❌ Incorrecto
InstitutionService.create_classroom(
    institution_id=1,
    name='A01',
    room_type='Aula',
    capacity=0  # Debe ser > 0
)
```

## Notas de Implementación

1. **Soft-delete**: Los modelos usan `active=False` en lugar de eliminar datos
2. **Validaciones en Servicios**: No se confíe solo en validaciones ORM
3. **Búsquedas**: Son case-insensitive (icontains)
4. **Transacciones**: Para operaciones multi-modelo, usar `@transaction.atomic()`
5. **Relaciones**: Institution y School_Year usan `on_delete=models.CASCADE`
