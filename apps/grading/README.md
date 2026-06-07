# Módulo `grading` — Registro de Desempeño Académico y Estructura Evaluativa

Este módulo se encarga del seguimiento integral del rendimiento académico de los estudiantes, gestionando la parametrización de estructuras evaluativas de varios niveles (bloques, criterios y subcriterios), el registro de calificaciones de actividades, la auditoría de cambios en notas, promedios finales y los procesos de recuperación académica.

---

## Estructura del Módulo

El módulo sigue un patrón de diseño por capas que garantiza la separación de responsabilidades:

```
grading/
├── models/             # Estructura evaluativa, calificaciones e históricos
├── repositories/       # Consultas ORM y acceso a datos centralizados
├── services/           # Lógica de cálculo de promedios, recuperación e históricos
├── api/                # ViewSets, Serializadores y Filtros REST
└── tests/              # Pruebas unitarias, integración y validación de seguridad RLS/RBAC
```

---

## Modelos de Datos

El esquema real del módulo consta de los siguientes modelos y campos (toda la información relativa a Asistencia e Incidentes de Conducta ha sido reubicada formalmente en el módulo independiente `attendance`):

### 1. `GradeType` (Tipo de Nota)

Catálogo precargado de tipos de evaluación disponibles en el sistema (ej. `NUM` para Numérica, `CUAL` para Cualitativa).

| Campo  | Tipo Django      | Descripción                       |
| :----- | :--------------- | :-------------------------------- |
| `id`   | `AutoField`      | Identificador único primario      |
| `code` | `CharField(20)`  | Código único del tipo (Ej: `NUM`) |
| `name` | `CharField(100)` | Nombre descriptivo                |

### 2. `QualitativeScale` (Escala Cualitativa)

Catálogo de escalas de valoración de competencias cualitativas y sus equivalencias numéricas correspondientes.

| Campo                 | Tipo Django      | Descripción                                                    |
| :-------------------- | :--------------- | :------------------------------------------------------------- |
| `id`                  | `AutoField`      | Identificador único primario                                   |
| `code`                | `CharField(10)`  | Código único de la escala (Ej: `DA`)                           |
| `description`         | `CharField(100)` | Descripción (Ej: `Domina el Aprendizaje`)                      |
| `numeric_equivalence` | `DecimalField`   | Valor numérico equivalente en escala de 10 puntos (Ej: `9.00`) |

### 3. `EvaluationBlock` (Macro Evaluación / Bloque)

Grupo evaluativo principal asociado a un período académico (ej. trimestres, quimestres) y un tipo de evaluación.

| Campo               | Tipo Django                   | Descripción                                                  |
| :------------------ | :---------------------------- | :----------------------------------------------------------- |
| `id`                | `AutoField`                   | Identificador único primario                                 |
| `academic_period`   | `ForeignKey(Academic_Period)` | Período académico asociado                                   |
| `name`              | `CharField(100)`              | Nombre del bloque (Ej: `Bloque 1`)                           |
| `evaluation_type`   | `CharField(30)`               | Tipo de evaluación (`FORMATIVA` o `SUMATIVA`)                |
| `weight_percentage` | `DecimalField`                | Peso porcentual del bloque sobre la nota final (Ej: `40.00`) |
| `active`            | `BooleanField`                | Indica si el bloque evaluativo está vigente                  |

### 4. `BlockComponent` (Criterio de Evaluación / Componente)

Subdivisión estructural intermedia de una macro evaluación (ej. insumos individuales, proyectos grupales).

| Campo              | Tipo Django                   | Descripción                                              |
| :----------------- | :---------------------------- | :------------------------------------------------------- |
| `id`               | `AutoField`                   | Identificador único primario                             |
| `evaluation_block` | `ForeignKey(EvaluationBlock)` | Bloque evaluativo padre                                  |
| `name`             | `CharField(100)`              | Nombre del componente (Ej: `Actividades Individuales`)   |
| `internal_weight`  | `DecimalField`                | Peso porcentual asignado dentro del bloque (Ej: `50.00`) |

### 5. `ComponentIndicator` (Subcriterio de Evaluación / Indicador)

Nivel de desagregación más granular de un componente evaluativo utilizado para evaluar indicadores específicos.

