# Módulo `scheduling` — Gestión de Horarios Escolares

Este módulo gestiona la infraestructura de tiempos de la institución, incluyendo la configuración de jornadas, la creación de franjas horarias (slots), la disponibilidad de los docentes y la asignación final de clases.

## Estructura de Carpetas

```
scheduling/
├── models/                    # Capa de datos (5 modelos)
│   ├── __init__.py           
│   ├── schedule_template_config.py # Configuración de jornada
│   ├── time_slot.py           # Franjas horarias
│   ├── teacher_availability.py # Disponibilidad docente
│   ├── subject_constraint.py   # Restricciones de materia
│   └── schedule_slot.py       # Asignación de horario
│
├── repositories/             # Capa de acceso a datos
│   ├── __init__.py
│   └── scheduling_repo.py    # Queries de horarios y disponibilidad
│
├── services/                 # Capa de lógica de negocio
│   ├── __init__.py
│   └── scheduling_service.py # Validación de conflictos y asignaciones
│
├── api/                      # Capa HTTP (REST)
│   ├── __init__.py
│   ├── serializers.py        # Serialización de datos
│   ├── views.py              # Operaciones CRUD
│   └── urls.py               # Rutas de la API
│
├── admin.py                  # Panel administrativo
├── apps.py                   # Configuración del módulo
├── urls.py                   # Rutas del módulo
├── README.md                 # Este archivo
└── migrations/               # Migraciones
```

## Modelos Principales

### ScheduleTemplateConfig
Define los parámetros globales de una jornada (Matutina/Vespertina), como duración de clases y recreos.

### TimeSlot
Representa cada periodo individual en la semana escolar.

### ScheduleSlot
Es la pieza central del horario, vinculando un docente/materia/sección con un aula y una franja horaria.

## Lógica de Validación

El `SchedulingService` garantiza que:
1. Un docente no tenga dos clases al mismo tiempo.
2. Un aula no esté ocupada por dos secciones simultáneamente.
3. Se respete la disponibilidad declarada por el docente.

## API REST

El módulo sigue el estándar del proyecto con rutas basadas en POST para todas las operaciones CRUD:

- `/api/scheduling/schedule-slot/list/`
- `/api/scheduling/time-slot/add/`
- `/api/scheduling/teacher-availability/update/`
- ... (etc)

## Ejemplos de Uso

```python
from apps.scheduling.services import SchedulingService

# Asignar una clase validando conflictos
try:
    slot = SchedulingService.assign_slot(
        teacher_subject_section_id=10,
        school_year_id=1,
        time_slot_id=5,
        classroom_id=2
    )
except ValueError as e:
    print(f"Error: {e}")
```
