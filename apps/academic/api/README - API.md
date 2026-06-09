# API - Módulo Academic

Esta API gestiona la infraestructura académica: materias, períodos académicos, tipos de período, configuraciones por grado, ofertas de materia, asignación docente y proyectos interdisciplinarios.

---

## Formato de Respuesta Estándar

Todas las respuestas usan el formato `{"ok": bool, "data": ..., "msg": "..."}` a través de `StandardResponseRenderer`.

| Código | Descripción                         |
| ------ | ----------------------------------- |
| 200    | Éxito (listar, obtener, actualizar) |
| 201    | Creación exitosa                    |
| 204    | Eliminación exitosa                 |
| 400    | Error de validación/solicitud       |
| 401    | No autenticado                      |
| 403    | Sin permisos                        |
| 404    | No encontrado                       |

---

## Autenticación y Permisos

Se requiere un token JWT válido en el header de cada petición:

```
Authorization: Bearer <access_token>
```

Todos los endpoints requieren autenticación (`IsAuthenticated`) + permiso específico por acción.

### Endpoints y Permisos

| Endpoint                      | GET                                       | POST                                        | PUT/PATCH                                   | DELETE                                      | soft-delete                                 |
| ----------------------------- | ----------------------------------------- | ------------------------------------------- | ------------------------------------------- | ------------------------------------------- | ------------------------------------------- |
| `subject/`                    | `academic.view_subject`                   | `academic.create_subject`                   | `academic.update_subject`                   | `academic.delete_subject`                   | `academic.delete_subject`                   |
| `academic-period/`            | `academic.view_period`                    | `academic.create_period`                    | `academic.update_period`                    | `academic.delete_period`                    | `academic.delete_period`                    |
| `period-types/`               | `academic.view_period_type`               | `academic.create_period_type`               | `academic.update_period_type`               | `academic.delete_period_type`               | `academic.delete_period_type`               |
| `teacher-subject-section/`    | `academic.view_teacher_subject`           | `academic.create_teacher_subject`           | `academic.update_teacher_subject`           | `academic.delete_teacher_subject`           | `academic.delete_teacher_subject`           |
| `subject-academic-configs/`   | `academic.view_subject_config`            | `academic.create_subject_config`            | `academic.update_subject_config`            | `academic.delete_subject_config`            | `academic.delete_subject_config`            |
| `subject-offerings/`          | `academic.view_subject_offering`          | `academic.create_subject_offering`          | `academic.update_subject_offering`          | `academic.delete_subject_offering`          | `academic.delete_subject_offering`          |
| `interdisciplinary-projects/` | `academic.view_interdisciplinary_project` | `academic.create_interdisciplinary_project` | `academic.update_interdisciplinary_project` | `academic.delete_interdisciplinary_project` | `academic.delete_interdisciplinary_project` |
| `subject-projects/`           | `academic.view_subject_project`           | `academic.create_subject_project`           | `academic.update_subject_project`           | `academic.delete_subject_project`           | `academic.delete_subject_project`           |

> **Nota:** El permiso `soft-delete` usa el mismo permiso que `delete`.

---

## Tipos de Período (`/api/academic/period-types/`)

Catálogo de tipos de período (Quimestre, Parcial, etc.).

**GET** `/api/academic/period-types/` — Listar
**POST** `/api/academic/period-types/` — Crear
**PUT** `/api/academic/period-types/{id}/` — Actualizar
**PATCH** `/api/academic/period-types/{id}/` — Actualización parcial
**DELETE** `/api/academic/period-types/{id}/` — Eliminar
**POST** `/api/academic/period-types/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "code": "QUIMESTRE_1",
  "name": "Quimestre 1",
  "description": "Primer quimestre del año escolar"
}
```

Response:

```json
{
  "id": 1,
  "code": "QUIMESTRE_1",
  "name": "Quimestre 1",
  "description": "Primer quimestre del año escolar",
  "is_active": true
}
```