| Campo             | Tipo Django                  | Descripción                                          |
| :---------------- | :--------------------------- | :--------------------------------------------------- |
| `id`              | `AutoField`                  | Identificador único primario                         |
| `block_component` | `ForeignKey(BlockComponent)` | Componente padre                                     |
| `name`            | `CharField(100)`             | Nombre del indicador de evaluación                   |
| `internal_weight` | `DecimalField`               | Peso porcentual dentro del componente (Ej: `100.00`) |

### 6. `EvaluativeActivity` (Actividad Evaluativa)

Tareas, exámenes, talleres u otras actividades planificadas y evaluadas por el docente para un grupo de estudiantes.

| Campo                     | Tipo Django                           | Descripción                                                                 |
| :------------------------ | :------------------------------------ | :-------------------------------------------------------------------------- |
| `id`                      | `AutoField`                           | Identificador único primario                                                |
| `component_indicator`     | `ForeignKey(ComponentIndicator)`      | Indicador evaluativo asociado                                               |
| `teacher_subject_section` | `ForeignKey(Teacher_Subject_Section)` | Asignación del docente de la sección de clase                               |
| `title`                   | `CharField(200)`                      | Título de la actividad                                                      |
| `activity_type`           | `CharField(30)`                       | Categoría de actividad (`TAREA`, `LECCION`, `EXAMEN`, `PROYECTO`, `TALLER`) |
| `max_score`               | `DecimalField`                        | Puntuación máxima obtenible (Ej: `10.00`)                                   |
| `due_date`                | `DateField`                           | Fecha máxima de entrega de la actividad                                     |

### 7. `StudentNote` (Nota de Estudiante)

Calificación individual obtenida por un estudiante matriculado en una actividad evaluativa específica. Soporta control offline-first.

| Campo                 | Tipo Django                      | Descripción                                                             |
| :-------------------- | :------------------------------- | :---------------------------------------------------------------------- |
| `id`                  | `AutoField`                      | Identificador único primario                                            |
| `uuid`                | `UUIDField`                      | Identificador único universal para sincronización offline               |
| `enrollment`          | `ForeignKey(Enrollment)`         | Matrícula del estudiante asociado                                       |
| `evaluative_activity` | `ForeignKey(EvaluativeActivity)` | Actividad evaluativa calificada                                         |
| `grade_type`          | `ForeignKey(GradeType)`          | Tipo de calificación                                                    |
| `qualitative_scale`   | `ForeignKey(QualitativeScale)`   | Escala cualitativa equivalente (opcional)                               |
| `numeric_score`       | `DecimalField`                   | Nota numérica obtenida (escala de 1 a 10)                               |
| `manually_overridden` | `BooleanField`                   | Bandera de modificación manual/administrativa                           |
| `teacher_observation` | `TextField`                      | Justificaciones u observaciones hechas por el docente                   |
| `sync_status`         | `CharField(20)`                  | Estado de sincronización offline (`PENDIENTE`, `SINCRONIZADO`, `ERROR`) |
| `synced_at`           | `DateTimeField`                  | Fecha y hora de sincronización                                          |
| `sync_version`        | `PositiveIntegerField`           | Número de versión para control de conflictos offline                    |
| `device_origin`       | `CharField(40)`                  | Nombre o ID del dispositivo físico de origen                            |
| `created_at`          | `DateTimeField`                  | Fecha de creación del registro                                          |
| `updated_at`          | `DateTimeField`                  | Fecha de actualización del registro                                     |

### 8. `GradeChangeHistory` (Historial de Cambios de Nota)

Bitácora de auditoría inmutable que registra cada edición manual efectuada sobre calificaciones existentes.

| Campo              | Tipo Django               | Descripción                                            |
| :----------------- | :------------------------ | :----------------------------------------------------- |
| `id`               | `AutoField`               | Identificador único primario                           |
| `student_note`     | `ForeignKey(StudentNote)` | Nota modificada                                        |
| `modified_by_user` | `ForeignKey(User)`        | Usuario administrador o docente responsable del cambio |
| `previous_score`   | `DecimalField`            | Calificación previa antes de la edición                |
| `new_score`        | `DecimalField`            | Nueva calificación guardada                            |
| `reason`           | `TextField`               | Justificación del cambio de nota                       |
| `modified_at`      | `DateTimeField`           | Sello de tiempo de la modificación                     |

