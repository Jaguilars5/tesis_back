# API - Módulo Academic

Esta API gestiona la infraestructura académica: períodos académicos, asignaturas, configuraciones por nivel, ofertas de materia y asignación de docentes.

---

## Formato de Respuesta Estándar

Todas las respuestas exitosas devuelven un HTTP 200 (o 201 para creación) con el siguiente esquema:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Autenticación y Permisos

Se requiere un token JWT válido en el header de cada petición:

```
Authorization: Bearer <access_token>
```

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `subject/` | GET | `academic.view_subject` |
| `subject/` | POST | `academic.create_subject` |
| `academic-period/` | GET | `academic.view_academic_period` |
| `academic-period/` | POST | `academic.create_academic_period` |
| `subject-academic-configs/` | GET | `academic.view_subject_academic_config` |
| `subject-offerings/` | GET | `academic.view_subject_offering` |
| `teacher-subject-section/` | GET | `academic.view_teacher_subject_section` |
| `teacher-subject-section/` | POST | `academic.create_teacher_subject_section` |
| `interdisciplinary-projects/` | GET | `academic.view_interdisciplinary_project` |
| `subject-projects/` | GET | `academic.view_subject_project` |

---

## Períodos Académicos (`/api/academic/academic-period/`)

### Listar
**GET** `/api/academic/academic-period/`

### Crear
**POST** `/api/academic/academic-period/`

Request:
```json
{
  "school_year": 1,
  "name": "Quimestre 1",
  "start_date": "2024-09-01",
  "end_date": "2024-11-30"
}
```

---

## Asignaturas (`/api/academic/subject/`)

### Listar
**GET** `/api/academic/subject/`

### Crear
**POST** `/api/academic/subject/`

Request:
```json
{
  "name": "Matemáticas",
  "code": "MAT"
}
```

---

## Configuración de Asignatura por Nivel (`/api/academic/subject-academic-configs/`)

### Listar
**GET** `/api/academic/subject-academic-configs/`

### Crear
**POST** `/api/academic/subject-academic-configs/`

Request:
```json
{
  "subject": 1,
  "academic_level": 1,
  "hours_weekly": 5,
  "order": 1
}
```

---

## Ofertas de Asignatura (`/api/academic/subject-offerings/`)

### Listar
**GET** `/api/academic/subject-offerings/`

### Crear
**POST** `/api/academic/subject-offerings/`

Request:
```json
{
  "subject_academic_config": 1,
  "section": 1,
  "school_year": 1
}
```

---

## Asignación Docente (`/api/academic/teacher-subject-section/`)

### Listar
**GET** `/api/academic/teacher-subject-section/`

### Crear
**POST** `/api/academic/teacher-subject-section/`

Request:
```json
{
  "user": 5,
  "subject_offering": 1
}
```

---

## Proyectos Interdisciplinarios (`/api/academic/interdisciplinary-projects/`)

### Listar
**GET** `/api/academic/interdisciplinary-projects/`

### Crear
**POST** `/api/academic/interdisciplinary-projects/`

Request:
```json
{
  "name": "Proyecto Ambiental",
  "academic_period": 1,
  "description": "Proyecto sobre medio ambiente"
}
```

---

## Proyectos de Asignatura (`/api/academic/subject-projects/`)

### Listar
**GET** `/api/academic/subject-projects/`

---

## Notas

- `Section` ya no existe en `academic` - fue movido a `institutions`. Las secciones ahora se crean vía matrícula en `students`.
- Los campos `level`, `grade`, `timing_regime` en secciones son **legacy** (ya no se usan).
- `academic-activity/` es un endpoint **legacy** - fue reemplazado por `evaluative-activities/` en `grading`.
- La estructura actual usa `SubjectOffering` (oferta de materia por sección) en lugar de asignatura directa por sección.