---

## Períodos Académicos (`/api/academic/academic-period/`)

Períodos académicos asociados a un año escolar y tipo de período.

**GET** `/api/academic/academic-period/` — Listar
**POST** `/api/academic/academic-period/` — Crear
**PUT** `/api/academic/academic-period/{id}/` — Actualizar
**PATCH** `/api/academic/academic-period/{id}/` — Actualización parcial
**DELETE** `/api/academic/academic-period/{id}/` — Eliminar
**POST** `/api/academic/academic-period/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "code": "Q1-2024",
  "school_year": 1,
  "name": "Quimestre 1",
  "period_type": 1,
  "start_date": "2024-09-01",
  "end_date": "2024-11-30",
  "is_regular_period": true
}
```

Response:

```json
{
  "id": 1,
  "code": "Q1-2024",
  "school_year": 1,
  "school_year_name": "2024-2025",
  "name": "Quimestre 1",
  "period_type": 1,
  "start_date": "2024-09-01",
  "end_date": "2024-11-30",
  "is_regular_period": true,
  "is_active": true
}
```

---

## Asignaturas (`/api/academic/subject/`)

Catálogo de materias ofrecidas por la institución.

**GET** `/api/academic/subject/` — Listar
**POST** `/api/academic/subject/` — Crear
**PUT** `/api/academic/subject/{id}/` — Actualizar
**PATCH** `/api/academic/subject/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject/{id}/` — Eliminar
**POST** `/api/academic/subject/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "name": "Matemáticas",
  "code": "MAT"
}
```

Response:

```json
{
  "id": 1,
  "name": "Matemáticas",
  "code": "MAT",
  "is_active": true
}
```

---

## Configuración de Asignatura por Grado (`/api/academic/subject-academic-configs/`)

Configuración de qué materias se dictan en cada grado, con horas semanales y orden pedagógico.

**GET** `/api/academic/subject-academic-configs/` — Listar
**POST** `/api/academic/subject-academic-configs/` — Crear
**PUT** `/api/academic/subject-academic-configs/{id}/` — Actualizar
**PATCH** `/api/academic/subject-academic-configs/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject-academic-configs/{id}/` — Eliminar
**POST** `/api/academic/subject-academic-configs/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "subject": 1,
  "academic_grade": 1,
  "weekly_hours": 5,
  "pedagogical_order": 1,
  "is_required": true
}
```

Response:

```json
{
  "id": 1,
  "subject": 1,
  "subject_name": "Matemáticas",
  "academic_grade": 1,
  "academic_grade_name": "10mo EGB",
  "weekly_hours": 5,
  "pedagogical_order": 1,
  "is_required": true,
  "is_active": true
}
```

---

## Ofertas de Asignatura (`/api/academic/subject-offerings/`)

Relación de qué materias se ofertan en cada sección durante un año escolar.

**GET** `/api/academic/subject-offerings/` — Listar
**POST** `/api/academic/subject-offerings/` — Crear
**PUT** `/api/academic/subject-offerings/{id}/` — Actualizar
**PATCH** `/api/academic/subject-offerings/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject-offerings/{id}/` — Eliminar
**POST** `/api/academic/subject-offerings/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "school_year": 1,
  "section": 1,
  "subject_academic_config": 1
}
```

Response:

```json
{
  "id": 1,
  "school_year": 1,
  "school_year_name": "2024-2025",
  "section": 1,
  "section_name": "10mo EGB 'A'",
  "subject_academic_config": 1,
  "subject_academic_config_name": "Matemáticas - 10mo EGB",
  "is_active": true
}
```

> **Nota:** La combinación `(school_year, section, subject_academic_config)` debe ser única.

---

## Asignación Docente (`/api/academic/teacher-subject-section/`)

Asignación de un docente (usuario) a una oferta de materia.

