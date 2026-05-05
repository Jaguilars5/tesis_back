# Cambios Requeridos en el Frontend

## 1. Resumen de Cambios

El backend migró de un patrón de vistas basadas en `POST` con ID en el body a un API **RESTful** usando **ViewSets de DRF**. Además, se implementó un sistema de **permisos granulares** que requiere autenticación JWT + permiso específico para cada endpoint.

**Módulos afectados:** `grading`, `scheduling`, `analytics`

---

## 2. Nuevas URLs RESTful

### 2.1 Grading — Calificaciones

| Acción | Método Antiguo (POST) | Método Nuevo | URL Nueva |
|--------|----------------------|--------------|-----------|
| Listar | `POST /api/grading/student-note/list/` | `GET` | `/api/grading/student-notes/` |
| Obtener | `POST /api/grading/student-note/get/` | `GET` | `/api/grading/student-notes/{id}/` |
| Crear | `POST /api/grading/student-note/add/` | `POST` | `/api/grading/student-notes/` |
| Actualizar | `POST /api/grading/student-note/update/` | `PATCH` | `/api/grading/student-notes/{id}/` |
| Eliminar | `POST /api/grading/student-note/soft-delete/` | `DELETE` | `/api/grading/student-notes/{id}/` |

### 2.2 Grading — Asistencia

| Acción | Método Antiguo | Método Nuevo | URL Nueva |
|--------|---------------|--------------|-----------|
| Listar | `POST /api/grading/attendance/list/` | `GET` | `/api/grading/attendance/` |
| Obtener | `POST /api/grading/attendance/get/` | `GET` | `/api/grading/attendance/{id}/` |
| Crear | `POST /api/grading/attendance/add/` | `POST` | `/api/grading/attendance/` |
| Actualizar | `POST /api/grading/attendance/update/` | `PATCH` | `/api/grading/attendance/{id}/` |
| Eliminar | `POST /api/grading/attendance/soft-delete/` | `DELETE` | `/api/grading/attendance/{id}/` |

### 2.3 Grading — Incidentes de Conducta

| Acción | Método Antiguo | Método Nuevo | URL Nueva |
|--------|---------------|--------------|-----------|
| Listar | `POST /api/grading/conduct-incident/list/` | `GET` | `/api/grading/conduct-incidents/` |
| Obtener | `POST /api/grading/conduct-incident/get/` | `GET` | `/api/grading/conduct-incidents/{id}/` |
| Crear | `POST /api/grading/conduct-incident/add/` | `POST` | `/api/grading/conduct-incidents/` |
| Actualizar | `POST /api/grading/conduct-incident/update/` | `PATCH` | `/api/grading/conduct-incidents/{id}/` |
| Eliminar | `POST /api/grading/conduct-incident/soft-delete/` | `DELETE` | `/api/grading/conduct-incidents/{id}/` |

### 2.4 Scheduling

| Modelo | Listar | Obtener | Crear | Actualizar | Eliminar |
|--------|--------|---------|-------|------------|----------|
| ScheduleSlot | `GET /api/scheduling/schedule-slots/` | `GET /api/scheduling/schedule-slots/{id}/` | `POST /api/scheduling/schedule-slots/` | `PATCH /api/scheduling/schedule-slots/{id}/` | `DELETE /api/scheduling/schedule-slots/{id}/` |
| TimeSlot | `GET /api/scheduling/time-slots/` | ... | ... | ... | ... |
| TeacherAvailability | `GET /api/scheduling/teacher-availability/` | ... | ... | ... | ... |
| SubjectConstraint | `GET /api/scheduling/subject-constraints/` | ... | ... | ... | ... |
| ScheduleTemplateConfig | `GET /api/scheduling/schedule-configs/` | ... | ... | ... | ... |

### 2.5 Analytics

| Modelo | Listar | Obtener |
|--------|--------|---------|
| StudentRiskScore | `GET /api/analytics/student-risk-scores/` | `GET /api/analytics/student-risk-scores/{id}/` |
| StudentFeatureSnapshot | `GET /api/analytics/feature-snapshots/` | `GET /api/analytics/feature-snapshots/{id}/` |

