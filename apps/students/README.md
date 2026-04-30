# Módulo Students

Gestión de estudiantes, representantes y sus relaciones. Registro de matrícula y contactos de emergencia.

## Estructura de Carpetas

```
students/
├── models/                    # Capa de datos (3 modelos)
│   ├── __init__.py           # Re-export de modelos
│   ├── student.py            # Modelo Student
│   ├── representative.py     # Modelo Representative
│   └── student_representative.py  # Tabla de unión
│
├── repositories/             # Capa de acceso a datos (3 repos)
│   ├── __init__.py
│   └── students_repo.py      # 3 repository classes
│
├── services/                 # Capa de lógica de negocio
│   ├── __init__.py
│   └── students_service.py   # StudentService (30+ métodos)
│
├── api/                      # Capa HTTP (REST) - Por crear
│   ├── __init__.py
│   ├── serializers.py        # Serializadores DRF
│   ├── views.py              # ViewSets
│   ├── filters.py            # Filtros
│   └── urls.py               # Router DRF
│
├── tests/                    # Tests (3 suites)
│   ├── __init__.py
│   ├── test_models.py        # Tests de modelos (15+ casos)
│   ├── test_services.py      # Tests de servicios (20+ casos)
│   └── test_api.py           # Tests HTTP (10+ casos)
│
├── admin.py                  # Panel de administración
├── apps.py                   # Configuración de app
├── urls.py                   # Rutas (includes api/urls.py)
├── README.md                 # Este archivo
└── migrations/               # Auto-generadas
```

## Arquitectura de Capas

### 1. Modelos (`models/`)

Tres modelos relacionados para gestionar estudiantes y sus representantes.

#### Student

- `dni` (CharField, 13, **unique**)
- `names` (CharField, 100)
- `last_names` (CharField, 100)
- `birth_date` (DateField)
- `section` (FK → Section, relacionada a academic)
- `enrollment_number` (CharField, 50, unique, nullable)
- `enrollment_date` (DateField, auto_now_add)
- `active` (BooleanField, default=True)
- `uuid` (UUIDField, auto-generated)
- `sync_status` (CharField: 'pending', 'synced', 'error')
- `synced_at` (DateTimeField, nullable)
- `deleted_at` (DateTimeField, nullable)
- `sync_version` (PositiveIntegerField, default=0)
- `device_origin` (CharField, 40, nullable)
- timestamps (created_at, updated_at)

**Métodos:**

- `__str__()` → "nombres apellidos"
- `get_full_name()` → Nombre completo
- `get_age()` → Calcula edad desde birth_date

#### Representative

- `dni` (CharField, 13, **unique**)
- `names` (CharField, 100)
- `last_names` (CharField, 100)
- `phone` (CharField, 15)
- `email` (CharField, 150, nullable)
- `address` (CharField, 255, nullable)
- `active` (BooleanField, default=True)
- timestamps

**Métodos:**

- `__str__()` → "nombres apellidos (parentesco)"
- `get_full_name()` → Nombre completo

#### Student_Representative

- `student` (FK → Student, cascade)
- `representative` (FK → Representative, cascade)
- `kinship` (CharField, 30) - Choices: "Padre", "Madre", "Abuelo/a", "Tío/a", "Hermano/a Mayor", "Otro"
- `is_primary` (BooleanField, default=False) - Principal contacto
- `can_pickup` (BooleanField, default=True) - Puede recoger
- `emergency_contact` (BooleanField, default=False) - Contacto de emergencia
- `receives_notifications` (BooleanField, default=True) - Recibe comunicaciones
- **unique_together** = ('student', 'representative')
- timestamps

### 2. Repositorios (`repositories/`)

Encapsulan todas las queries complejas.

#### StudentRepository (6 métodos)

- `get_all()` - Todos los estudiantes activos
- `get_by_id(pk)` - Por ID
- `get_by_dni(dni)` - Por DNI
- `get_by_section(section_id)` - Estudiantes de una sección
- `get_by_enrollment_number(enrollment_number)` - Por matrícula
- `search(query)` - Búsqueda: nombre, DNI, matrícula

#### RepresentativeRepository (6 métodos)

- `get_all()` - Todos los representantes activos
- `get_by_id(pk)` - Por ID
- `get_by_dni(dni)` - Por DNI
- `get_by_student(student_id)` - Todos los representantes de un estudiante
- `get_primary_representative(student_id)` - Representante principal
- `search(query)` - Búsqueda: nombre o DNI

#### StudentRepresentativeRepository (4 métodos)

- `get_by_id(pk)` - Obtener relación por ID
- `get_by_student(student_id)` - Todas las relaciones de un estudiante
- `get_by_representative(representative_id)` - Todos los estudiantes de un representante
- `get_relationship(student_id, representative_id)` - Relación específica

### 3. Servicios (`services/`)

`StudentService` con 30+ métodos divididos en 3 grupos.

#### Student (9 métodos)

- `create_student(dni, names, last_names, birth_date, section_id, enrollment_number=None, device_origin=None)`
  - Valida DNI único y edad (5-30 años)
- `get_student(student_id)` - Obtiene o lanza error
- `get_student_by_dni(dni)` - Por DNI
- `get_all_students(active_only=True)` - Listado
- `list_students_by_section(section_id)` - Por sección
- `get_student_details(student_id)` - Detalles completos (representantes, edad, etc.)
- `update_student(student_id, **kwargs)` - Actualiza
- `deactivate_student(student_id)` - Soft-delete
- `search_students(query)` - Búsqueda
- `count_students_by_section(section_id)` - Contar estudiantes

#### Representative (8 métodos)

