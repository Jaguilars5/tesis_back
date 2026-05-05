# Módulo `grading` — Registro de Desempeño y Conducta

Este módulo se encarga del seguimiento integral del estudiante, gestionando sus calificaciones, registros de asistencia e incidentes de conducta.

Su diseño garantiza que las reglas de negocio, como la normalización de notas a base 10 y el cálculo de promedios ponderados, se apliquen de forma consistente mediante una capa de servicios robusta.

---

## Estructura del Módulo

```
grading/
├── models/         # Calificaciones, Asistencia, Conducta
├── repositories/   # Consultas especializadas y filtros
├── services/       # Lógica de normalización y promedios
├── api/            # Serializadores y vistas dinámicas
└── tests/          # Verificación de lógica y cálculos
```

---

## Modelos de Datos

### StudentNote (Nota de Estudiante)
Calificaciones individuales vinculadas a una actividad académica.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `uuid` | UUIDField | UUID |
| `student` | ForeignKey (Student) | Estudiante |
| `academic_activity` | ForeignKey (Academic_Activity) | Actividad Académica |
| `academic_period` | ForeignKey (Academic_Period) | Período Académico |
| `teacher_subject_section` | ForeignKey (Teacher_Subject_Section) | Docente-Materia-Sección |
| `note_value` | DecimalField | Valor de la Nota |
| `normalized_value` | DecimalField | Valor Normalizado |
| `observation` | TextField | Observación |
| `sync_status` | CharField (20) | Estado de Sincronización |
| `synced_at` | DateTimeField | Sincronizado el |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |
| `deleted_at` | DateTimeField | Fecha de Eliminación |
| `sync_version` | PositiveIntegerField | Versión de Sincronización |
| `device_origin` | CharField (40) | Dispositivo de Origen |

---

## Capa de Servicios

### GradingService (Orquestador)

- `create_student_note`: Registra o actualiza la nota de un estudiante para una actividad. Realiza automáticamente la normalización a base 10 basándose en el valor máximo de la actividad.
- `update_student_note`: Modifica una calificación existente y recalcula el valor normalizado si el puntaje numérico ha cambiado.
- `calculate_period_average`: Obtiene el promedio simple de las notas normalizadas de un estudiante para un período y materia específicos.
- `create_attendance`: Registra el estado de asistencia de un alumno (Presente, Ausente, etc.) para una fecha y clase determinada. Si ya existe un registro para ese día, lo actualiza.
- `list_attendance`: Recupera registros de asistencia filtrados por estudiante, sección, fecha o estado.
- `create_conduct_incident`: Documenta un evento disciplinario o académico, asignando una categoría y nivel de gravedad (Leve, Moderado, Grave).
- `list_conduct_incidents`: Lista los incidentes registrados con soporte de filtros por severidad y estado de notificación familiar.
- `deactivate_student_note`: Ejecuta un borrado lógico de una calificación marcándola como inactiva en el sistema.

---

## Endpoints

Todos los endpoints son RESTful con ViewSets de DRF.

### StudentNote

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/grading/student-notes/` | Listar calificaciones (paginado) | grading.view_note |
| POST | `/api/grading/student-notes/` | Crear calificación | grading.create_note |
| GET | `/api/grading/student-notes/{id}/` | Detalle de calificación | grading.view_note |
| PATCH | `/api/grading/student-notes/{id}/` | Actualizar parcialmente | grading.update_note |
| DELETE | `/api/grading/student-notes/{id}/` | Eliminar (soft delete) | grading.delete_note |

### Attendance

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/grading/attendance/` | Listar asistencia (paginado) | grading.view_attendance |
| POST | `/api/grading/attendance/` | Crear registro de asistencia | grading.create_attendance |
| GET | `/api/grading/attendance/{id}/` | Detalle de asistencia | grading.view_attendance |
| PATCH | `/api/grading/attendance/{id}/` | Actualizar parcialmente | grading.update_attendance |
| DELETE | `/api/grading/attendance/{id}/` | Eliminar (soft delete) | grading.delete_attendance |

### ConductIncident

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/grading/conduct-incidents/` | Listar incidentes (paginado) | grading.view_incident |
| POST | `/api/grading/conduct-incidents/` | Crear incidente | grading.create_incident |
| GET | `/api/grading/conduct-incidents/{id}/` | Detalle de incidente | grading.view_incident |
| PATCH | `/api/grading/conduct-incidents/{id}/` | Actualizar parcialmente | grading.update_incident |
| DELETE | `/api/grading/conduct-incidents/{id}/` | Eliminar (soft delete) | grading.delete_incident |

---

## Seguridad

### Autenticación y Permisos

Todos los endpoints requieren:
1. Header `Authorization: Bearer <token>`
2. Permiso específico del usuario

### Permisos por modelo

| Modelo | Ver | Crear | Actualizar | Eliminar |
|--------|-----|-------|------------|----------|
| StudentNote | grading.view_note | grading.create_note | grading.update_note | grading.delete_note |
| Attendance | grading.view_attendance | grading.create_attendance | grading.update_attendance | grading.delete_attendance |
| ConductIncident | grading.view_incident | grading.create_incident | grading.update_incident | grading.delete_incident |

Seedear permisos:
```bash
python manage.py seed_permissions --module grading
```

---

## Pruebas

```
python manage.py test apps.grading
```

---

## Integracion con Analytics

El modulo `grading` funciona como fuente de datos para el modelo de riesgo
academico de `analytics`.

Datos consumidos:

- `StudentNote`: promedio normalizado, ultimo examen y materias reprobadas.
- `Attendance`: porcentaje de asistencia, faltas justificadas, faltas
  injustificadas, tardanzas y maximo de faltas consecutivas.
- `ConductIncident`: faltas leves, moderadas, graves, observaciones recientes
  y notificacion familiar.

Repositorios para snapshots de riesgo:

- `StudentNoteRepository.list_for_risk_snapshot(student_id, academic_period_id)`.
- `AttendanceRepository.list_for_risk_snapshot(student_id, academic_period_id)`.
- `ConductIncidentRepository.list_for_risk_snapshot(student_id, academic_period_id)`.

Estos metodos mantienen las consultas ORM dentro de la capa de repositorios y
permiten que `apps.analytics.services.feature_builder.AcademicRiskFeatureBuilder`
construya el JSON de entrada sin acceder directamente a los modelos.

---

## Lógica de Negocio Clave

1.  **Normalización Interna**: El servicio utiliza `_normalize_note` para asegurar que todas las notas, independientemente de su base original (20, 100, etc.), se almacenen en `normalized_value` con base 10.
2.  **Sincronización**: Los registros incluyen metadatos de sincronización (`sync_status`, `device_origin`) para soportar escenarios de uso en dispositivos móviles con conexión intermitente.
