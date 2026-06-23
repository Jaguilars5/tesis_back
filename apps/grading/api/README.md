# API — Módulo Grading

Gestiona calificaciones, estructura evaluativa, promedios de período, procesos de recuperación y notas.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student-notes/` | GET/POST | `grading.view/create_note` |
| `student-notes/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_note` |
| `evaluation-blocks/` | GET/POST | `grading.view/create_evaluation_macro` |
| `evaluation-blocks/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_evaluation_macro` |
| `block-components/` | GET/POST | `grading.view/create_evaluation_criteria` |
| `block-components/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_evaluation_criteria` |
| `component-indicators/` | GET/POST | `grading.view/create_evaluation_subcriteria` |
| `component-indicators/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_evaluation_subcriteria` |
| `evaluative-activities/` | GET/POST | `grading.view/create_class_assignment` |
| `evaluative-activities/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_class_assignment` |
| `grade-history/` | GET | `grading.view_grade_history` |
| `period-grade-summaries/` | GET/POST | `grading.view/create_gradesummary` |
| `period-grade-summaries/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_gradesummary` |
| `recovery-processes/` | GET/POST | `grading.view/create_recoveryprocess` |
| `recovery-processes/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_recoveryprocess` |
| `grade-types/` | GET/POST | `grading.view/create_grade_type` |
| `grade-types/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_grade_type` |
| `qualitative-scales/` | GET/POST | `grading.view/create_qualitative_scale` |
| `qualitative-scales/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_qualitative_scale` |
| `activity-types/` | GET/POST | `grading.view/create_activity_type` |
| `activity-types/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_activity_type` |
| `recovery-process-types/` | GET/POST | `grading.view/create_recovery_process_type` |
| `recovery-process-types/{id}/` | GET/PUT/PATCH/DEL | `grading.view/update/delete_recovery_process_type` |

---

## Calificaciones (`/api/grading/student-notes/`)

### POST — Crear nota

```json
{
  "enrollment": 1,
  "evaluative_activity": 1,
  "grading_mode": "NUMERIC",
  "numeric_score": "8.50",
  "grade_type": 1,
  "teacher_observation": "Buen trabajo"
}
```

---

## Historial de Cambios (`/api/grading/grade-history/`)

Solo lectura.

---

## Catálogos

### GradeTypes (`/api/grading/grade-types/`)

```json
{"code": "NUM", "name": "Numérica"}
{"code": "CUAL", "name": "Cualitativa"}
```

### QualitativeScales (`/api/grading/qualitative-scales/`)

```json
{"code": "SE", "name": "Superior", "numeric_equivalence": "9.00"}
{"code": "SA", "name": "Alcanza", "numeric_equivalence": "7.00"}
{"code": "AC", "name": "Básico", "numeric_equivalence": "5.00"}
{"code": "NA", "name": "No Alcanza", "numeric_equivalence": "3.00"}
```

### RecoveryProcessTypes (`/api/grading/recovery-process-types/`)

```json
{"code": "MEJORA_DIRECTA", "name": "Mejora Directa", "allows_improvement_eval": true}
{"code": "SUPLETORIA", "name": "Supletoria", "allows_suppletorio": true}
```

---

## Notas

- No existen endpoints `evaluation-types/`, `promotion-statuses/` ni `project-notes/`. Esos son `TextChoices` internos de `EvaluationBlock` y `PeriodGradeSummary`.
- `LearningReport` y `RecoverySession` tienen serializers pero **no tienen ViewSets**.
- `GradeType` no tiene archivo de modelo (`grade_type.py`), aunque `GradeTypeRepository`, `GradeTypeViewSet` y `GradeTypeSerializer` existen — la importación fallaría en tiempo de ejecución.