- `create_representative(dni, names, last_names, phone, email=None, address=None)`
- `get_representative(representative_id)`
- `get_representative_by_dni(dni)`
- `get_all_representatives(active_only=True)`
- `get_representative_details(representative_id)` - Detalles con estudiantes
- `update_representative(representative_id, **kwargs)`
- `deactivate_representative(representative_id)`
- `search_representatives(query)`

#### Student_Representative (13+ métodos)

- `assign_representative(student_id, representative_id, kinship="Padre", is_primary=False, can_pickup=True, emergency_contact=False, receives_notifications=True)`
  - Valida que no sea duplicado
  - Primer representante automáticamente primario
- `get_student_representatives(student_id)` - Todos los representantes
- `get_primary_representative(student_id)` - Representante principal
- `set_primary_representative(student_id, representative_id)` - Cambiar principal
- `update_representative_authorization(student_id, representative_id, **kwargs)` - Campos: `kinship`, `can_pickup`, `emergency_contact`, `receives_notifications`, `is_primary`
- `remove_representative(student_id, representative_id)` - Desasignar
  - Valida que no sea el único
- `get_representative_students(representative_id)` - Estudiantes del representante
- `get_contact_info_for_student(student_id)` - Info completa de contactos

### 4. API (`api/`)

Endpoints REST con validación y filtrado (por crear/completar).

**ViewSets esperados:**

- `StudentViewSet` - CRUD + filtros
- `RepresentativeViewSet` - CRUD + filtros
- `StudentRepresentativeViewSet` - Gestión de relaciones

**Rutas:**

```
/api/students/student/              - Estudiantes
/api/students/representative/       - Representantes
/api/students/student-representative/  - Relaciones
```

### 5. Tests (`tests/`)

#### test_models.py (15+ casos)

- StudentModelTest: Creación, DNI único, edad, full_name
- RepresentativeModelTest: Creación, DNI único, opciones parentesco
- StudentRepresentativeModelTest: Creación, unique_together, múltiples

#### test_services.py (20+ casos)

- StudentServiceTest: CRUD, búsqueda, filtros, deactivate
- RepresentativeServiceTest: CRUD, búsqueda, deactivate
- StudentRepresentativeServiceTest: Asignación, principal, autorizaciones, contactos

#### test_api.py (10+ casos)

- StudentAPITest: Endpoints CRUD
- RepresentativeAPITest: Endpoints CRUD

## Ejemplos de Uso

### Crear estudiante

```python
from apps.students.services.students_service import StudentService
from datetime import date

student = StudentService.create_student(
    dni='1234567890',
    names='Juan',
    last_names='Pérez García',
    birth_date=date(2012, 5, 15),
    section_id=1,
    enrollment_number='MAT-2024-001'
)
```

### Crear representante y asignarlo

```python
# Crear representante
representative = StudentService.create_representative(
    dni='9876543210',
    names='María',
    last_names='Pérez García',
    phone='0987654321',
    email='maria@example.com'
)

# Asignar al estudiante con su parentesco y permisos
StudentService.assign_representative(
    student_id=student.id,
    representative_id=representative.id,
    kinship='Madre',
    is_primary=True,
    can_pickup=True,
    receives_notifications=True
)
```

### Obtener información de contacto

```python
contact_info = StudentService.get_contact_info_for_student(student_id=1)

# Retorna:
# {
#   'student': Student,
#   'contacts': [
#       {
#           'representative': Representative,
#           'kinship': 'Madre',
#           'phone': '0987654321',
#           'email': 'maria@example.com',
#           'is_primary': True,
#           'can_pickup': True,
#           'receives_notifications': True,
#           'emergency_contact': False,
#       },
#       ...
#   ],
#   'primary_contact': {...}
# }
```

### Cambiar representante principal

```python
StudentService.set_primary_representative(
    student_id=student.id,
    representative_id=new_rep_id
)
```

### Listar estudiantes de una sección

```python
students = StudentService.list_students_by_section(section_id=1)

# O con búsqueda
results = StudentService.search_students('Pérez')
```

### Actualizar autorizaciones

```python
StudentService.update_representative_authorization(
    student_id=1,
    representative_id=5,
    can_pickup=False,
    receives_notifications=True
)
```

## Validaciones Importantes

1. **Student.dni** - Único, máx 13 caracteres
2. **Student.birth_date** - Edad calculada debe estar entre 5 y 30 años
3. **Representative.dni** - Único, máx 13 caracteres
4. **Student_Representative.kinship** - Debe ser una opción válida (se movió desde Representative)
5. **Student_Representative** - unique_together('student', 'representative')
6. **Primer representante** - Automáticamente se marca como principal
7. **Eliminar representante** - No se permite si es el único

## Sincronización

Los estudiantes tienen control de sincronización:

- `device_origin`: Dispositivo que registró el estudiante
- `sync_version`: Versión para detectar conflictos

## Flujo Típico

```
1. create_student()              ← Registro de estudiante
2. create_representative()       ← Crear representante (padre, madre, etc.)
3. assign_representative()       ← Vincular representante
4. get_contact_info_for_student() ← Obtener datos de contacto
```

## Casos de Uso Frecuentes

### Estudiante con dos representantes

```python
# Padre principal
StudentService.assign_representative(
    student_id=1,
    representative_id=1,
    is_primary=True
)

# Madre secundaria
StudentService.assign_representative(
    student_id=1,
    representative_id=2,
    is_primary=False
)
```

### Abuelo no autorizado para recoger

```python
StudentService.assign_representative(
    student_id=1,
    representative_id=3,
    kinship='Abuelo/a',
    is_primary=False,
    can_pickup=False,
    receives_notifications=True,
    emergency_contact=True
)
```

### Cambiar sección de estudiante

```python
StudentService.update_student(
    student_id=1,
    section_id=2  # Nueva sección
)
```