### 9. `PeriodGradeSummary` (Resumen de Calificaciones del Período)

Consolidación y promedio final calculado de las notas de un alumno para una asignatura específica en un período escolar.

| Campo                 | Tipo Django                    | Descripción                                                               |
| :-------------------- | :----------------------------- | :------------------------------------------------------------------------ |
| `id`                  | `AutoField`                    | Identificador único primario                                              |
| `enrollment`          | `ForeignKey(Enrollment)`       | Matrícula del estudiante                                                  |
| `subject_offering`    | `ForeignKey(SubjectOffering)`  | Oferta de asignatura asociada                                             |
| `academic_period`     | `ForeignKey(Academic_Period)`  | Período académico evaluado                                                |
| `formative_avg`       | `DecimalField`                 | Promedio ponderado de insumos formativos                                  |
| `summative_avg`       | `DecimalField`                 | Promedio ponderado de insumos sumativos                                   |
| `final_avg_truncated` | `DecimalField`                 | Promedio final del período redondeado/truncado                            |
| `qualitative_scale`   | `ForeignKey(QualitativeScale)` | Calificación cualitativa equivalente                                      |
| `requires_recovery`   | `BooleanField`                 | Indica si el estudiante tiene promedio insuficiente y requiere supletorio |
| `promotion_status`    | `CharField(20)`                | Estado de promoción académica (`approved`, `failed`, `recovery`)          |
| `calculated_at`       | `DateTimeField`                | Fecha y hora de cálculo del resumen                                       |

### 10. `RecoveryProcess` (Proceso de Recuperación)

Registro y seguimiento de exámenes supletorios o de mejora académica asignados a alumnos con notas insuficientes.

| Campo                    | Tipo Django                      | Descripción                                                                  |
| :----------------------- | :------------------------------- | :--------------------------------------------------------------------------- |
| `id`                     | `AutoField`                      | Identificador único primario                                                 |
| `period_grade_summary`   | `ForeignKey(PeriodGradeSummary)` | Consolidado académico asociado                                               |
| `managed_by_user`        | `ForeignKey(User)`               | Docente o directivo que gestiona el proceso                                  |
| `process_type`           | `CharField(30)`                  | Tipo de recuperación (`MEJORA_DIRECTA`, `MEJORA_CON_REFUERZO`, `SUPLETORIA`) |
| `initial_grade`          | `DecimalField`                   | Calificación inicial antes del proceso                                       |
| `reinforcement_grade`    | `DecimalField (null)`            | Calificación obtenida en el refuerzo académico                               |
| `improvement_eval_grade` | `DecimalField (null)`            | Calificación obtenida en la evaluación de recuperación                       |
| `final_calculated_grade` | `DecimalField (null)`            | Calificación definitiva después de aplicar reglas de mejora                  |
| `family_notified`        | `BooleanField`                   | Indica si se notificó el inicio del proceso a la familia                     |
| `start_date`             | `DateField`                      | Fecha de inicio formal del proceso                                           |
| `end_date`               | `DateField (null)`               | Fecha de finalización formal del proceso                                     |
| `observations`           | `TextField (null)`               | Observaciones de seguimiento docente                                         |

### 11. `DiagnosticEvaluation` (Evaluación Diagnóstica)

Seguimiento e informes diagnósticos efectuados al inicio de un período para identificar el nivel inicial de competencias socioemocionales de los alumnos.

| Campo                  | Tipo Django                   | Descripción                                                    |
| :--------------------- | :---------------------------- | :------------------------------------------------------------- |
| `id`                   | `AutoField`                   | Identificador único primario                                   |
| `enrollment`           | `ForeignKey(Enrollment)`      | Matrícula del alumno diagnosticado                             |
| `academic_period`      | `ForeignKey(Academic_Period)` | Período de evaluación                                          |
| `applied_by_user`      | `ForeignKey(User)`            | Profesional del DECE o consejero a cargo                       |
| `socioemotional_area`  | `CharField(100)`              | Dimensión socioemocional evaluada (Ej: `Habilidades Sociales`) |
| `findings_description` | `TextField`                   | Diagnóstico de hallazgos observados                            |
| `development_level`    | `CharField(50)`               | Nivel de desarrollo determinado (Ej: `Alto`, `Bajo`)           |
| `application_date`     | `DateField`                   | Fecha de aplicación de la evaluación                           |
| `recommendations`      | `TextField (null)`            | Recomendaciones de intervención y soporte                      |

