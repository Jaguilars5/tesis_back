# API - Módulo Grading

Esta API gestiona el desempeño estudiantil: calificaciones estructuradas en bloques de evaluación, tipos de calificación, escalas cualitativas y procesos de recuperación.

---

## Formato de Respuesta

Todas las peticiones devuelven el esquema estandarizado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Autenticación y Permisos

Header requerido:
```
Authorization: Bearer <access_token>
```

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student-notes/` | GET | `grading.view_note` |
| `student-notes/` | POST | `grading.create_note` |
| `student-notes/{id}/` | GET | `grading.view_note` |
| `student-notes/{id}/` | PATCH | `grading.update_note` |
| `student-notes/{id}/` | DELETE | `grading.delete_note` |
| `grade-types/` | GET | `grading.view_gradetype` |
| `qualitative-scales/` | GET | `grading.view_qualitativescale` |
| `evaluation-blocks/` | GET | `grading.view_evaluationblock` |
| `evaluation-blocks/` | POST | `grading.create_evaluationblock` |
| `block-components/` | GET | `grading.view_blockcomponent` |
| `component-indicators/` | GET | `grading.view_componentindicator` |
| `evaluative-activities/` | GET | `grading.view_evaluativeactivity` |
| `grade-history/` | GET | `grading.view_gradechangehistory` |
| `period-grade-summaries/` | GET | `grading.view_periodgradesummary` |
| `recovery-processes/` | GET | `grading.view_recoveryprocess` |
| `recovery-processes/` | POST | `grading.create_recoveryprocess` |
| `diagnostic-evaluations/` | GET | `grading.view_diagnosticevaluation` |
| `project-notes/` | GET | `grading.view_projectnote` |

---

## Calificaciones (`/api/grading/student-notes/`)

### Listar
**GET** `/api/grading/student-notes/`

Response (paginado):
```json
{
  "ok": true,
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "enrollment": 1,
        "evaluative_activity": 1,
        "numeric_score": 8.5,
        "qualitative_score": 8.5,
        "qualitative_scale": 1,
        "manually_overridden": false
      }
    ]
  },
  "msg": ""
}
```

### Crear
**POST** `/api/grading/student-notes/`

Request:
```json
{
  "enrollment": 1,
  "evaluative_activity": 1,
  "numeric_score": 18.50,
  "qualitative_score": 18.50,
  "qualitative_scale": 1,
  "teacher_observation": "Buen trabajo"
}
```

---

## Bloques de Evaluación (`/api/grading/evaluation-blocks/`)

### Listar
**GET** `/api/grading/evaluation-blocks/`

### Crear
**POST** `/api/grading/evaluation-blocks/`

Request:
```json
{
  "academic_period": 1,
  "name": "Bloque 1 - Quimestre 1",
  "weight": 40.0
}
```

---

## Componentes de Bloque (`/api/grading/block-components/`)

### Crear
**POST** `/api/grading/block-components/`

Request:
```json
{
  "evaluation_block": 1,
  "name": "Exámenes",
  "weight": 60.0
}
```

---

## Indicadores de Componente (`/api/grading/component-indicators/`)

### Crear
**POST** `/api/grading/component-indicators/`

Request:
```json
{
  "block_component": 1,
  "name": "Indicador 1",
  "order": 1
}
```

---

## Actividades Evaluativas (`/api/grading/evaluative-activities/`)

### Crear
**POST** `/api/grading/evaluative-activities/`

Request:
```json
{
  "component_indicator": 1,
  "teacher_subject_section": 1,
  "grade_type": 1,
  "name": "Examen Parcial 1",
  "max_score": 10.0
}
```

---

## Tipos de Calificación (`/api/grading/grade-types/`)

### Listar
**GET** `/api/grading/grade-types/`

Response:
```json
{
  "ok": true,
  "data": [
    {"id": 1, "code": "PAR", "name": "Parcial"},
    {"id": 2, "code": "REC", "name": "Recuperación"}
  ],
  "msg": ""
}
```

---

## Escalas Cualitativas (`/api/grading/qualitative-scales/`)

### Listar
**GET** `/api/grading/qualitative-scales/`

Response:
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "name": "Escala Ecuador",
      "min_value": 1,
      "max_value": 10,
      "passing_value": 7
    }
  ],
  "msg": ""
}
```

---

## Historial de Cambios (`/api/grading/grade-history/`)

### Listar
**GET** `/api/grading/grade-history/`

---

## Resúmenes de Período (`/api/grading/period-grade-summaries/`)

### Listar
**GET** `/api/grading/period-grade-summaries/`

Filtros: `enrollment`, `academic_period`

---

## Procesos de Recuperación (`/api/grading/recovery-processes/`)

### Listar
**GET** `/api/grading/recovery-processes/`

### Crear
**POST** `/api/grading/recovery-processes/`

Request:
```json
{
  "enrollment": 1,
  "academic_period": 1,
  "recovery_type": "EXAM",
  "start_date": "2024-12-01",
  "end_date": "2024-12-15"
}
```

---

## Evaluaciones Diagnósticas (`/api/grading/diagnostic-evaluations/`)

### Listar
**GET** `/api/grading/diagnostic-evaluations/`

---

## Notas de Proyecto (`/api/grading/project-notes/`)

### Listar
**GET** `/api/grading/project-notes/`

---

## Notas

- La asistencia y incidentes conductuales ahora se gestionan en el módulo **Attendance** (`/api/attendance/`).
- Los endpoints de calificaciones ahora usan `evaluative_activity` en lugar de `class_assignment`.