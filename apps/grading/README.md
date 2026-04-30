# Módulo `grading` — Gestión de Calificaciones, Asistencia y Conducta

Este módulo implementa el patrón de arquitectura de **separación en capas** (models → repositories → services → api) para gestionar el ciclo de vida académico de los estudiantes en cuanto a sus notas, asistencia diaria e incidentes de comportamiento.

## Estructura de Carpetas

```
grading/
├── models/                    # Capa de datos (3 modelos)
│   ├── __init__.py           # Re-export de todos los modelos
│   ├── student_note.py       # Calificaciones por actividad
│   ├── attendance.py         # Registro de asistencia
│   └── conduct_incident.py   # Reportes de conducta
│
├── repositories/             # Capa de acceso a datos
│   ├── __init__.py
│   └── grading_repo.py       # Repositorios para Note, Attendance e Incident
│
├── services/                 # Capa de lógica de negocio
│   ├── __init__.py
│   └── grading_service.py    # Orquesta operaciones y cálculos (promedios, etc.)
│
├── api/                      # Capa HTTP (REST)
│   ├── __init__.py
│   ├── serializers.py        # Validadores de entrada/salida
│   ├── views.py              # Vistas generadas dinámicamente
│   └── urls.py               # Rutas estandarizadas (list, get, add, update, delete)
│
├── tests/                    # Tests
│   ├── __init__.py
│   └── ...                   # Suites de tests
│
├── admin.py                  # Panel de administración Django
├── apps.py                   # Configuración de la app
├── urls.py                   # Rutas raíz del módulo
├── README.md                 # Este archivo
└── migrations/               # Migraciones (auto-generadas)
```

## Modelos

### StudentNote

Registro de calificación para una actividad académica específica.
- `student`: FK a Student
- `academic_activity`: FK a Academic_Activity
- `note_value`: Valor numérico original
- `normalized_value`: Valor normalizado a base 10
- `sync_status`: Estado de sincronización (pending, synced)

### Attendance

Registro de asistencia diaria o por materia.
- `student`: FK a Student
- `status`: P (Presente), A (Ausente), T (Tardanza), J (Justificado)
- `date`: Fecha del registro

### ConductIncident

Reporte de incidentes de comportamiento.
- `category`: disciplina, académica, social, asistencia
- `severity`: 1 (Leve), 2 (Moderado), 3 (Grave)
- `family_notified`: Boolean

## Repositorios

Centralizan las consultas a la base de datos.
- `StudentNoteRepository`: Consultas compuestas por estudiante/actividad/periodo.
- `AttendanceRepository`: Consultas por fecha y clase.
- `ConductIncidentRepository`: Consultas filtradas por severidad y categoría.

## Servicios

### GradingService

Orquesta la lógica compleja. Por ejemplo, al crear una nota:
1. Valida los rangos permitidos.
2. Calcula el `normalized_value` automáticamente.
3. Gestiona la actualización si ya existe un registro para esa combinación única.

```python
from apps.grading.services.grading_service import GradingService

# Crear una nota
note = GradingService.create_student_note(
    student_id=1,
    academic_activity_id=5,
    academic_period_id=1,
    teacher_subject_section_id=10,
    note_value=8.5
)

# Calcular promedio
average = GradingService.calculate_period_average(student_id=1, academic_period_id=1)
```

## API REST

El módulo usa una estructura de endpoints POST estandarizada:

### Student Notes
- `POST /api/grading/student-note/list/`
- `POST /api/grading/student-note/get/`
- `POST /api/grading/student-note/add/`
- `POST /api/grading/student-note/update/`
- `POST /api/grading/student-note/delete/`

### Attendance
- `POST /api/grading/attendance/list/`
- `POST /api/grading/attendance/add/`
- ... (mismo patrón)

### Conduct Incidents
- `POST /api/grading/conduct-incident/list/`
- `POST /api/grading/conduct-incident/add/`
- ... (mismo patrón)

## Notas Importantes

1. **Normalización**: Las notas siempre se guardan con su valor original y uno normalizado a base 10 para reportes globales.
2. **Sincronización**: Los modelos incluyen campos de `sync_version` y `device_origin` para soportar la captura de datos offline desde dispositivos móviles.
3. **Validación**: `StudentNote` valida que la nota no exceda el `value_max` definido en la `Academic_Activity`.
