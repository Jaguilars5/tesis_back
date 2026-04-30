# Estructura del Módulo Students

```
students/
├─ api/                          # REST API (DRF) - Por completar
│  ├─ __init__.py
│  ├─ filters.py                 # Filtros
│  ├─ serializers.py             # Serializadores (3)
│  ├─ urls.py                    # Router DRF
│  └─ views.py                   # ViewSets (3)
│
├─ models/                       # Capa de datos (3 modelos)
│  ├─ __init__.py                # Re-export: Student, Representative, Student_Representative
│  ├─ student.py                 # Student
│  ├─ representative.py          # Representative
│  └─ student_representative.py  # Student_Representative (M2M explícito)
│
├─ repositories/                 # Capa de acceso a datos
│  ├─ __init__.py
│  └─ students_repo.py           # 3 Repository classes (16 métodos)
│
├─ services/                     # Capa de lógica de negocio
│  ├─ __init__.py
│  └─ students_service.py        # StudentService (30+ métodos)
│
├─ tests/                        # Tests (3 suites)
│  ├─ __init__.py
│  ├─ test_api.py                # Tests HTTP (10+ casos)
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

- **models/** — 3 modelos para estudiantes y representantes
- **repositories/** — 3 clases repository para queries complejas (16 métodos)

### 💼 Capa de Lógica

- **services/** — 30+ métodos de orquestación
  - CRUD para Student
  - CRUD para Representative
  - Gestión de relaciones Student-Representative
  - Búsquedas y filtros
  - Información de contacto completa
- **tests/** — 45+ casos de prueba

### 🌐 Capa HTTP

- **api/** — Serialización, vistas, rutas REST
- **admin.py** — Interfaz de administración

## ¿Dónde agregar cosas nuevas?

| Necesidad         | Carpeta         | Archivo                    |
| ----------------- | --------------- | -------------------------- |
| Nuevo modelo      | `models/`       | `nuevo_modelo.py`          |
| Query compleja    | `repositories/` | `students_repo.py`         |
| Lógica de negocio | `services/`     | `students_service.py`      |
| Endpoint API      | `api/`          | `views.py` (nuevo ViewSet) |
| Serializer        | `api/`          | `serializers.py`           |
| Test              | `tests/`        | `test_{tipo}.py`           |

## Niveles de Importación

### ✅ Correcto

```python
# Desde otra app
from apps.students.models import Student, Representative, Student_Representative
from apps.students.services.students_service import StudentService
from apps.students.repositories.students_repo import StudentRepository

# Dentro del módulo
from apps.students.models import Student
from .repositories.students_repo import StudentRepository
from .services.students_service import StudentService
```

### ❌ Incorrecto

```python
# No importes directo de archivos internos
from apps.students.models.student import Student  # Usa models/__init__.py
```

## Métodos del Servicio (Resumen)

### Student (10)

create, get, get_by_dni, get_all, list_by_section, get_details,
update, deactivate, search, count_by_section

### Representative (8)

create, get, get_by_dni, get_all, get_details, update, deactivate, search

### Student_Representative (13+)

assign, get_student_representatives, get_primary, set_primary,
update_authorization, remove, get_representative_students,
get_contact_info

## Relaciones Principales

```
Section (academic)
  └── Student (1-N) ✓
       └── Student_Representative (1-N) ✓
            └── Representative (1-N) ✓
```

## Validaciones Críticas

1. **Student.dni** - unique, máx 13 caracteres
2. **Student.birth_date** - edad calculada 5-30 años
3. **Representative.dni** - unique, máx 13 caracteres
4. **Student_Representative.kinship** - valores válidos
5. **Student_Representative** - unique('student', 'representative')
6. **Primer representante** - automáticamente primario
7. **Eliminar representante** - no permite si es único

## Características Especiales

### Información de Contacto

Método `get_contact_info_for_student()` retorna:

- Todos los contactos ordenados por is_primary
- Filtrados por activos
- Con todas las autorizaciones

### Autorizaciones Flexibles

Cada representante puede tener:

- `can_pickup` - Permiso para recoger
- `receives_notifications` - Recibe comunicaciones
- `emergency_contact` - Contacto de emergencia

### Principal Automático

Primer representante asignado automáticamente = principal
Cambiar principal: `set_primary_representative()`

## Flujo de Creación

```
1. create_student()              ← Matrícula en sección
2. create_representative()       ← Crear contacto (padre/madre/etc)
3. assign_representative()       ← Vincular (múltiples permitidos)
4. update_representative_authorization() ← Ajustar permisos si es necesario
5. get_contact_info_for_student() ← Usar para contactos
```

## Sincronización

Para dispositivos móviles:

- `device_origin`: Qué dispositivo registró
- `sync_version`: Versión para conflictos
- Permitir replicación sin duplicados