### 12. `ProjectNote` (Nota de Proyecto)

Calificaciones de proyectos interdisciplinarios integrados para medir competencias transversales de los estudiantes.

| Campo                       | Tipo Django                            | Descripción                                       |
| :-------------------------- | :------------------------------------- | :------------------------------------------------ |
| `id`                        | `AutoField`                            | Identificador único primario                      |
| `uuid`                      | `UUIDField`                            | Identificador único universal                     |
| `enrollment`                | `ForeignKey(Enrollment)`               | Matrícula del estudiante                          |
| `interdisciplinary_project` | `ForeignKey(InterdisciplinaryProject)` | Proyecto interdisciplinario calificado            |
| `product_score`             | `DecimalField`                         | Nota del entregable o producto final desarrollado |
| `presentation_score`        | `DecimalField`                         | Nota de la exposición oral o defensa del proyecto |
| `final_score`               | `DecimalField`                         | Calificación definitiva del proyecto              |
| `observation`               | `TextField (null)`                     | Observaciones del jurado o docente tutor          |
| `sync_status`               | `CharField(20)`                        | Estado de sincronización                          |
| `created_at`                | `DateTimeField`                        | Fecha de creación del registro                    |

---

## Firmas de Servicios y Reglas de Negocio

La lógica centralizada para cálculos de notas y flujos evaluativos está contenida en los siguientes servicios principales:

### `EvaluationService`

- `calculate_block_grade(enrollment, block)`: Calcula el promedio formativo o sumativo del estudiante para un bloque específico integrando ponderaciones jerárquicas de componentes y actividades.
- `get_grade_hierarchy(activity)`: Obtiene toda la traza estructural de un indicador, criterio y bloque evaluativo a partir de una actividad.
- `create_grade_change_history(student_note, new_score, user, reason)`: Realiza una modificación sobre una nota existente, marcando la bandera `manually_overridden=True` e inyectando un registro inmutable en `GradeChangeHistory`.

### `GradeCalculationService`

- Cálculo automático de promedios ponderados y promedios finales truncados del período para alimentar las instancias de `PeriodGradeSummary`.

### `RecoveryProcessService`

- Lógica atómica y condicional que gestiona la aplicación de las notas de exámenes supletorios para recalcular y actualizar promedios de promoción académica según la regulación vigente.

---

## API REST Reference

Todos los endpoints interactivos emplean el formato estandarizado global `{"ok": true, "data": ..., "msg": "..."}`.

### Calificaciones de Actividades (`/api/grading/student-notes/`)

- `GET /api/grading/student-notes/`: Lista paginada y ordenada de calificaciones individuales.
- `POST /api/grading/student-notes/`: Registra una nueva calificación individual.
- `GET/PATCH/DELETE /api/grading/student-notes/{id}/`: Detalle, edición y desactivación lógica de notas.

### Jerarquía Evaluativa (Estructura de Calificaciones)

- **Bloques** (`/api/grading/evaluation-blocks/`): GET/POST/PATCH/DELETE de macro evaluaciones del período.
- **Criterios** (`/api/grading/block-components/`): GET/POST/PATCH/DELETE de componentes intermedios de evaluación.
- **Subcriterios** (`/api/grading/component-indicators/`): GET/POST/PATCH/DELETE de indicadores individuales.
- **Actividades** (`/api/grading/evaluative-activities/`): GET/POST/PATCH/DELETE de tareas y exámenes.

### Procesos de Calificaciones e Historiales

- **Auditoría Histórica** (`/api/grading/grade-history/`): GET de solo lectura para acceder a la bitácora de cambios de nota.
- **Resúmenes del Período** (`/api/grading/period-grade-summaries/`): GET/POST/PATCH/DELETE para promedios trimestres/anuales.
- **Procesos de Recuperación** (`/api/grading/recovery-processes/`): GET/POST/PATCH/DELETE de exámenes supletorios y mejoras de nota.
- **Evaluaciones Diagnósticas** (`/api/grading/diagnostic-evaluations/`): GET/POST/PATCH/DELETE de informes del DECE.
- **Notas de Proyectos** (`/api/grading/project-notes/`): GET/POST/PATCH/DELETE de notas de proyectos transversales.

