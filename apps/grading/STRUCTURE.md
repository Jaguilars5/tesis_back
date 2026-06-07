# Estructura Técnica: Módulo `grading`

Este documento detalla la organización interna y las responsabilidades de cada componente dentro del módulo de calificaciones y conducta.

## API — Serializers

Los serializers del módulo exponen campos descriptivos adicionales para las ForeignKeys:

| Serializer                       | Campos enriquecidos                                                                          |
| -------------------------------- | -------------------------------------------------------------------------------------------- |
| `StudentNoteSerializer`          | `enrollment_name`, `evaluative_activity_title`, `grade_type_name`, `qualitative_scale_name`  |
| `EvaluationBlockSerializer`      | `academic_period_name`                                                                       |
| `BlockComponentSerializer`       | `evaluation_block_name`                                                                      |
| `ComponentIndicatorSerializer`   | `block_component_name`                                                                       |
| `EvaluativeActivitySerializer`   | `component_indicator_name`, `teacher_subject_section_name`                                   |
| `GradeChangeHistorySerializer`   | `student_note_name`, `modified_by_user_name`                                                 |
| `PeriodGradeSummarySerializer`   | `enrollment_name`, `subject_offering_name`, `academic_period_name`, `qualitative_scale_name` |
| `DiagnosticEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `applied_by_user_name`                            |
| `RecoveryProcessSerializer`      | `period_grade_summary_name`, `managed_by_user_name`                                          |
| `ProjectNoteSerializer`          | `enrollment_name`, `interdisciplinary_project_title`                                         |

## Árbol de Directorios

```text
grading/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Notas, Tipos de Calificación, Bloques
│   ├── views.py          # ViewSets (StudentNote, GradeType, EvaluationBlock, etc.)
│   └── urls.py           # Rutas vía DefaultRouter
├── models/               # Capa de Datos (Entidades)
│   ├── student_note.py         # Gestión de calificaciones
│   ├── grade_type.py           # Tipos de calificación
│   ├── qualitative_scale.py    # Escalas cualitativas
│   ├── evaluation_block.py     # Bloques de evaluación
│   ├── block_component.py      # Componentes de bloque
│   ├── component_indicator.py  # Indicadores de componente
│   ├── evaluative_activity.py  # Actividades evaluativas
│   ├── grade_change_history.py # Historial de cambios de nota
│   ├── period_grade_summary.py # Resumen de notas por período
│   ├── recovery_process.py     # Procesos de recuperación
│   ├── diagnostic_evaluation.py # Evaluaciones diagnósticas
│   └── project_note.py         # Notas de proyectos
├── repositories/         # Capa de Persistencia (Queries)
│   ├── __init__.py
│   ├── grading_repo.py               # Repositorio principal de calificaciones
│   ├── evaluation_repo.py            # Repositorio de evaluación
│   ├── period_grade_summary_repository.py
│   └── recovery_process_repository.py
├── services/             # Capa de Negocio (Orquestación)
│   ├── grading_service.py          # Lógica de calificaciones
│   ├── evaluation_service.py       # Servicio de evaluación
│   ├── grade_calculation_service.py # Cálculos de notas
│   ├── behavior_evaluation_service.py # Evaluación de conducta
│   └── recovery_process_service.py  # Procesos de recuperación
└── tests/                # Suites de Pruebas
    ├── test_models.py
    ├── test_services.py
    ├── test_api.py
    ├── test_evaluation.py
    ├── test_viewsets.py
    └── test_api_gaps.py
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
from apps.grading.models import StudentNote, GradeType, EvaluationBlock

# Importar repositorios
from apps.grading.repositories.grading_repo import StudentNoteRepository
```

### ❌ Prácticas a Evitar

```python
# Importar desde archivos internos específicos
from apps.grading.models.student_note import StudentNote

# Realizar cálculos de promedios en la vista
avg = sum(n.value for n in notes) / len(notes) # Usar GradingService
```

## Responsabilidades de Capas

1.  **Models**: Definen la estructura de los datos del desempeño estudiantil.
2.  **Repositories**: Centralizan las consultas complejas y el filtrado por períodos o secciones.
3.  **Services**: Implementan la lógica crítica (normalización de notas, promedios de período, validación).
4.  **API**: Exponen las acciones CRUD mediante ViewSets que estandarizan las respuestas del sistema.