**GET** `/api/academic/teacher-subject-section/` — Listar
**POST** `/api/academic/teacher-subject-section/` — Crear
**PUT** `/api/academic/teacher-subject-section/{id}/` — Actualizar
**PATCH** `/api/academic/teacher-subject-section/{id}/` — Actualización parcial
**DELETE** `/api/academic/teacher-subject-section/{id}/` — Eliminar
**POST** `/api/academic/teacher-subject-section/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "user": 5,
  "subject_offering": 1
}
```

Response:

```json
{
  "id": 1,
  "user": 5,
  "user_name": "Juan Pérez",
  "subject_offering": 1,
  "subject_offering_name": "2024-2025 - 10mo EGB 'A' - Matemáticas - 10mo EGB",
  "is_active": true
}
```

---

## Proyectos Interdisciplinarios (`/api/academic/interdisciplinary-projects/`)

Proyectos que integran múltiples asignaturas en un período académico.

**GET** `/api/academic/interdisciplinary-projects/` — Listar
**POST** `/api/academic/interdisciplinary-projects/` — Crear
**PUT** `/api/academic/interdisciplinary-projects/{id}/` — Actualizar
**PATCH** `/api/academic/interdisciplinary-projects/{id}/` — Actualización parcial
**DELETE** `/api/academic/interdisciplinary-projects/{id}/` — Eliminar
**POST** `/api/academic/interdisciplinary-projects/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "academic_period": 1,
  "title": "Proyecto Ambiental",
  "description": "Proyecto sobre medio ambiente",
  "start_date": "2024-09-15",
  "delivery_date": "2024-11-15"
}
```

Response:

```json
{
  "id": 1,
  "academic_period": 1,
  "academic_period_name": "Quimestre 1",
  "title": "Proyecto Ambiental",
  "description": "Proyecto sobre medio ambiente",
  "start_date": "2024-09-15",
  "delivery_date": "2024-11-15",
  "subject_projects": [],
  "is_active": true
}
```

> Incluye los `subject_projects` asociados en la respuesta (read-only).

---

## Proyectos de Asignatura (`/api/academic/subject-projects/`)

Asociación entre un proyecto interdisciplinario y una oferta de asignatura participante.

**GET** `/api/academic/subject-projects/` — Listar
**POST** `/api/academic/subject-projects/` — Crear
**PUT** `/api/academic/subject-projects/{id}/` — Actualizar
**PATCH** `/api/academic/subject-projects/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject-projects/{id}/` — Eliminar
**POST** `/api/academic/subject-projects/{id}/soft-delete/` — Desactivar

Request (POST/PUT):

```json
{
  "interdisciplinary_project": 1,
  "subject_offering": 1
}
```

Response:

```json
{
  "id": 1,
  "interdisciplinary_project": 1,
  "interdisciplinary_project_title": "Proyecto Ambiental",
  "subject_offering": 1,
  "subject_offering_name": "2024-2025 - 10mo EGB 'A' - Matemáticas - 10mo EGB"
}
```

> **Nota:** La combinación `(interdisciplinary_project, subject_offering)` debe ser única.

---

## Características Comunes

### Soft Delete

Todos los endpoints incluyen la acción `POST /{id}/soft-delete/` que marca `is_active = False` en lugar de eliminar el registro. Solamente funciona en modelos que tengan el campo `is_active`.

### Paginación

Usa `StandardResultsSetPagination`. La respuesta paginada incluye:

```json
{
  "count": 100,
  "next": "http://...?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Notas

- `Section` ya no existe en `academic` — fue movido a `institutions`. Las secciones ahora se crean vía matrícula en `students`.
- `academic-activity/` es un endpoint **legacy** — fue reemplazado por `evaluative-activities/` en `grading`.
- La estructura actual usa `SubjectOffering` (oferta de materia por sección) en lugar de asignatura directa por sección.
- El permiso `academic.view_config` y `academic.create_config` (sin `_subject`) existen en el sistema pero no se usan en los ViewSets actuales; se emplean `view_subject_config` / `create_subject_config`.
