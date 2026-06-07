# Módulo `attendance` — Gestión de Asistencia, Comportamiento e Incidentes

El módulo `attendance` es responsable de registrar, almacenar y evaluar la asistencia diaria de los estudiantes, sus incidentes conductuales y las evaluaciones cualitativas socioemocionales de la institución. Estos datos sirven de base para alimentar al motor analítico predictivo de alertas tempranas (`analytics`).

---

## 🏛️ Arquitectura del Módulo

El módulo sigue la arquitectura en capas estándar del sistema:

```
attendance/
├── models/         # Modelos de base de datos (Asistencia, Comportamiento, Habilidades)
├── repositories/   # Encapsulamiento de queries ORM con ordenamientos y filtros
├── services/       # Lógica para la agregación conductual del estudiante
├── api/            # Serializadores y ViewSets de Django REST Framework (DRF)
└── tests/          # Cobertura de pruebas unitarias, lógica conductual e integración RBAC
```

---

## 🗃️ Modelos de Datos

### 1. `Attendance` (Registro de Asistencia)

Almacena la asistencia de los estudiantes en clases y períodos académicos específicos.

| Campo                     | Tipo Django     | Relación / Significado                                         |
| :------------------------ | :-------------- | :------------------------------------------------------------- |
| `uuid`                    | `UUIDField`     | Identificador único universal (autogenerado).                  |
| `enrollment`              | `ForeignKey`    | `students.Enrollment` (Matrícula activa).                      |
| `teacher_subject_section` | `ForeignKey`    | `academic.Teacher_Subject_Section` (Clase correspondiente).    |
| `academic_period`         | `ForeignKey`    | `academic.Academic_Period` (Periodo escolar).                  |
| `attendance_status`       | `ForeignKey`    | `attendance.AttendanceStatus` (Presente, Falta, etc.).         |
| `attendance_date`         | `DateField`     | Fecha del registro de asistencia.                              |
| `absence_type`            | `CharField`     | Categoría: `"justified"`, `"unjustified"`, `"late"`, `"none"`. |
| `observation`             | `TextField`     | Justificación o notas adicionales.                             |
| `sync_status`             | `CharField`     | Estado de sincronización del dispositivo (`pending`, etc.).    |
| `synced_at`               | `DateTimeField` | Fecha de sincronización en servidor.                           |

### 2. `AttendanceStatus` (Catálogo de Estados de Asistencia)

Define los estados válidos de asistencia y su clasificación para los cálculos.

| Campo  | Tipo Django      | Relación / Significado                                                 |
| :----- | :--------------- | :--------------------------------------------------------------------- |
| `code` | `CharField(10)`  | Código único del estado (ej: `"P"` para Presente).                     |
| `name` | `CharField(100)` | Nombre descriptivo del estado.                                         |
| `tipo` | `CharField`      | Clasificación: `"POSITIVO"` (Presente) o `"NEGATIVO"` (Falta/Retraso). |

### 3. `IncidentType` (Catálogo de Tipos de Incidente)

Tipificación formal de las faltas conductuales dentro de la institución.

| Campo         | Tipo Django      | Relación / Significado                               |
| :------------ | :--------------- | :--------------------------------------------------- |
| `code`        | `CharField(20)`  | Código de tipificación única (ej: `"INDISCIPLINA"`). |
| `name`        | `CharField(100)` | Nombre común del tipo de falta.                      |
| `description` | `TextField`      | Explicación del tipo de falta.                       |

### 4. `ConductIncident` (Incidente de Conducta)

Registra las faltas disciplinarias o incidentes cometidos por un estudiante.