---

## 3. Autenticación

Todos los endpoints (excepto login/refresh) requieren:

```
Authorization: Bearer <access_token>
```

Si no se envía token → `401 Unauthorized`
Si el token no tiene el permiso requerido → `403 Forbidden`

### Endpoints públicos (sin auth):
- `POST /api/accounts/login/`
- `POST /api/accounts/refresh/`

---

## 4. Cambios en el Formato de Peticiones

### 4.1 ID ahora va en la URL, no en el body

**Antes (POST con ID en body):**
```json
POST /api/grading/student-note/get/
{
  "id": 123
}
```

**Ahora (GET con ID en URL):**
```
GET /api/grading/student-notes/123/
```

### 4.2 Crear recurso

**Antes:**
```json
POST /api/grading/student-note/add/
{
  "student": 1,
  "note_value": 18.5,
  ...
}
```

**Ahora (mismo método POST, URL diferente):**
```json
POST /api/grading/student-notes/
{
  "student": 1,
  "note_value": 18.5,
  ...
}
```

### 4.3 Actualizar recurso

**Antes:**
```json
POST /api/grading/student-note/update/
{
  "id": 123,
  "note_value": 19.0
}
```

**Ahora:**
```json
PATCH /api/grading/student-notes/123/
{
  "note_value": 19.0
}
```

### 4.4 Eliminar recurso

**Antes:**
```json
POST /api/grading/student-note/soft-delete/
{
  "id": 123
}
```

**Ahora:**
```
DELETE /api/grading/student-notes/123/
```

---

## 5. Cambios en el Formato de Respuestas

Las respuestas ahora incluyen paginación estándar para listados:

```json
{
  "ok": true,
  "data": {
    "count": 25,
    "next": "http://localhost:8000/api/grading/student-notes/?page=2",
    "previous": null,
    "results": [
      { "id": 1, ... },
      { "id": 2, ... }
    ]
  },
  "msg": ""
}
```

**Parámetros de paginación:**
- `?page=2` — Navegar a página 2
- `?page_size=50` — Cambiar tamaño de página (default: 20, max: 100)

Para respuestas de detalle (single resource), no hay paginación:

```json
{
  "ok": true,
  "data": {
    "id": 1,
    ...
  },
  "msg": ""
}
```

---

## 6. Errores de Autenticación y Permisos

### Sin autenticación (401):
```json
{
  "ok": false,
  "data": {},
  "msg": "No tienes permiso para realizar esta acción."
}
```

### Sin permiso específico (403):
```json
{
  "ok": false,
  "data": {},
  "msg": "No tienes permiso para realizar esta acción."
}
```

---

## 7. Tabla de Permisos Requeridos

Cada endpoint requiere un permiso específico. El usuario debe tenerlo asignado via rol o UserPermission.

### 7.1 Accounts

| ViewSet | list/retrieve | create | update | delete |
|---------|---------------|--------|--------|--------|
| User | `accounts.view_user` | `accounts.create_user` | `accounts.update_user` | `accounts.delete_user` |
| Role | `accounts.view_role` | `accounts.create_role` | `accounts.update_role` | `accounts.delete_role` |
| Permission | `accounts.view_permission` | `accounts.create_permission` | `accounts.update_permission` | `accounts.delete_permission` |

### 7.2 Institutions

| ViewSet | list/retrieve | create | update | delete |
|---------|---------------|--------|--------|--------|
| Institution | `institutions.view_institution` | `institutions.create_institution` | `institutions.update_institution` | `institutions.delete_institution` |
| SchoolYear | `institutions.view_school_year` | `institutions.create_school_year` | `institutions.update_school_year` | `institutions.delete_school_year` |
| Classroom | `institutions.view_classroom` | `institutions.create_classroom` | `institutions.update_classroom` | `institutions.delete_classroom` |

### 7.3 Academic

