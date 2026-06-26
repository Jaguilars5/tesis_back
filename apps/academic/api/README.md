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
| `subjects/` | `academic.view_subject` | `academic.create_subject` | `academic.update_subject` | `academic.delete_subject` | `academic.delete_subject` |
| `academic-periods/` | `academic.view_period` | `academic.create_period` | `academic.update_period` | `academic.delete_period` | `academic.delete_period` |
| `period-types/` | `academic.view_period_type` | `academic.create_period_type` | `academic.update_period_type` | `academic.delete_period_type` | `academic.delete_period_type` |
| `teacher-subject-sections/` | `academic.view_teacher_subject` | `academic.create_teacher_subject` | `academic.update_teacher_subject` | `academic.delete_teacher_subject` | `academic.delete_teacher_subject` |
| `subject-academic-configs/` | `academic.view_subject_config` | `academic.create_subject_config` | `academic.update_subject_config` | `academic.delete_subject_config` | `academic.delete_subject_config` |
| `subject-offerings/` | `academic.view_subject_offering` | `academic.create_subject_offering` | `academic.update_subject_offering` | `academic.delete_subject_offering` | `academic.delete_subject_offering` |
| `class-schedules/` | `academic.view_class_schedule` | `academic.create_class_schedule` | `academic.update_class_schedule` | `academic.delete_class_schedule` | `academic.delete_class_schedule` |

---

## Asignaturas (`/api/academic/subjects/`)

Catálogo de materias.

**GET** `/api/academic/subjects/` — Listar
**POST** `/api/academic/subjects/` — Crear
**GET** `/api/academic/subjects/{id}/` — Obtener
**PUT** `/api/academic/subjects/{id}/` — Actualizar
**PATCH** `/api/academic/subjects/{id}/` — Actualización parcial
**DELETE** `/api/academic/subjects/{id}/` — Eliminar
**POST** `/api/academic/subjects/{id}/soft-delete/` — Desactivar (requiere `{"confirm": true}`)

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
  "is_active": true,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

---

## Tipos de Período (`/api/academic/period-types/`)

