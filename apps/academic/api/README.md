# API — Módulo Academic

Gestiona la infraestructura académica: materias, períodos académicos, tipos de período, configuraciones por grado, ofertas de materia, asignación docente y horarios.

---

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.

| Código | Descripción |
| ------ | ----------- |
| 200 | Éxito (listar, obtener, actualizar) |
| 201 | Creación exitosa |
| 204 | Eliminación exitosa |
| 400 | Error de validación/solicitud |
| 401 | No autenticado |
| 403 | Sin permisos |
| 404 | No encontrado |

---

## Autenticación y Permisos

```
Authorization: Bearer <access_token>
```

Todos los endpoints requieren `IsAuthenticated` + permiso específico por acción vía `HasPermission`.

| Endpoint | GET | POST | PUT/PATCH | DELETE | soft-delete |
| -------- | --- | ---- | --------- | ------ | ----------- |
| `subject/` | `academic.view_subject` | `academic.create_subject` | `academic.update_subject` | `academic.delete_subject` | `academic.delete_subject` |
| `academic-period/` | `academic.view_period` | `academic.create_period` | `academic.update_period` | `academic.delete_period` | `academic.delete_period` |
| `period-types/` | `academic.view_period_type` | `academic.create_period_type` | `academic.update_period_type` | `academic.delete_period_type` | `academic.delete_period_type` |
| `teacher-subject-section/` | `academic.view_teacher_subject` | `academic.create_teacher_subject` | `academic.update_teacher_subject` | `academic.delete_teacher_subject` | `academic.delete_teacher_subject` |
| `subject-academic-configs/` | `academic.view_subject_config` | `academic.create_subject_config` | `academic.update_subject_config` | `academic.delete_subject_config` | `academic.delete_subject_config` |
| `subject-offerings/` | `academic.view_subject_offering` | `academic.create_subject_offering` | `academic.update_subject_offering` | `academic.delete_subject_offering` | `academic.delete_subject_offering` |
| `class-schedule/` | `academic.view_class_schedule` | `academic.create_class_schedule` | `academic.update_class_schedule` | `academic.delete_class_schedule` | `academic.delete_class_schedule` |

---

## Asignaturas (`/api/academic/subject/`)

Catálogo de materias.

**GET** `/api/academic/subject/` — Listar
**POST** `/api/academic/subject/` — Crear
**GET** `/api/academic/subject/{id}/` — Obtener
**PUT** `/api/academic/subject/{id}/` — Actualizar
**PATCH** `/api/academic/subject/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject/{id}/` — Eliminar
**POST** `/api/academic/subject/{id}/soft-delete/` — Desactivar

Request:
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

## Tipos de Período (`/api/academic/period-types/`)

Catálogo de tipos de período (Quimestre, Parcial, etc.).

**GET** `/api/academic/period-types/` — Listar
**POST** `/api/academic/period-types/` — Crear
**GET** `/api/academic/period-types/{id}/` — Obtener
**PUT** `/api/academic/period-types/{id}/` — Actualizar
**PATCH** `/api/academic/period-types/{id}/` — Actualización parcial
**DELETE** `/api/academic/period-types/{id}/` — Eliminar
**POST** `/api/academic/period-types/{id}/soft-delete/` — Desactivar

Request:
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

Períodos académicos asociados a un año escolar y tipo de período. Pueden anidarse vía `parent_period` (ej: un Quimestre como padre de parciales).

**GET** `/api/academic/academic-period/` — Listar
**POST** `/api/academic/academic-period/` — Crear
**GET** `/api/academic/academic-period/{id}/` — Obtener
**PUT** `/api/academic/academic-period/{id}/` — Actualizar
**PATCH** `/api/academic/academic-period/{id}/` — Actualización parcial
**DELETE** `/api/academic/academic-period/{id}/` — Eliminar
**POST** `/api/academic/academic-period/{id}/soft-delete/` — Desactivar

Request:
```json
{
  "code": "Q1-2024",
  "school_year": 1,
  "name": "Quimestre 1",
  "period_type": 1,
  "parent_period": null,
  "start_date": "2024-09-01",
  "end_date": "2024-11-30",
  "peso_en_anio": "40.00",
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
  "period_type_name": "Quimestre",
  "parent_period": null,
  "start_date": "2024-09-01",
  "end_date": "2024-11-30",
  "peso_en_anio": "40.00",
  "is_regular_period": true,
  "is_active": true
}
```

---

## Configuración de Asignatura por Grado (`/api/academic/subject-academic-configs/`)