| ViewSet | list/retrieve | create | update | delete |
|---------|---------------|--------|--------|--------|
| Section | `academic.view_section` | `academic.create_section` | `academic.update_section` | `academic.delete_section` |
| Subject | `academic.view_subject` | `academic.create_subject` | `academic.update_subject` | `academic.delete_subject` |
| ConfigAcademic | `academic.view_config` | `academic.create_config` | `academic.update_config` | `academic.delete_config` |
| AcademicPeriod | `academic.view_period` | `academic.create_period` | `academic.update_period` | `academic.delete_period` |
| AcademicActivity | `academic.view_activity` | `academic.create_activity` | `academic.update_activity` | `academic.delete_activity` |
| TimingRegime | `academic.view_regime` | `academic.create_regime` | `academic.update_regime` | `academic.delete_regime` |
| TeacherSubjectSection | `academic.view_teacher_subject` | `academic.create_teacher_subject` | `academic.update_teacher_subject` | `academic.delete_teacher_subject` |

### 7.4 Students

| ViewSet | list/retrieve | create | update | delete |
|---------|---------------|--------|--------|--------|
| Student | `students.view_student` | `students.create_student` | `students.update_student` | `students.delete_student` |
| Representative | `students.view_representative` | `students.create_representative` | `students.update_representative` | `students.delete_representative` |
| StudentRepresentative | `students.view_relationship` | `students.create_relationship` | `students.update_relationship` | `students.delete_relationship` |

### 7.5 Grading

| ViewSet | list/retrieve | create | update | delete |
|---------|---------------|--------|--------|--------|
| StudentNote | `grading.view_note` | `grading.create_note` | `grading.update_note` | `grading.delete_note` |
| Attendance | `grading.view_attendance` | `grading.create_attendance` | `grading.update_attendance` | `grading.delete_attendance` |
| ConductIncident | `grading.view_incident` | `grading.create_incident` | `grading.update_incident` | `grading.delete_incident` |

### 7.6 Scheduling

| ViewSet | list/retrieve | create | update | delete |
|---------|---------------|--------|--------|--------|
| ScheduleSlot | `scheduling.view_schedule` | `scheduling.create_schedule` | `scheduling.update_schedule` | `scheduling.delete_schedule` |
| TimeSlot | `scheduling.view_timeslot` | `scheduling.create_timeslot` | `scheduling.update_timeslot` | `scheduling.delete_timeslot` |
| TeacherAvailability | `scheduling.view_availability` | `scheduling.create_availability` | `scheduling.update_availability` | `scheduling.delete_availability` |
| SubjectConstraint | `scheduling.view_constraint` | `scheduling.create_constraint` | `scheduling.update_constraint` | `scheduling.delete_constraint` |
| ScheduleTemplateConfig | `scheduling.view_template` | `scheduling.create_template` | `scheduling.update_template` | `scheduling.delete_template` |

### 7.7 Analytics

| ViewSet | list/retrieve |
|---------|---------------|
| StudentRiskScore | `analytics.view_risk_score` |
| StudentFeatureSnapshot | `analytics.view_feature_snapshot` |

---

## 8. Seed de Permisos

Antes de usar cualquier endpoint protegido, se deben seedear los permisos:

```bash
python manage.py seed_permissions
# O solo un módulo:
python manage.py seed_permissions --module grading
```

---

## 9. Resumen de Acciones Requeridas

1. **Actualizar URLs**: Reemplazar todas las URLs antiguas (`/student-note/list/`, `/attendance/add/`, etc.) por las nuevas URLs RESTful
2. **Cambiar método HTTP**: Las operaciones de listar ahora usan `GET` en lugar de `POST`; eliminar usan `DELETE` en lugar de `POST`; actualizar usan `PATCH` en lugar de `POST`
3. **Mover ID a la URL**: El ID del recurso ahora va en la URL, no en el body de la petición
4. **Agregar paginación**: Las respuestas de listado ahora incluyen `count`, `next`, `previous`, `results`
5. **Manejar 401/403**: Agregar manejo de errores de autenticación y permisos en el frontend
6. **Agregar lógica de login**: Obtener y almacenar el JWT token, enviarlo en todas las peticiones