### Catálogos del Módulo

- **Tipos de Nota** (`/api/grading/grade-types/`): GET de solo lectura para los tipos registrados.
- **Escalas Cualitativas** (`/api/grading/qualitative-scales/`): GET de solo lectura de escalas registradas ordenadas descendente por equivalencia.

---

## Formato de Respuestas Enriquecidas

Los serializers del módulo incluyen campos de solo lectura con los nombres relacionados a las ForeignKeys.

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

Ejemplo de respuesta en `StudentNote`:

```json
{
  "id": 1,
  "enrollment": 5,
  "enrollment_name": "Juan Pérez - 5to EGB A (Activo)",
  "evaluative_activity": 3,
  "evaluative_activity_title": "Evaluación Parcial de Matemáticas",
  "grade_type": 1,
  "grade_type_name": "Promedio",
  "qualitative_scale": 2,
  "qualitative_scale_name": "MB - Muy Buena",
  "numeric_score": 18.5
}
```

---

## Seguridad y Permisos

Todos los endpoints requieren un token JWT Bearer válido y están protegidos por el control de accesos basado en roles (RBAC) definido a nivel de cada ViewSet:

| ViewSet                       | Acciones CRUD / Custom                               | Permiso Requerido                                                                                                                              |
| :---------------------------- | :--------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| `StudentNoteViewSet`          | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_note` / `.create_note` / `.update_note` / `.delete_note`                                                                         |
| `EvaluationBlockViewSet`      | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_evaluation_macro` / `.create_evaluation_macro` / `.update_evaluation_macro` / `.delete_evaluation_macro`                         |
| `BlockComponentViewSet`       | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_evaluation_criteria` / `.create_evaluation_criteria` / `.update_evaluation_criteria` / `.delete_evaluation_criteria`             |
| `ComponentIndicatorViewSet`   | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_evaluation_subcriteria` / `.create_evaluation_subcriteria` / `.update_evaluation_subcriteria` / `.delete_evaluation_subcriteria` |
| `EvaluativeActivityViewSet`   | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_class_assignment` / `.create_class_assignment` / `.update_class_assignment` / `.delete_class_assignment`                         |
| `GradeChangeHistoryViewSet`   | `list`, `retrieve` (Solo Lectura)                    | `grading.view_grade_history`                                                                                                                   |
| `PeriodGradeSummaryViewSet`   | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_gradesummary` / `.create_gradesummary` / `.update_gradesummary` / `.delete_gradesummary`                                         |
| `RecoveryProcessViewSet`      | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_recoveryprocess` / `.create_recoveryprocess` / `.update_recoveryprocess` / `.delete_recoveryprocess`                             |
| `DiagnosticEvaluationViewSet` | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_diagnosticevaluation` / `.create_diagnosticevaluation` / `.update_diagnosticevaluation` / `.delete_diagnosticevaluation`         |
| `ProjectNoteViewSet`          | `list`, `retrieve` / `create` / `update` / `destroy` | `grading.view_projectnote` / `.create_projectnote` / `.update_projectnote` / `.delete_projectnote`                                             |
| `GradeTypeViewSet`            | `list`, `retrieve` (Solo Lectura)                    | `grading.view_grade_type`                                                                                                                      |
| `QualitativeScaleViewSet`     | `list`, `retrieve` (Solo Lectura)                    | `grading.view_qualitative_scale`                                                                                                               |

Seed de permisos en Base de Datos:

```bash
python manage.py seed_permissions --module grading
```

---

## Suite de Pruebas y Cobertura

Para verificar la integridad del código del módulo y el control de accesos RBAC sobre todos los endpoints descritos:

```bash
python manage.py test apps.grading --settings=config.settings.test
```

- **Total de Pruebas**: 40 pruebas unitarias y de integración.
- **Resultados de la Validación**: 100% de éxito (todas las pruebas pasan de forma limpia e independiente sin advertencias de paginación del ORM).
