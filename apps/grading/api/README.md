# API - Módulo Grading

Esta API gestiona calificaciones, estructura evaluativa (bloques → componentes → indicadores → actividades), promedios de período, procesos de recuperación, informes de aprendizaje y notas de proyectos.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student-notes/` | GET/POST | `grading.view/create_note` |
| `student-notes/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_note` |
| `evaluation-blocks/` | GET/POST | `grading.view/create_evaluation_macro` |
| `evaluation-blocks/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_evaluation_macro` |
| `block-components/` | GET/POST | `grading.view/create_evaluation_criteria` |
| `block-components/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_evaluation_criteria` |
| `component-indicators/` | GET/POST | `grading.view/create_evaluation_subcriteria` |
| `component-indicators/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_evaluation_subcriteria` |
| `evaluative-activities/` | GET/POST | `grading.view/create_class_assignment` |
| `evaluative-activities/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_class_assignment` |
| `grade-history/` | GET | `grading.view_grade_history` |
| `period-grade-summaries/` | GET/POST | `grading.view/create_gradesummary` |
| `period-grade-summaries/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_gradesummary` |
| `recovery-processes/` | GET/POST | `grading.view/create_recoveryprocess` |
| `recovery-processes/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_recoveryprocess` |
| `project-notes/` | GET/POST | `grading.view/create_projectnote` |
| `project-notes/{id}/` | GET/PATCH/DEL | `grading.view/update/delete_projectnote` |
| `grade-types/` | GET/POST | `grading.view/create_grade_type` |
| `qualitative-scales/` | GET/POST | `grading.view/create_qualitative_scale` |
| `evaluation-types/` | GET/POST | `grading.view/create_evaluation_type` |
| `activity-types/` | GET/POST | `grading.view/create_activity_type` |
| `promotion-statuses/` | GET/POST | `grading.view/create_promotion_status` |
| `recovery-process-types/` | GET/POST | `grading.view/create_recovery_process_type` |

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

**Response (201 Created):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "enrollment": 1,
    "enrollment_name": "Juan Perez - 7mo A (Activa)",
    "evaluative_activity": 1,
    "evaluative_activity_title": "Examen Parcial",
    "grading_mode": "NUMERIC",
    "numeric_score": "8.50",
    "grade_type": 1,
    "grade_type_name": "Numérica",
    "qualitative_scale": null,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "sync_status": "PENDING",
    "sync_version": 1
  },
  "msg": ""
}
```

### GET — Listar con filtros

**Filtros:** `?enrollment=1`, `?evaluative_activity=1`

---

## Bloques de Evaluación (`/api/grading/evaluation-blocks/`)

### POST — Crear

```json
{
  "academic_period": 1,
  "subject_offering": 1,
  "name": "Bloque 1 - Quimestre 1",
  "evaluation_type": 1,
  "weight_percentage": "40.00"
}
```

---

## Componentes (`/api/grading/block-components/`)

### POST — Crear

```json
{
  "evaluation_block": 1,
  "name": "Exámenes",
  "internal_weight": "60.00"
}
```

---

## Indicadores (`/api/grading/component-indicators/`)

### POST — Crear

```json
{
  "block_component": 1,
  "name": "Indicador 1",
  "internal_weight": "100.00"
}
```

---

## Actividades Evaluativas (`/api/grading/evaluative-activities/`)

### POST — Crear

```json
{
  "component_indicator": 1,
  "teacher_subject_section": 1,
  "title": "Examen Parcial 1",
  "activity_type": 1,
  "max_score": "10.00",
  "due_date": "2025-10-15"
}
```

---

## Resúmenes de Período (`/api/grading/period-grade-summaries/`)

### POST — Crear

```json
{
  "enrollment": 1,
  "subject_offering": 1,
  "academic_period": 1,
  "formative_avg": "8.50",
  "summative_avg": "9.00",
  "final_avg_truncated": "8.75",
  "qualitative_scale": 1,
  "requires_recovery": false
}
```

**Filtros GET:** `?enrollment=1`, `?academic_period=1`

---

## Procesos de Recuperación (`/api/grading/recovery-processes/`)

### POST — Crear

```json
{
  "period_grade_summary": 1,
  "subject_offering": 1,
  "managed_by_user": 1,
  "process_type": 1,
  "initial_grade": "6.00",
  "start_date": "2025-12-01"
}
```

---

## Historial de Cambios (`/api/grading/grade-history/`)

### GET — Listar (solo lectura)

---

## Catálogos

### GradeTypes (`/api/grading/grade-types/`)

```json
{"code": "NUM", "name": "Numérica"}
{"code": "CUAL", "name": "Cualitativa"}
{"code": "RECUP", "name": "Recuperación"}
```

### QualitativeScales (`/api/grading/qualitative-scales/`)

```json
{"code": "SE", "name": "Superior", "description": "Supera los aprendizajes", "numeric_equivalence": "9.00"}
{"code": "SA", "name": "Alcanza", "description": "Alcanza los aprendizajes", "numeric_equivalence": "7.00"}
{"code": "AC", "name": "Básico", "description": "Está próximo", "numeric_equivalence": "5.00"}
{"code": "NA", "name": "No Alcanza", "description": "No alcanza los aprendizajes", "numeric_equivalence": "3.00"}
```

### RecoveryProcessTypes (`/api/grading/recovery-process-types/`)

```json
{"code": "MEJORA_DIRECTA", "name": "Mejora Directa", "allows_improvement_eval": true}
{"code": "MEJORA_CON_REFUERZO", "name": "Mejora con Refuerzo", "allows_suppletorio": false}
{"code": "SUPLETORIA", "name": "Supletoria", "allows_suppletorio": true}
```

---

## Códigos de Razón para GradeChangeHistory

| reason_code | Descripción |
|-------------|-------------|
| ERROR_CAPTURA | Error de captura |
| CORRECCION_DOCENTE | Corrección del docente |
| RECUPERACION | Resultado de recuperación |
| MEJORA | Mejora de calificaciones |
| SUPLETORIO | Examen supletorio |
| IMPORTACION | Importación de datos |
| SINCRONIZACION | Sincronización offline |
