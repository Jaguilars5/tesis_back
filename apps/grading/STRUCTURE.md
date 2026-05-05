# Estructura Técnica: Módulo `grading`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo de calificaciones y conducta.

## Árbol de Directorios

```text
grading/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Notas, Asistencia y Conducta
│   ├── views.py          # Generador de vistas CRUD dinámicas
│   └── urls.py           # Rutas por acción (list, get, add, etc.)
├── models/               # Capa de Datos (Entidades)
│   ├── student_note.py   # Gestión de calificaciones
│   ├── attendance.py     # Gestión de asistencia
│   └── conduct_incident.py # Gestión de comportamiento
├── repositories/         # Capa de Persistencia (Queries)
│   ├── __init__.py       # Exportación de repositorios
│   └── (clases internas) # Queries optimizadas y filtros
├── services/             # Capa de Negocio (Orquestación)
│   └── grading_service.py # Lógica de cálculos y normalización
└── tests/                # Suites de Pruebas
    └── (test suites)     # Validación de promedios y lógica
```

## Flujo de Trabajo Recomendado

Para mantener el desacoplamiento, siga este flujo de llamadas:
`API View` → `Service` → `Repository` → `Model`

> [!IMPORTANT]
> **Nunca** inserte registros de notas directamente usando el modelo. Debe utilizar siempre `GradingService.create_student_note` para asegurar que el proceso de normalización a base 10 y el marcado de `sync_status` se ejecuten correctamente.

## Guía de Importación

Utilice los puntos de entrada definidos para evitar dependencias circulares:

### ✅ Prácticas Correctas
```python
# Importar servicios
from apps.grading.services.grading_service import GradingService

# Importar modelos (re-exportados en models/__init__.py)
from apps.grading.models import StudentNote, Attendance

# Importar repositorios
from apps.grading.repositories import StudentNoteRepository
```

### ❌ Prácticas a Evitar
```python
# Importar desde archivos internos específicos
from apps.grading.models.student_note import StudentNote 

# Realizar cálculos de promedios en la vista
avg = sum(n.value for n in notes) / len(notes) # Usar GradingService
```

## Consultas para Analytics

`grading` expone consultas especializadas para que `analytics` pueda construir
snapshots de riesgo academico sin romper la separacion por capas.

Metodos disponibles:

- `StudentNoteRepository.list_for_risk_snapshot`: retorna notas activas del
  estudiante y periodo con actividad academica y materia precargadas.
- `AttendanceRepository.list_for_risk_snapshot`: retorna asistencias del
  estudiante y periodo ordenadas por fecha.
- `ConductIncidentRepository.list_for_risk_snapshot`: retorna incidentes del
  estudiante y periodo ordenados del mas reciente al mas antiguo.

Estas consultas son usadas por `AcademicRiskFeatureBuilder` para calcular
conducta, asistencia y calificaciones del semaforo de riesgo.

## Responsabilidades de Capas

1.  **Models**: Definen la estructura de los datos del desempeño estudiantil.
2.  **Repositories**: Centralizan las consultas complejas y el filtrado por períodos o secciones.
3.  **Services**: Implementan la lógica crítica (normalización de notas, promedios de período, validación de estados de asistencia).
4.  **API**: Exponen las acciones CRUD mediante un generador dinámico que estandariza las respuestas del sistema.