Configuración de materias por grado con horas semanales y orden pedagógico.

**GET** `/api/academic/subject-academic-configs/` — Listar
**POST** `/api/academic/subject-academic-configs/` — Crear
**GET** `/api/academic/subject-academic-configs/{id}/` — Obtener
**PUT** `/api/academic/subject-academic-configs/{id}/` — Actualizar
**PATCH** `/api/academic/subject-academic-configs/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject-academic-configs/{id}/` — Eliminar
**POST** `/api/academic/subject-academic-configs/{id}/soft-delete/` — Desactivar

Request:
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

> Unique: `(subject, academic_grade)`.

---

## Ofertas de Asignatura (`/api/academic/subject-offerings/`)

Relación de materias ofertadas en cada sección durante un año escolar.

**GET** `/api/academic/subject-offerings/` — Listar
**POST** `/api/academic/subject-offerings/` — Crear
**GET** `/api/academic/subject-offerings/{id}/` — Obtener
**PUT** `/api/academic/subject-offerings/{id}/` — Actualizar
**PATCH** `/api/academic/subject-offerings/{id}/` — Actualización parcial
**DELETE** `/api/academic/subject-offerings/{id}/` — Eliminar
**POST** `/api/academic/subject-offerings/{id}/soft-delete/` — Desactivar

Request:
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

> Unique: `(school_year, section, subject_academic_config)`.

---

## Asignación Docente (`/api/academic/teacher-subject-section/`)

Asignación de un docente (usuario) a una oferta de materia.

**GET** `/api/academic/teacher-subject-section/` — Listar
**POST** `/api/academic/teacher-subject-section/` — Crear
**GET** `/api/academic/teacher-subject-section/{id}/` — Obtener
**PUT** `/api/academic/teacher-subject-section/{id}/` — Actualizar
**PATCH** `/api/academic/teacher-subject-section/{id}/` — Actualización parcial
**DELETE** `/api/academic/teacher-subject-section/{id}/` — Eliminar
**POST** `/api/academic/teacher-subject-section/{id}/soft-delete/` — Desactivar

Request:
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

> Unique: `(user, subject_offering)`.

---

## Horarios Académicos (`/api/academic/class-schedule/`)

Horarios asociados a una asignación docente-materia-sección.

**GET** `/api/academic/class-schedule/` — Listar
**POST** `/api/academic/class-schedule/` — Crear
**GET** `/api/academic/class-schedule/{id}/` — Obtener
**PUT** `/api/academic/class-schedule/{id}/` — Actualizar
**PATCH** `/api/academic/class-schedule/{id}/` — Actualización parcial
**DELETE** `/api/academic/class-schedule/{id}/` — Eliminar
**POST** `/api/academic/class-schedule/{id}/soft-delete/` — Desactivar

Request:
```json
{
  "teacher_subject_section": 1,
  "day_of_week": 1,
  "start_time": "07:00",
  "end_time": "08:30"
}
```

Response:
```json
{
  "id": 1,
  "teacher_subject_section": 1,
  "subject_offering_name": "2024-2025 - 10mo EGB 'A' - Matemáticas - 10mo EGB",
  "day_of_week": 1,
  "day_of_week_name": "Lunes",
  "start_time": "07:00",
  "end_time": "08:30",
  "is_active": true
}
```

> `day_of_week` usa `IntegerChoices`: 1=Lunes..7=Domingo. Unique: `(teacher_subject_section, day_of_week, start_time)`.

---

## Características Comunes

### Soft Delete

`POST /{id}/soft-delete/` marca `is_active = False` en lugar de eliminar. Funciona en todos los modelos con campo `is_active`.

### Paginación

Usa `StandardResultsSetPagination` (subclase de `PageNumberPagination`). La respuesta paginada incluye `count`, `next`, `previous`, `results`.

---

## Notas

- Los modelos `InterdisciplinaryProject`, `SubjectProject` y `DayOfWeek` **no existen** en este módulo. `DayOfWeek` es un `IntegerChoices` dentro de `ClassSchedule`.
- No hay endpoints para `interdisciplinary-projects/` ni `subject-projects/`.
- `Section` pertenece a `institutions`.
- Los permisos `academic.view_config`/`create_config`/`update_config`/`delete_config` existen en el sistema como constantes pero **no se usan** en ningún ViewSet; se emplean `view_subject_config`, `create_subject_config`, etc.
- Los permisos `academic.view_interdisciplinary_project`, `academic.view_subject_project`, `academic.view_day_of_week` existen como constantes pero ningún ViewSet los utiliza.
