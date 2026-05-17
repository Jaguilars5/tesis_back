# Módulo `grading` — Registro de Desempeño y Conducta

Este módulo se encarga del seguimiento integral del estudiante, gestionando calificaciones, asistencia e incidentes de conducta.

Su diseño garantiza que las reglas de negocio se apliquen de forma consistente mediante una capa de servicios.

---

## Estructura del Módulo

```
grading/
├── models/         # Calificaciones, Asistencia, Conducta
├── repositories/   # Consultas especializadas
├── services/       # Lógica de normalización y promedios
├── api/            # Serializadores y ViewSets
└── tests/          # Verificación de lógica
```

---

## Modelos de Datos

### AttendanceStatus (Estado de Asistencia)
Catálogo de estados (Presente, Ausente, Tardanza, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | CharField (10) | Código único |
| `name` | CharField (100) | Nombre |

### GradeType (Tipo de Nota)
Catálogo de tipos de evaluación (Examen, Tarea, Proyecto, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | CharField (20) | Código único |
| `name` | CharField (100) | Nombre |

### QualitativeScale (Escala Cualitativa)
Equivalencias entre escalas cualitativas y numéricas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | CharField (10) | Código único |
| `description` | CharField (100) | Descripción |
| `numeric_equivalence` | DecimalField | Equivalencia numérica |

### EvaluationMacro (Macro Evaluación)
Grupo principal de evaluación (Ej: "Examen Final").

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `academic_period` | ForeignKey (Academic_Period) | Período académico |
| `name` | CharField (100) | Nombre |
| `weight_percentage` | DecimalField | Peso porcentual |
| `active` | BooleanField | Activo |

### EvaluationCriteria (Criterio de Evaluación)
Subdivisión de una macro evaluación.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `evaluation_macro` | ForeignKey (EvaluationMacro) | Macro evaluación |
| `name` | CharField (100) | Nombre |
| `internal_weight` | DecimalField | Peso interno (%) |

### EvaluationSubcriteria (Subcriterio de Evaluación)
细分 más granular de un criterio.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `evaluation_criteria` | ForeignKey (EvaluationCriteria) | Criterio |
| `name` | CharField (100) | Nombre |
| `internal_weight` | DecimalField | Peso interno (%) |

### ClassAssignment (Tarea/Actividad)
Actividades evaluativas específicas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `evaluation_subcriteria` | ForeignKey (EvaluationSubcriteria) | Subcriterio |
| `teacher_subject_section` | ForeignKey (Teacher_Subject_Section) | Asignación docente |
| `title` | CharField (200) | Título |
| `max_score` | DecimalField | Puntaje máximo |
| `due_date` | DateField | Fecha de entrega |

### StudentNote (Nota de Estudiante)
Calificaciones individuales vinculadas a una actividad.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `uuid` | UUIDField | UUID único |
| `enrollment` | ForeignKey (Enrollment) | Matrícula |
| `class_assignment` | ForeignKey (ClassAssignment) | Actividad |
| `grade_type` | ForeignKey (GradeType) | Tipo de nota |
| `qualitative_scale` | ForeignKey (QualitativeScale) | Escala cualitativa |
| `numeric_score` | DecimalField | Nota numérica |
| `manually_overridden` | BooleanField | Modificado manualmente |
| `teacher_observation` | TextField | Observación del docente |
| `administrative_observation` | TextField | Observación administrativa |
| `sync_status` | CharField (20) | Estado de sincronización |
| `synced_at` | DateTimeField | Sincronizado el |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Fecha de actualización |
| `deleted_at` | DateTimeField | Fecha de eliminación |
| `sync_version` | PositiveIntegerField | Versión de sincronización |
| `device_origin` | CharField (40) | Dispositivo de origen |

### Attendance (Asistencia)
Registros de asistencia por clase.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `uuid` | UUIDField | UUID único |
| `enrollment` | ForeignKey (Enrollment) | Matrícula |
| `teacher_subject_section` | ForeignKey (Teacher_Subject_Section) | Clase |
| `academic_period` | ForeignKey (Academic_Period) | Período académico |
| `attendance_status` | ForeignKey (AttendanceStatus) | Estado |
| `attendance_date` | DateField | Fecha |
| `observation` | TextField | Observación |
| `sync_status` | CharField (20) | Estado de sincronización |
| `synced_at` | DateTimeField | Sincronizado el |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Fecha de actualización |
| `sync_version` | PositiveIntegerField | Versión de sincronización |
| `device_origin` | CharField (40) | Dispositivo de origen |

### ConductIncident (Incidente de Conducta)
Registros disciplinarios.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `uuid` | UUIDField | UUID único |
| `enrollment` | ForeignKey (Enrollment) | Matrícula |
| `reported_by_user` | ForeignKey (User) | Reportado por |
| `academic_period` | ForeignKey (Academic_Period) | Período académico |
| `incident_date` | DateField | Fecha del incidente |
| `category` | CharField (30) | Categoría |
| `severity` | IntegerField | Gravedad |
| `description` | TextField | Descripción |
| `family_notified` | BooleanField | Familia notificada |
| `sync_status` | CharField (20) | Estado de sincronización |
| `synced_at` | DateTimeField | Sincronizado el |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Fecha de actualización |
| `sync_version` | PositiveIntegerField | Versión de sincronización |
| `device_origin` | CharField (40) | Dispositivo de origen |

### BehaviorEvaluation (Evaluación de Conducta)
Evaluación conductual por período.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `enrollment` | ForeignKey (Enrollment) | Matrícula |
| `academic_period` | ForeignKey (Academic_Period) | Período académico |
| `calculated_scale` | ForeignKey (QualitativeScale) | Escala calculada |
| `final_scale` | ForeignKey (QualitativeScale) | Escala final (override) |
| `override_reason` | TextField | Razón del override |

### GradeChangeHistory (Historial de Cambio de Nota)
Auditoría de cambios de calificaciones.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student_note` | ForeignKey (StudentNote) | Nota |
| `modified_by_user` | ForeignKey (User) | Modificado por |
| `previous_score` | DecimalField | Nota anterior |
| `new_score` | DecimalField | Nota nueva |
| `reason` | TextField | Razón del cambio |
| `modified_at` | DateTimeField | Fecha de modificación |

---

## API REST (Resumen)

### Calificaciones
- GET/POST `/api/grading/student-notes/`
- GET/PUT/PATCH/DELETE `/api/grading/student-notes/{id}/`

### Asistencia
- GET/POST `/api/grading/attendance/`
- GET/PUT/PATCH/DELETE `/api/grading/attendance/{id}/`

### Incidentes de Conducta
- GET/POST `/api/grading/conduct-incidents/`
- GET/PUT/PATCH/DELETE `/api/grading/conduct-incidents/{id}/`

### Catálogos
- GET/POST `/api/grading/attendance-status/`
- GET/POST `/api/grading/grade-type/`
- GET/POST `/api/grading/qualitative-scale/`
- GET/POST `/api/grading/evaluation-macro/`
- GET/POST `/api/grading/evaluation-criteria/`
- GET/POST `/api/grading/evaluation-subcriteria/`
- GET/POST `/api/grading/class-assignment/`

### Evaluaciones de Conducta
- GET/POST `/api/grading/behavior-evaluation/`

---

## Seguridad

Todos los endpoints requieren `Authorization: Bearer <token>` y permiso específico.

| Modelo | View | Create | Update | Delete |
|--------|------|--------|--------|--------|
| StudentNote | `grading.view_note` | `grading.create_note` | `grading.update_note` | `grading.delete_note` |
| Attendance | `grading.view_attendance` | `grading.create_attendance` | `grading.update_attendance` | `grading.delete_attendance` |
| ConductIncident | `grading.view_incident` | `grading.create_incident` | `grading.update_incident` | `grading.delete_incident` |
| EvaluationMacro | `grading.view_macro` | `grading.create_macro` | `grading.update_macro` | `grading.delete_macro` |
| ClassAssignment | `grading.view_assignment` | `grading.create_assignment` | `grading.update_assignment` | `grading.delete_assignment` |

Seedear permisos:
```bash
python manage.py seed_permissions --module grading
```

---

## Pruebas

```bash
python manage.py test apps.grading --settings=config.settings.test
```

---

## Integración con Analytics

El módulo `grading` funciona como fuente de datos para el modelo de riesgo académico de `analytics`.

Datos consumidos:
- `StudentNote`: promedio normalizado, materias reprobadas
- `Attendance`: tasa de asistencia, faltas consecutivas, tardanzas
- `ConductIncident`: incidentes por severidad, notificación familiar

Repositorios para snapshots de riesgo:
- `StudentNoteRepository.list_for_risk_snapshot(student_id, academic_period_id)`
- `AttendanceRepository.list_for_risk_snapshot(student_id, academic_period_id)`
- `ConductIncidentRepository.list_for_risk_snapshot(student_id, academic_period_id)`