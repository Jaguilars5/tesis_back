# API - Módulo Academic

Esta API gestiona la infraestructura académica, permitiendo la configuración de períodos, secciones, asignaturas y la asignación de docentes.

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

Todos los ViewSets usan `HasPermission` con `action_permissions`. Ver tabla de permisos en `apps/academic/README.md`.

---

## Secciones (`/api/academic/section/`)

### Listar Secciones
**GET** `/api/academic/section/`

Response:
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "level": "Secundaria",
      "grade": "10mo",
      "parallel": "A",
      "capacity": 35
    }
  ],
  "msg": ""
}
```

### Crear Sección
**POST** `/api/academic/section/`

Request:
```json
{
  "school_year": 1,
  "timing_regime": 1,
  "level": "Secundaria",
  "grade": "10mo",
  "parallel": "A",
  "capacity": 35
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "level": "Secundaria"
  },
  "msg": ""
}
```

---

## Asignaturas (`/api/academic/subject/`)

### Crear Asignatura
**POST** `/api/academic/subject/`

Request:
```json
{
  "school_year": 1,
  "section": 1,
  "name": "Matemáticas",
  "code": "MAT-10A",
  "weekly_hours": 5,
  "approve_percentage": 70
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "Matemáticas"
  },
  "msg": ""
}
```

---

## Actividades Académicas (`/api/academic/academic-activity/`)

### Crear Actividad
**POST** `/api/academic/academic-activity/`

Request:
```json
{
  "config_academic": 1,
  "subject": 1,
  "name": "Examen Primer Quimestre",
  "value_max": 20,
  "weight": 0.5,
  "applies_to": "all",
  "is_recoverable": true,
  "order": 1
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "Examen Primer Quimestre"
  },
  "msg": ""
}
```

---

## Asignación Docente (`/api/academic/teacher-subject-section/`)

### Asignar Docente
**POST** `/api/academic/teacher-subject-section/`

Request:
```json
{
  "user": 5,
  "subject": 1,
  "section": 1,
  "school_year": 1
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "user": 5,
    "subject": 1
  },
  "msg": ""
}
```

---

## Acciones Comunes

### Borrado Lógico (Soft Delete)
**POST** `/api/academic/{recurso}/{id}/soft-delete/`

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "active": false
  },
  "msg": ""
}
```
