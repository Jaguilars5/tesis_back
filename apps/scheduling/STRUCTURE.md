# Estructura Técnica: Módulo `scheduling`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo de gestión de horarios.

## Árbol de Directorios

```text
scheduling/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Horarios y Disponibilidad
│   ├── views.py          # Generador de vistas CRUD dinámicas
│   └── urls.py           # Rutas por acción (list, get, add, etc.)
├── models/               # Capa de Datos (Entidades)
│   ├── schedule_slot.py  # Asignaciones finales
│   ├── time_slot.py      # Definición de horas
│   └── teacher_availability.py # Horas de trabajo docente
├── repositories/         # Capa de Persistencia (Queries)
│   ├── __init__.py       # Exportación de repositorios
│   └── (clases internas) # Lógica de detección de conflictos
├── services/             # Capa de Negocio (Orquestación)
│   └── scheduling_service.py # Orquestación de asignaciones
└── tests/                # Suites de Pruebas
    └── (test suites)     # Validación de conflictos y choques
```

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** cree un `ScheduleSlot` sin pasar por el servicio. `SchedulingService.assign_slot` es el único punto encargado de verificar simultáneamente la disponibilidad del docente, el aula y la materia para evitar solapamientos.

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.scheduling.services.scheduling_service import SchedulingService

# Importar modelos (re-exportados en models/__init__.py)
from apps.scheduling.models import ScheduleSlot, TimeSlot

# Importar repositorios
from apps.scheduling.repositories import ScheduleSlotRepository
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos
from apps.scheduling.models.schedule_slot import ScheduleSlot 
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura de los horarios y las franjas temporales.
2.  **Repositories**: Implementan la lógica de búsqueda de conflictos (clashes) mediante queries SQL/ORM complejas.
3.  **Services**: Orquestan el proceso de asignación, manejando transacciones atómicas para asegurar que no se creen slots inválidos.
4.  **API**: Exponen las acciones CRUD mediante el generador dinámico estandarizado.