| Campo              | Tipo Django    | Relación / Significado                                    |
| :----------------- | :------------- | :-------------------------------------------------------- |
| `uuid`             | `UUIDField`    | Identificador único universal (autogenerado).             |
| `enrollment`       | `ForeignKey`   | `students.Enrollment` (Matrícula activa).                 |
| `reported_by_user` | `ForeignKey`   | `accounts.User` (Usuario que reporta la falta).           |
| `academic_period`  | `ForeignKey`   | `academic.Academic_Period` (Periodo correspondiente).     |
| `incident_type`    | `ForeignKey`   | `attendance.IncidentType` (Tipo de incidente).            |
| `incident_date`    | `DateField`    | Fecha de ocurrencia.                                      |
| `severity`         | `IntegerField` | Gravedad de la falta (escala del `1` al `5`).             |
| `description`      | `TextField`    | Detalle textual de lo sucedido.                           |
| `actions_taken`    | `TextField`    | Acciones o correctivos tomados por el docente.            |
| `family_notified`  | `BooleanField` | Indica si los padres fueron notificados (`True`/`False`). |

### 5. `BehaviorEvaluation` (Evaluación de Conducta Periódica)

Consolidación cualitativa del comportamiento del estudiante en un período académico.

| Campo                 | Tipo Django  | Relación / Significado                                              |
| :-------------------- | :----------- | :------------------------------------------------------------------ |
| `enrollment`          | `ForeignKey` | `students.Enrollment` (Matrícula activa).                           |
| `academic_period`     | `ForeignKey` | `academic.Academic_Period` (Periodo evaluado).                      |
| `calculated_scale`    | `ForeignKey` | `grading.QualitativeScale` (Escala estimada por algoritmo).         |
| `final_scale`         | `ForeignKey` | `grading.QualitativeScale` (Escala final asignada por junta/tutor). |
| `general_observation` | `TextField`  | Observaciones conductuales globales.                                |
| `override_reason`     | `TextField`  | Explicación en caso de que la nota final difiera de la estimada.    |

### 6. `SocioemotionalSkill` (Catálogo de Habilidades Socioemocionales)

Habilidades socioemocionales evaluadas periódicamente en los estudiantes.

| Campo         | Tipo Django      | Relación / Significado                          |
| :------------ | :--------------- | :---------------------------------------------- |
| `code`        | `CharField(20)`  | Código único de la habilidad (ej: `"EMPATIA"`). |
| `name`        | `CharField(100)` | Nombre de la habilidad.                         |
| `description` | `TextField`      | Explicación o descriptores de la habilidad.     |
| `active`      | `BooleanField`   | Define si se encuentra activa para evaluar.     |

### 7. `SkillEvaluation` (Evaluación de Habilidad Socioemocional)

Resultados individuales de la evaluación socioemocional del estudiante.

| Campo                  | Tipo Django  | Relación / Significado                                   |
| :--------------------- | :----------- | :------------------------------------------------------- |
| `enrollment`           | `ForeignKey` | `students.Enrollment` (Matrícula activa).                |
| `academic_period`      | `ForeignKey` | `academic.Academic_Period` (Periodo correspondiente).    |
| `socioemotional_skill` | `ForeignKey` | `attendance.SocioemotionalSkill` (Habilidad evaluada).   |
| `qualitative_scale`    | `ForeignKey` | `grading.QualitativeScale` (Nivel cualitativo asignado). |
| `observation`          | `TextField`  | Observaciones sobre el desarrollo de la habilidad.       |

---

## 🚦 Reglas de Negocio: Evaluación de Conducta

El cálculo de la nota cualitativa conductual estimada (`calculated_scale`) del estudiante se realiza en `BehaviorEvaluationService` en base a la gravedad de los incidentes disciplinarios de conducta registrados durante el período escolar:

1.  🥇 **Superior (SE)**: El alumno no tiene ningún incidente de conducta registrado.
2.  🥈 **Satisfactorio (SA)**: El alumno posee únicamente incidentes menores con una gravedad menor a `3`.
3.  🥉 **Aceptable (AC)**: El alumno cuenta con exactamente **un incidente grave** (gravedad mayor o igual a `3`).
4.  🚨 **No Aceptable (NA)**: El alumno cuenta con **múltiples incidentes graves** en el periodo escolar.

---

## 🔌 API Endpoints y Mapeo de Permisos (RBAC)

Todos los endpoints requieren autenticación por token JWT (`Authorization: Bearer <token>`) y validan de manera rigurosa los permisos a nivel de vista a través de la clase `HasPermission`.

