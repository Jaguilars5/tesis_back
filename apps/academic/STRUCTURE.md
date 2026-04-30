# Estructura del Módulo Academic

```
academic/
├─ api/                          # REST API (DRF)
│  ├─ __init__.py
│  ├─ filters.py                 # Filtros de búsqueda
│  ├─ serializers.py             # Serializadores (8+)
│  ├─ urls.py                    # Router DRF
│  └─ views.py                   # ViewSets (8+)
│
├─ models/                       # Capa de datos (8 modelos)
│  ├─ __init__.py                # Re-export de modelos
│  ├─ academic_activity.py       # Academic_Activity
│  ├─ academic_period.py         # Academic_Period
│  ├─ config_academic.py         # Config_Academic
│  ├─ section.py                 # Section
│  ├─ student_note.py            # Student_Note
│  ├─ subject.py                 # Subject
│  ├─ teacher_subject_section.py # Teacher_Subject_Section
│  └─ timing_regime.py           # Timing_Regime
│
├─ repositories/                 # Capa de acceso a datos
│  ├─ __init__.py
│  └─ academic_repo.py           # 8 Repository classes
│
├─ services/                     # Capa de lógica de negocio
│  ├─ __init__.py
│  └─ academic_service.py        # AcademicService (40+ métodos)
│
├─ tests/                        # Tests (3 suites)
│  ├─ __init__.py
│  ├─ test_api.py                # Tests HTTP (10+ casos)
│  ├─ test_models.py             # Tests unitarios (10+ casos)
│  └─ test_services.py           # Tests lógica (15+ casos)
│
├─ __init__.py                   # Paquete Python
├─ admin.py                      # Panel Django
├─ apps.py                       # Configuración de app
├─ README.md                     # Documentación principal
├─ STRUCTURE.md                  # Este archivo
├─ urls.py                       # Rutas: path('', include(api.urls))
└─ migrations/                   # (Auto-generadas)
```

## Organización por Responsabilidades

### 🗄️ Capa de Datos

- **models/** — 8 modelos para infraestructura académica completa
- **repositories/** — 8 clases repository para queries complejas

### 💼 Capa de Lógica

- **services/** — 40+ métodos de orquestación y validaciones
  - Cálculo de promedios ponderados
  - Normalización de notas
  - Control de sincronización
  - Validaciones de límites y rangos
- **tests/** — 35+ casos de prueba

### 🌐 Capa HTTP

- **api/** — Serialización, vistas, rutas REST
- **admin.py** — Interfaz de administración

## ¿Dónde agregar cosas nuevas?

| Necesidad         | Carpeta         | Archivo                    |
| ----------------- | --------------- | -------------------------- |
| Nuevo modelo      | `models/`       | `nuevo_modelo.py`          |
| Query compleja    | `repositories/` | `academic_repo.py`         |
| Lógica de negocio | `services/`     | `academic_service.py`      |
| Endpoint API      | `api/`          | `views.py` (nuevo ViewSet) |
| Serializer        | `api/`          | `serializers.py`           |
| Test              | `tests/`        | `test_{tipo}.py`           |

## Niveles de Importación

### ✅ Correcto

```python
# Desde otra app
from apps.academic.models import Section, Subject, StudentNote
from apps.academic.services.academic_service import AcademicService
from apps.academic.repositories.academic_repo import SectionRepository

# Dentro del módulo
from apps.academic.models import Section
from .repositories.academic_repo import SectionRepository
from .services.academic_service import AcademicService
```

### ❌ Incorrecto

```python
# No importes directo de archivos internos
from apps.academic.models.section import Section  # Usa models/__init__.py
```

## Métodos del Servicio (Resumen)

### Config_Academic (4)

create, get, list, update

### Timing_Regime (4)

create, get, list, update

### Section (6)

create, get, get_all, get_details, list_by_school_year, update

### Subject (6)

create, get, get_all, get_details, list_by_section, update

### Academic_Period (4)

create, get, list_by_config, update

### Academic_Activity (5)

create, get, list_by_subject, update (+ validaciones peso, value_max)

### Teacher_Subject_Section (4)

assign, get, list (+ filtros), remove

### Student_Note (8+)

record, get, list (+ filtros), calculate_period_average,
calculate_section_average, mark_synced, deactivate

## Cálculos Clave

### Normalización

```
nota_normalizada = (nota_valor / valor_maximo) × 10
```

### Promedio Ponderado

```
promedio = Σ(nota_normalizada × peso_actividad)
```

### Sincronización

```
Status: pending → synced
Version: se incrementa en cada cambio
Timestamp: registra timestamp en segundos
```

## Relaciones Principales

```
School_Year
  ├── Config_Academic (1-N)
  ├── Timing_Regime (1-N)
  └── Section (1-N)
       ├── Subject (1-N)
       │    └── Academic_Activity (1-N)
       └── Teacher_Subject_Section (1-N)
            └── Student_Note (1-N)

Academic_Period (de Config_Academic)
Student_Note (registra en Academic_Period)
```

## Validaciones Críticas

1. **Section.capacity > 0**
2. **Academic_Activity.value_max > 0**
3. **Academic_Activity.weight ∈ [0, 1]**
4. **Student_Note.note_value ∈ [0, value_max]**
5. **Teacher_Subject_Section** = unique('user', 'subject', 'section', 'school_year')
6. **Section** = unique('school_year', 'level', 'grade', 'parallel')

## Flujo de Creación Típico

```
1. create_config_academic()      ← Configuración del año
2. create_timing_regime()        ← Jornadas horarias
3. create_section()              ← Grados/paralelos
4. create_subject()              ← Asignaturas
5. create_academic_activity()    ← Evaluaciones
6. assign_teacher()              ← Docentes
7. record_student_note()         ← Calificaciones
8. calculate_period_average()    ← Resultados
```