Catálogo de tipos de período (Trimestre, Quimestre, Parcial, etc.).

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
  "description": "Primer quimestre del año escolar",
  "divisions_per_year": 2
}
```

Response:
```json
{
  "id": 1,
  "code": "QUIMESTRE_1",
  "name": "Quimestre 1",
  "description": "Primer quimestre del año escolar",
  "divisions_per_year": 2,
  "is_active": true,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

Campos adicionales en el modelo: `divisions_per_year` (PositiveSmallIntegerField, ej: 3 para Trimestre).

---

## Períodos Académicos (`/api/academic/academic-periods/`)

Períodos académicos asociados a un año escolar y tipo de período.

> **Nota:** Ya no existe el campo `parent_period`. Los períodos ya no se anidan jerárquicamente.
> El campo `peso_en_anio` fue renombrado a `year_weight`.

**GET** `/api/academic/academic-periods/` — Listar
**POST** `/api/academic/academic-periods/` — Crear
**GET** `/api/academic/academic-periods/{id}/` — Obtener
**PUT** `/api/academic/academic-periods/{id}/` — Actualizar
**PATCH** `/api/academic/academic-periods/{id}/` — Actualización parcial
**DELETE** `/api/academic/academic-periods/{id}/` — Eliminar
**POST** `/api/academic/academic-periods/{id}/soft-delete/` — Desactivar

Request:
```json
{
  "code": "Q1-2024",
  "school_year": 1,
  "name": "Quimestre 1",
  "period_type": 1,
  "start_date": "2024-09-01",
  "end_date": "2024-11-30",
  "year_weight": "40.00",
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
  "start_date": "2024-09-01",
  "end_date": "2024-11-30",
  "year_weight": "40.00",
  "is_regular_period": true,
  "is_active": true,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

---

## Configuración de Asignatura por Grado (`/api/academic/subject-academic-configs/`)

Configuración de materias por grado con horas semanales.

> **Nota:** Ya no existe el campo `pedagogical_order`.

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
  "is_required": true,
  "is_active": true,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

> Unique: `(subject, academic_grade)`.

---

## Ofertas de Asignatura (`/api/academic/subject-offerings/`)

Relación de materias ofertadas en cada sección.

> **Nota:** Ya no tiene FK directo a `school_year`. `school_year` se obtiene como propiedad desde `section.school_year`.
> Unique constraint cambió de `(school_year, section, subject_academic_config)` a `(section, subject_academic_config)`.

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
  "is_active": true,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

> Unique: `(section, subject_academic_config)`.

---

## Asignación Docente (`/api/academic/teacher-subject-sections/`)

Asignación de un docente (usuario) a una oferta de materia.

**GET** `/api/academic/teacher-subject-sections/` — Listar
**POST** `/api/academic/teacher-subject-sections/` — Crear
**GET** `/api/academic/teacher-subject-sections/{id}/` — Obtener
**PUT** `/api/academic/teacher-subject-sections/{id}/` — Actualizar
**PATCH** `/api/academic/teacher-subject-sections/{id}/` — Actualización parcial
**DELETE** `/api/academic/teacher-subject-sections/{id}/` — Eliminar
**POST** `/api/academic/teacher-subject-sections/{id}/soft-delete/` — Desactivar

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
  "subject_offering_name": "Matemáticas - 10mo EGB 'A'",
  "subject_offering_school_year": 1,
  "subject_offering_school_year_name": "2024-2025",
  "subject_offering_section": 1,
  "subject_offering_section_name": "10mo EGB 'A'",
  "subject_offering_academic_grade": 1,
  "subject_offering_academic_grade_name": "10mo EGB",
  "subject_offering_subject": 1,
  "subject_offering_subject_name": "Matemáticas",
  "subject_offering_config": 1,
  "subject_offering_config_name": "Matemáticas - 10mo EGB",
  "is_active": true,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

> Unique: `(user, subject_offering)`.

---

## Horarios Académicos (`/api/academic/class-schedules/`)

Horarios asociados a una asignación docente-materia-sección.

**GET** `/api/academic/class-schedules/` — Listar
**POST** `/api/academic/class-schedules/` — Crear
**GET** `/api/academic/class-schedules/{id}/` — Obtener
**PUT** `/api/academic/class-schedules/{id}/` — Actualizar
**PATCH** `/api/academic/class-schedules/{id}/` — Actualización parcial
**DELETE** `/api/academic/class-schedules/{id}/` — Eliminar
**POST** `/api/academic/class-schedules/{id}/soft-delete/` — Desactivar

**GET** `/api/academic/class-schedules/by-section/?section_id=X` — Horarios de una sección
**GET** `/api/academic/class-schedules/my-schedule/` — Horario del usuario autenticado (docente o estudiante)
**GET** `/api/academic/class-schedules/my-today/` — Clases de hoy (solo docentes)

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
  "day_of_week": 1,
  "start_time": "07:00",
  "end_time": "08:30",
  "is_active": true,
  "subject_offering_name": "Matemáticas - 10mo EGB 'A'",
  "day_of_week_name": "Lunes",
  "section_name": "10mo EGB 'A'",
  "section_id": 1,
  "subject_name": "Matemáticas",
  "subject_id": 1,
  "teacher_name": "Juan Pérez",
  "teacher_id": 5,
  "created_at": "2024-09-01T00:00:00Z",
  "updated_at": "2024-09-01T00:00:00Z"
}
```

> `day_of_week` usa `DayOfWeekChoices` (IntegerChoices): 1=Lunes, 2=Martes, 3=Miércoles, 4=Jueves, 5=Viernes, 6=Sábado, 7=Domingo.
> Unique: `(teacher_subject_section, day_of_week, start_time)`.

### Acciones adicionales de ClassSchedule

#### `by-section`
```
GET /api/academic/class-schedules/by-section/?section_id=1
```
Retorna todos los horarios de una sección específica. Requiere query param `section_id`.

#### `my-schedule`
```
GET /api/academic/class-schedules/my-schedule/
```
Retorna el horario del usuario autenticado:
- Si es `ESTUDIANTE`, busca por su perfil de estudiante (`student.id`)
- Si es docente, busca por `user.id`

#### `my-today`
```
GET /api/academic/class-schedules/my-today/
```
Retorna las clases del día actual para el docente autenticado. Solo disponible para usuarios con `user_category` de docente.

---

## Características Comunes

### Soft Delete con Confirmación

`POST /{id}/soft-delete/` marca `is_active = False` en lugar de eliminar. Todos los endpoints requieren body `{"confirm": true}`.

Incluye validación en cascada: si el registro tiene dependencias activas, rechaza la operación con un mensaje descriptivo.

### Paginación

Usa `StandardResultsSetPagination` (subclase de `PageNumberPagination`). La respuesta paginada incluye `count`, `next`, `previous`, `results`.

### Búsqueda y Filtros

Cada ViewSet expone:
- `search` query param para búsqueda textual (ver campos `search_fields` en cada ViewSet)
- Filtros vía `django-filter` (ver `filterset_class` en cada ViewSet)
- Ordenamiento vía `ordering` query param

### AcademicRouter

Los endpoints usan un `AcademicRouter` personalizado con routing explícito en lugar del `DefaultRouter` estándar. Las URLs usan **plural** para todos los recursos.

---

## Notas

- Los endpoints usan **plural**: `subjects/`, `academic-periods/`, `class-schedules/`, etc.
- `SubjectOffering` ya no tiene FK a `school_year` — se obtiene vía `section.school_year`.
- `AcademicPeriod` ya no tiene `parent_period`.
- `SubjectAcademicConfig` ya no tiene `pedagogical_order`.
- El campo `peso_en_anio` fue renombrado a `year_weight`.
- `Section` pertenece a la app `institutions`.
- `DayOfWeekChoices` es un `IntegerChoices` dentro del modelo `ClassSchedule`.