| Endpoint REST                            | Método   | Acción DRF | Descripción                        | Permiso Codificado Requerido           |
| :--------------------------------------- | :------- | :--------- | :--------------------------------- | :------------------------------------- |
| `/api/attendance/attendances/`           | `GET`    | `list`     | Listar registros de asistencia     | `attendance.view_attendance`           |
| `/api/attendance/attendances/`           | `POST`   | `create`   | Crear asistencia diaria            | `attendance.create_attendance`         |
| `/api/attendance/attendances/{id}/`      | `PUT`    | `update`   | Actualizar asistencia              | `attendance.update_attendance`         |
| `/api/attendance/attendances/{id}/`      | `DELETE` | `destroy`  | Eliminar asistencia física         | `attendance.delete_attendance`         |
| `/api/attendance/attendance-statuses/`   | `GET`    | `list`     | Listar catálogo de estados         | `attendance.view_attendancestatus`     |
| `/api/attendance/attendance-statuses/`   | `POST`   | `create`   | Registrar nuevo estado             | `attendance.create_attendancestatus`   |
| `/api/attendance/conduct-incidents/`     | `GET`    | `list`     | Listar incidentes                  | `attendance.view_conductincident`      |
| `/api/attendance/conduct-incidents/`     | `POST`   | `create`   | Registrar incidente conductual     | `attendance.create_conductincident`    |
| `/api/attendance/incident-types/`        | `GET`    | `list`     | Listar tipos de incidentes         | `attendance.view_incidenttype`         |
| `/api/attendance/socioemotional-skills/` | `GET`    | `list`     | Listar catálogo de habilidades     | `attendance.view_socioemotionalskill`  |
| `/api/attendance/skill-evaluations/`     | `GET`    | `list`     | Listar evaluaciones de habilidades | `attendance.view_skillevaluation`      |
| `/api/attendance/skill-evaluations/`     | `POST`   | `create`   | Registrar evaluación de habilidad  | `attendance.create_skillevaluation`    |
| `/api/attendance/behavior-evaluations/`  | `GET`    | `list`     | Listar evaluaciones de conducta    | `attendance.view_behaviorevaluation`   |
| `/api/attendance/behavior-evaluations/`  | `POST`   | `create`   | Registrar evaluación conductual    | `attendance.create_behaviorevaluation` |

---

## Formato de Respuestas Enriquecidas

Los serializers del módulo incluyen campos de solo lectura con los nombres relacionados a las ForeignKeys.

| Serializer                     | Campos enriquecidos                                                                                 |
| ------------------------------ | --------------------------------------------------------------------------------------------------- |
| `AttendanceSerializer`         | `enrollment_name`, `teacher_subject_section_name`, `academic_period_name`, `attendance_status_name` |
| `ConductIncidentSerializer`    | `enrollment_name`, `reported_by_user_name`, `academic_period_name`, `incident_type_name`            |
| `SkillEvaluationSerializer`    | `enrollment_name`, `academic_period_name`, `socioemotional_skill_name`, `qualitative_scale_name`    |
| `BehaviorEvaluationSerializer` | `enrollment_name`, `academic_period_name`, `calculated_scale_name`, `final_scale_name`              |

Ejemplo de respuesta en `Attendance`:

```json
{
  "id": 1,
  "enrollment": 5,
  "enrollment_name": "Juan Pérez - 5to EGB A (Activo)",
  "teacher_subject_section": 3,
  "teacher_subject_section_name": "jperez@email.com - 2024-2025 - 5to EGB A - Matemáticas",
  "academic_period": 1,
  "academic_period_name": "Primer Trimestre",
  "attendance_status": 1,
  "attendance_status_name": "Presente",
  "attendance_date": "2024-10-15"
}
```

---

## 🧪 Pruebas del Módulo

Para ejecutar la suite completa de pruebas del módulo (incluyendo las pruebas de conducta y las de seguridad de la API), use el siguiente comando:

```bash
python manage.py test apps.attendance --settings=config.settings.test
```
