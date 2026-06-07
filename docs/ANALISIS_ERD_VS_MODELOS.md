# Análisis de Inconsistencias: ERD vs Modelos Django

> **Fecha:** 29 de mayo de 2026
> **Proyecto:** SIGAE — Sistema de Gestión Académica (Modelo Ecuador 2025-2026)
> **Base:** Diagrama ERD (`docs/bd_en.html`) vs Modelos Django Actuales

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Metodología](#2-metodología)
3. [Inventario de Modelos Actuales](#3-inventario-de-modelos-actuales)
4. [Modelos del ERD Faltantes (10)](#4-modelos-del-erd-faltantes-10)
5. [Campos Faltantes en Modelos Existentes](#5-campos-faltantes-en-modelos-existentes)
6. [Inconsistencias en Analytics](#6-inconsistencias-en-analytics)
7. [Discrepancias Menores](#7-discrepancias-menores)
8. [Violaciones a Principios SOLID](#8-violaciones-a-principios-solid)
9. [Propuesta de Reestructuración: Árbol Ideal](#9-propuesta-de-reestructuración-árbol-ideal)
10. [Agrupación de Modelos por App (SRP + DDD)](#10-agrupación-de-modelos-por-app-srp--ddd)
11. [Mapa de Migración de Modelos](#11-mapa-de-migración-de-modelos)
12. [Plan de Implementación por Fases](#12-plan-de-implementación-por-fases)

---

## 1. Resumen Ejecutivo

Se realizó una comparación exhaustiva entre el diagrama entidad-relación (ERD) definido en `docs/bd_en.html` y los **48 modelos Django** existentes en el proyecto. Se identificaron:

| Tipo de Hallazgo                       | Cantidad          | Severidad  |
| -------------------------------------- | ----------------- | ---------- |
| Modelos completos faltantes            | 10                | 🔴 Crítico |
| Campos faltantes en modelos existentes | ~21               | 🟡 Medio   |
| FK apuntando a entidad incorrecta      | 2                 | 🟡 Medio   |
| Violaciones SRP en modularización      | 1 (app `grading`) | 🟡 Medio   |
| Discrepancias de nomenclatura          | 3                 | ⚪ Leve    |

---

## 2. Metodología

1. **Extracción de entidades ERD**: Se analizó el diagrama Mermaid en `docs/bd_en.html`, identificando las ~40 entidades con sus atributos y relaciones.
2. **Inventario de modelos Django**: Se exploraron las 8 apps del proyecto (`core`, `accounts`, `academic`, `grading`, `institutions`, `scheduling`, `students`, `analytics`) y se listaron los 48 modelos con todos sus campos.
3. **Mapeo ERD → Modelos**: Cada entidad del ERD se comparó contra su modelo Django correspondiente, verificando:
   - Existencia del modelo
   - Coincidencia de campos (nombre y tipo)
   - Correctitud de relaciones (FKs)
   - Exportación en `__init__.py`
4. **Análisis de arquitectura**: Se evaluó la adherencia a SRP (Single Responsibility Principle) y la arquitectura en capas.

---

## 3. Inventario de Modelos Actuales

### 3.1. `apps.core` (1 modelo)

| Modelo         | Archivo            | Descripción                                       |
| -------------- | ------------------ | ------------------------------------------------- |
| `SystemConfig` | `system_config.py` | CONFIG_SISTEMA — Configuración global clave-valor |

### 3.2. `apps.institutions` (6 modelos)

| Modelo          | Archivo             | Entidad ERD         |
| --------------- | ------------------- | ------------------- |
| `School_Year`   | `school_year.py`    | ANNO_ESCOLAR ✅     |
| `AcademicLevel` | `academic_level.py` | NIVEL_ACADEMICO ✅  |
| `AcademicGrade` | `academic_grade.py` | GRADO_ACADEMICO ✅  |
| `DocumentType`  | `document_type.py`  | TIPO_DOCUMENTO ✅   |
| `Classroom`     | `classroom.py`      | — (gestión interna) |
| `RoomType`      | `room_type.py`      | — (gestión interna) |

### 3.3. `apps.academic` (6 modelos)

| Modelo                    | Archivo                      | Entidad ERD                 |
| ------------------------- | ---------------------------- | --------------------------- |
| `Section`                 | `section.py`                 | PARALELO ✅                 |
| `Subject`                 | `subject.py`                 | ASIGNATURA ✅               |
| `Academic_Period`         | `academic_period.py`         | PERIODO_ACADEMICO ✅        |
| `SubjectAcademicConfig`   | `subject_academic_config.py` | CONFIGURACION_ASIGNATURA ✅ |
| `SubjectOffering`         | `subject_offering.py`        | OFERTA_ASIGNATURA ✅        |
| `Teacher_Subject_Section` | `teacher_subject_section.py` | ASIGNACION_DOCENTE ✅       |

### 3.4. `apps.accounts` (6 modelos)

| Modelo           | Archivo              | Entidad ERD    |
| ---------------- | -------------------- | -------------- |
| `Person`         | `person.py`          | PERSONA ✅     |
| `User`           | `user.py`            | USUARIO ✅     |
| `Role`           | `role.py`            | ROL ✅         |
| `Permission`     | `permission.py`      | PERMISO ✅     |
| `UserRole`       | `user_role.py`       | USUARIO_ROL ✅ |
| `RolePermission` | `role_permission.py` | ROL_PERMISO ✅ |

### 3.5. `apps.students` (4 modelos)

| Modelo                   | Archivo                     | Entidad ERD          |
| ------------------------ | --------------------------- | -------------------- |
| `Student`                | `student.py`                | PERFIL_ESTUDIANTE ✅ |
| `Student_Representative` | `student_representative.py` | VINCULO_FAMILIAR ✅  |
| `Enrollment`             | `enrollment.py`             | MATRICULA ✅         |
| `EnrollmentStatus`       | `enrollment_status.py`      | ESTADO_MATRICULA ✅  |

### 3.6. `apps.grading` (12 modelos)

| Modelo                  | Archivo                     | Entidad ERD                                 |
| ----------------------- | --------------------------- | ------------------------------------------- |
| `EvaluationMacro`       | `evaluation_macro.py`       | BLOQUE_EVALUACION ✅                        |
| `EvaluationCriteria`    | `evaluation_criteria.py`    | COMPONENTE_BLOQUE ✅                        |
| `EvaluationSubcriteria` | `evaluation_subcriteria.py` | INDICADOR_COMPONENTE ✅                     |
| `ClassAssignment`       | `class_assignment.py`       | ACTIVIDAD_EVALUATIVA ✅                     |
| `GradeType`             | `grade_type.py`             | TIPO_CALIFICACION ✅                        |
| `QualitativeScale`      | `qualitative_scale.py`      | ESCALA_CUALITATIVA ✅                       |
| `StudentNote`           | `student_note.py`           | NOTA_ACTIVIDAD ✅                           |
| `GradeChangeHistory`    | `grade_change_history.py`   | AUDITORIA_NOTA ✅                           |
| `Attendance`            | `attendance.py`             | REGISTRO_ASISTENCIA ⚠️ (app incorrecta)     |
| `AttendanceStatus`      | `attendance_status.py`      | ESTADO_ASISTENCIA ⚠️ (app incorrecta)       |
| `ConductIncident`       | `conduct_incident.py`       | INCIDENTE_DISCIPLINARIO ⚠️ (app incorrecta) |
| `BehaviorEvaluation`    | `behavior_evaluation.py`    | RESUMEN_COMPORTAMIENTO ⚠️ (app incorrecta)  |

### 3.7. `apps.analytics` (4 modelos)

| Modelo                   | Archivo                       | Entidad ERD                             |
| ------------------------ | ----------------------------- | --------------------------------------- |
| `RiskFactor`             | `risk_factor.py`              | FACTOR_RIESGO ✅                        |
| `StudentFeatureSnapshot` | `student_feature_snapshot.py` | SNAPSHOT_FEATURES_ML ⚠️ (FK incorrecto) |
| `StudentRiskScore`       | `student_risk_score.py`       | PREDICCION_DESERCION ⚠️ (FK incorrecto) |
| `StudentRiskFactor`      | `student_risk_factor.py`      | DETALLE_FACTOR_PREDICCION ✅            |

### 3.8. `apps.scheduling` (5 modelos)

| Modelo                   | Archivo                       | Entidad ERD         |
| ------------------------ | ----------------------------- | ------------------- |
| `ScheduleSlot`           | `schedule_slot.py`            | — (gestión interna) |
| `ScheduleTemplateConfig` | `schedule_template_config.py` | — (gestión interna) |
| `SubjectConstraint`      | `subject_constraint.py`       | — (gestión interna) |
| `TeacherAvailability`    | `teacher_availability.py`     | — (gestión interna) |
| `TimeSlot`               | `time_slot.py`                | — (gestión interna) |

**Total: 48 modelos**

---

## 4. Modelos del ERD Faltantes (10)

Estas entidades existen en el ERD pero **no tienen modelo Django** implementado.

| #   | Entidad ERD                    | Modelo Sugerido            | App Destino     | Descripción                                   |
| --- | ------------------------------ | -------------------------- | --------------- | --------------------------------------------- |
| 1   | `TIPO_INCIDENTE`               | `IncidentType`             | `attendance` 🆕 | Catálogo de tipos de incidente disciplinario  |
| 2   | `HABILIDAD_SOCIOEMOCIONAL`     | `SocioemotionalSkill`      | `attendance` 🆕 | Catálogo de habilidades socioemocionales      |
| 3   | `EVALUACION_HABILIDAD`         | `SkillEvaluation`          | `attendance` 🆕 | Evaluación de habilidades por estudiante      |
| 4   | `PROYECTO_INTERDISCIPLINAR`    | `InterdisciplinaryProject` | `academic`      | Proyectos interdisciplinarios                 |
| 5   | `PROYECTO_ASIGNATURA`          | `SubjectProject`           | `academic`      | Tabla intermedia proyecto ↔ oferta_asignatura |
| 6   | `NOTA_PROYECTO`                | `ProjectNote`              | `grading`       | Calificaciones de proyectos                   |
| 7   | `EVALUACION_DIAGNOSTICA`       | `DiagnosticEvaluation`     | `grading`       | Evaluación socioemocional diagnóstica         |
| 8   | `PROCESO_RECUPERACION`         | `RecoveryProcess`          | `grading`       | Procesos de recuperación académica            |
| 9   | `RESUMEN_CALIFICACION_PERIODO` | `PeriodGradeSummary`       | `grading`       | Resumen de calificaciones por periodo         |
| 10  | `ALERTA_TEMPRANA`              | `EarlyAlert`               | `analytics`     | Alertas tempranas de deserción                |

Además, el modelo `COLA_SINCRONIZACION` (`SyncQueue`) debería crearse en `core` como parte de la infraestructura de sincronización offline.

### 4.1. Detalle de Campos para Nuevos Modelos

#### `IncidentType` (TIPO_INCIDENTE)

```
code:          CharField(unique=True)  → código corto (ej: "BULLYING")
name:          CharField               → nombre descriptivo
description:   TextField(null=True)    → descripción detallada
```

#### `SocioemotionalSkill` (HABILIDAD_SOCIOEMOCIONAL)

```
code:          CharField(unique=True)  → código corto
name:          CharField               → nombre de la habilidad
description:   TextField(null=True)    → descripción
active:        BooleanField(default=True)
```

#### `SkillEvaluation` (EVALUACION_HABILIDAD)

```
enrollment:             FK → Enrollment
academic_period:        FK → Academic_Period
socioemotional_skill:   FK → SocioemotionalSkill
qualitative_scale:      FK → QualitativeScale
observation:            TextField(null=True)
evaluation_date:        DateTimeField(auto_now_add=True)
```

#### `InterdisciplinaryProject` (PROYECTO_INTERDISCIPLINAR)

```
academic_period:    FK → Academic_Period
title:              CharField(max_length=200)
description:        TextField(null=True)
start_date:         DateField
delivery_date:      DateField
active:             BooleanField(default=True)
```

#### `SubjectProject` (PROYECTO_ASIGNATURA)

```
interdisciplinary_project:  FK → InterdisciplinaryProject
subject_offering:           FK → SubjectOffering

Meta: unique_together = ("interdisciplinary_project", "subject_offering")
```

#### `ProjectNote` (NOTA_PROYECTO)

```
uuid:               UUIDField(unique=True, default=uuid4)
enrollment:         FK → Enrollment
interdisciplinary_project:  FK → InterdisciplinaryProject
product_score:      DecimalField(max_digits=5, decimal_places=2)
presentation_score: DecimalField(max_digits=5, decimal_places=2)
final_score:        DecimalField(max_digits=5, decimal_places=2)
observation:        TextField(null=True)
sync_status:        CharField(max_length=20, default="pending")
synced_at:          DateTimeField(null=True)
created_at:         DateTimeField(auto_now_add=True)
sync_version:       PositiveIntegerField(default=0)
device_origin:      CharField(max_length=40, null=True)
```

#### `PeriodGradeSummary` (RESUMEN_CALIFICACION_PERIODO)

```
enrollment:                FK → Enrollment
subject_offering:          FK → SubjectOffering
academic_period:           FK → Academic_Period
formative_avg:             DecimalField(max_digits=5, decimal_places=2)
summative_avg:             DecimalField(max_digits=5, decimal_places=2)
final_avg_truncated:       DecimalField(max_digits=5, decimal_places=2)
qualitative_scale:         FK → QualitativeScale (null=True)
requires_recovery:         BooleanField(default=False)
promotion_status:          CharField(max_length=20, null=True)
calculated_at:             DateTimeField(auto_now_add=True)

Meta: unique_together = ("enrollment", "subject_offering", "academic_period")
```

#### `RecoveryProcess` (PROCESO_RECUPERACION)

```
period_grade_summary:     FK → PeriodGradeSummary
managed_by_user:          FK → User
process_type:             CharField(max_length=30)
initial_grade:            DecimalField(max_digits=5, decimal_places=2)
reinforcement_grade:      DecimalField(max_digits=5, decimal_places=2, null=True)
improvement_eval_grade:  DecimalField(max_digits=5, decimal_places=2, null=True)
final_calculated_grade:   DecimalField(max_digits=5, decimal_places=2, null=True)
family_notified:          BooleanField(default=False)
start_date:               DateField
end_date:                 DateField(null=True)
observations:             TextField(null=True)
```

#### `DiagnosticEvaluation` (EVALUACION_DIAGNOSTICA)

```
enrollment:              FK → Enrollment
academic_period:         FK → Academic_Period
applied_by_user:         FK → User
socioemotional_area:     CharField(max_length=100)
findings_description:    TextField()
development_level:       CharField(max_length=50)
application_date:        DateField
recommendations:         TextField(null=True)
```

#### `EarlyAlert` (ALERTA_TEMPRANA)

```
enrollment:              FK → Enrollment
academic_period:         FK → Academic_Period
alert_type:              CharField(max_length=50)
description:             TextField()
urgency_level:           CharField(max_length=20)
attended:                BooleanField(default=False)
attended_by_user:        FK → User (null=True)
detected_at:             DateTimeField(auto_now_add=True)
attended_at:             DateTimeField(null=True)
response_actions:        TextField(null=True)
```

#### `SyncQueue` (COLA_SINCRONIZACION)

```
uuid:           UUIDField(unique=True, default=uuid4)
user:           FK → User
source_table:   CharField(max_length=100)
record_uuid:    UUIDField()
operation:      CharField(max_length=20)  → "create", "update", "delete"
payload:        JSONField()
attempts:       IntegerField(default=0)
last_error:     TextField(null=True)
status:         CharField(max_length=20, default="pending")
created_at:     DateTimeField(auto_now_add=True)
processed_at:   DateTimeField(null=True)
```

---

## 5. Campos Faltantes en Modelos Existentes

### 5.1. `Enrollment` (MATRICULA) — `apps/students/models/enrollment.py`

**3 campos faltantes + 1 campo extra**

| Campo ERD                                           | Tipo ERD          | Estado          | Tipo Sugerido                              |
| --------------------------------------------------- | ----------------- | --------------- | ------------------------------------------ |
| `school_year` (anno_escolar_id)                     | FK → ANNO_ESCOLAR | ❌ **Faltante** | `FK → School_Year`                         |
| `is_repeat` (es_repitente)                          | Boolean           | ❌ **Faltante** | `BooleanField(default=False)`              |
| `repeated_school_year` (anno_escolar_repitencia_id) | FK → ANNO_ESCOLAR | ❌ **Faltante** | `FK → School_Year (null=True)`             |
| `final_status`                                      | —                 | ⚠️ **Extra**    | No está en ERD, campo adicional del modelo |

### 5.2. `Student` (PERFIL_ESTUDIANTE) — `apps/students/models/student.py`

**2 campos faltantes**

| Campo ERD                       | Tipo ERD | Estado          | Tipo Sugerido                                      |
| ------------------------------- | -------- | --------------- | -------------------------------------------------- |
| `has_special_needs` (tiene_nee) | Boolean  | ❌ **Faltante** | `BooleanField(default=False)`                      |
| `special_needs_type` (tipo_nee) | String   | ❌ **Faltante** | `CharField(max_length=100, null=True, blank=True)` |

### 5.3. `Academic_Period` (PERIODO_ACADEMICO) — `apps/academic/models/academic_period.py`

**1 campo faltante**

| Campo ERD                    | Tipo ERD | Estado          | Tipo Sugerido              |
| ---------------------------- | -------- | --------------- | -------------------------- |
| `period_type` (tipo_periodo) | String   | ❌ **Faltante** | `CharField(max_length=50)` |

### 5.4. `Attendance` (REGISTRO_ASISTENCIA) — `apps/grading/models/attendance.py`

**1 campo faltante**

| Campo ERD                      | Tipo ERD | Estado          | Tipo Sugerido                                     |
| ------------------------------ | -------- | --------------- | ------------------------------------------------- |
| `absence_type` (tipo_ausencia) | String   | ❌ **Faltante** | `CharField(max_length=30, null=True, blank=True)` |

### 5.5. `ConductIncident` (INCIDENTE_DISCIPLINARIO) — `apps/grading/models/conduct_incident.py`

**2 campos problemáticos**

| Aspecto ERD                               | Estado Actual                         | Problema                     | Solución                                       |
| ----------------------------------------- | ------------------------------------- | ---------------------------- | ---------------------------------------------- |
| `tipo_incidente_id` → FK a TIPO_INCIDENTE | `category = CharField(max_length=30)` | ❌ Debería ser FK a catálogo | Reemplazar por `FK → IncidentType`             |
| `acciones_tomadas` (TextField)            | ❌ No existe                          | Campo faltante               | Agregar `actions_taken = TextField(null=True)` |

### 5.6. `BehaviorEvaluation` (RESUMEN_COMPORTAMIENTO_PERIODO) — `apps/grading/models/behavior_evaluation.py`

**1 campo faltante**

| Campo ERD                                   | Tipo ERD | Estado                            | Tipo Sugerido                                |
| ------------------------------------------- | -------- | --------------------------------- | -------------------------------------------- |
| `observacion_general` (general_observation) | Text     | ❌ **Faltante**                   | `general_observation = TextField(null=True)` |
| `razon_anulacion` (override_reason)         | Text     | ✅ Mapeado como `override_reason` | —                                            |

---

## 6. Inconsistencias en Analytics

### 6.1. `StudentFeatureSnapshot` — FK incorrecto + 10 campos faltantes

#### FK Principal

| ERD                             | Actual                     | Problema                                          |
| ------------------------------- | -------------------------- | ------------------------------------------------- |
| `matricula_id` → FK a MATRICULA | `student` → FK a `Student` | ❌ Debería apuntar a `Enrollment`, no a `Student` |

#### Campos Faltantes (vs `SNAPSHOT_FEATURES_ML` del ERD)

| Campo ERD                                                   | Tipo      | Estado                                              |
| ----------------------------------------------------------- | --------- | --------------------------------------------------- |
| `justified_absences` (ausencias_justificadas)               | Integer   | ❌ Faltante                                         |
| `unjustified_absences` (ausencias_injustificadas)           | Integer   | ❌ Faltante                                         |
| `formative_avg_normalized` (promedio_formativo_normalizado) | Decimal   | ❌ Consolidado en `avg_grade_normalized`            |
| `summative_avg_normalized` (promedio_sumativo_normalizado)  | Decimal   | ❌ No existe separado                               |
| `severe_incidents_count` (cantidad_incidentes_graves)       | Integer   | ❌ Faltante                                         |
| `is_repeat` (es_repitente)                                  | Boolean   | ❌ Faltante                                         |
| `has_special_needs` (tiene_nee)                             | Boolean   | ❌ Faltante                                         |
| `residential_zone` (zona_residencia)                        | CharField | ❌ Faltante (existe en Student pero no en snapshot) |
| `distance_to_school_km` (distancia_institucion_km)          | Decimal   | ❌ Faltante (existe en Student pero no en snapshot) |
| `active_alerts` (alertas_activas)                           | Integer   | ❌ Faltante                                         |

### 6.2. `StudentRiskScore` — FK incorrecto

| ERD                             | Actual                     | Problema                          |
| ------------------------------- | -------------------------- | --------------------------------- |
| `matricula_id` → FK a MATRICULA | `student` → FK a `Student` | ⚠️ Debería apuntar a `Enrollment` |

---

## 7. Discrepancias Menores

| Entidad ERD                   | Modelo Actual                       | Diferencia                                                              | Severidad |
| ----------------------------- | ----------------------------------- | ----------------------------------------------------------------------- | --------- |
| `PARALELO.letra` (1 carácter) | `Section.parallel` (max_length=255) | ⚪ ERD sugiere 1 char (letra A, B, C...), el modelo permite texto largo | Baja      |
| `AUDITORIA_NOTA`              | `GradeChangeHistory`                | ⚪ Nombre diferente, funcionalidad equivalente ✅                       | Muy baja  |
| `MATRICULA` → `ANNO_ESCOLAR`  | Relación indirecta vía `Section`    | ⚪ El ERD muestra relación directa, el código la deriva                 | Baja      |

---

## 8. Violaciones a Principios SOLID

### 8.1. S — Single Responsibility Principle (SRP)

La app `grading` actualmente viola SRP porque maneja **múltiples responsabilidades no relacionadas**:

| Responsabilidad           | Modelos                                                    | ¿Debe estar aquí? |
| ------------------------- | ---------------------------------------------------------- | :---------------: |
| Estructura de evaluación  | EvaluationMacro, EvaluationCriteria, EvaluationSubcriteria |        ✅         |
| Calificaciones            | StudentNote, GradeType, QualitativeScale, ClassAssignment  |        ✅         |
| Auditoría de notas        | GradeChangeHistory                                         |        ✅         |
| **Asistencia**            | Attendance, AttendanceStatus                               |        ❌         |
| **Conducta/Incidentes**   | ConductIncident                                            |        ❌         |
| **Evaluación conductual** | BehaviorEvaluation                                         |        ❌         |

**Solución:** Extraer los modelos de asistencia, conducta y comportamiento a una nueva app `attendance`.

### 8.2. O — Open/Closed Principle

La arquitectura en capas (models → repositories → services → api) está bien diseñada para cumplir OCP:

- Los servicios pueden extenderse sin modificar los modelos
- Los repositorios abstraen las consultas ORM

### 8.3. D — Dependency Inversion Principle

La dependencia actual es correcta:

```
Models ← Repositories ← Services ← API
```

Cada capa depende de abstracciones de la capa inferior.

### 8.4. Violación adicional: Acoplamiento en `grading`

Actualmente `grading` contiene 12 modelos. Al extraer `attendance`:

- `grading` → se reduce a **8 modelos** (SRP cumplido)
- `attendance` → nueva app con **7 modelos** (SRP cumplido)

---

## 9. Propuesta de Reestructuración: Árbol Ideal

La reestructuración propuesta organiza el proyecto en **9 apps** (vs 8 actuales), aplicando SRP y DDD.

```
back/
├── apps/
│   ├── core/                          # 🏛️ Infraestructura compartida
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── system_config.py       # CONFIG_SISTEMA ✓
│   │   │   └── sync_queue.py          # COLA_SINCRONIZACION 🆕
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   ├── constants/                 # permisos tipados
│   │   ├── exceptions.py
│   │   ├── middleware.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── renderers.py
│   │   ├── schema.py
│   │   └── utils/
│   │
│   ├── institutions/                  # 🏫 Estructura institucional
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document_type.py       # TIPO_DOCUMENTO ✓
│   │   │   ├── school_year.py         # ANNO_ESCOLAR ✓
│   │   │   ├── academic_level.py      # NIVEL_ACADEMICO ✓
│   │   │   ├── academic_grade.py      # GRADO_ACADEMICO ✓
│   │   │   ├── section.py             # PARALELO ◀️ desde academic
│   │   │   ├── classroom.py           # ✓ (gestión interna)
│   │   │   └── room_type.py           # ✓ (gestión interna)
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   ├── academic/                      # 📚 Núcleo académico
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── subject.py             # ASIGNATURA ✓
│   │   │   ├── subject_academic_config.py  # CONFIG_ASIGNATURA ✓
│   │   │   ├── subject_offering.py    # OFERTA_ASIGNATURA ✓
│   │   │   ├── academic_period.py     # PERIODO_ACADEMICO ✓ (agregar period_type)
│   │   │   ├── teacher_subject_section.py  # ASIGNACION_DOCENTE ✓
│   │   │   ├── interdisciplinary_project.py  # PROYECTO_INTERDISCIPLINAR 🆕
│   │   │   └── subject_project.py     # PROYECTO_ASIGNATURA 🆕
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   ├── accounts/                      # 👤 Personas y seguridad
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── person.py             # PERSONA ✓
│   │   │   ├── user.py               # USUARIO ✓
│   │   │   ├── role.py               # ROL ✓
│   │   │   ├── permission.py         # PERMISO ✓
│   │   │   ├── user_role.py          # USUARIO_ROL ✓
│   │   │   └── role_permission.py    # ROL_PERMISO ✓
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   ├── students/                      # 🎓 Perfiles estudiantiles y matrículas
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── student.py            # PERFIL_ESTUDIANTE ✓ (agregar campos)
│   │   │   ├── student_representative.py  # VINCULO_FAMILIAR ✓
│   │   │   ├── enrollment.py         # MATRICULA ✓ (agregar campos)
│   │   │   └── enrollment_status.py  # ESTADO_MATRICULA ✓
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   ├── grading/                       # 📝 Evaluaciones y calificaciones
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── evaluation_macro.py       # BLOQUE_EVALUACION ✓
│   │   │   ├── evaluation_criteria.py    # COMPONENTE_BLOQUE ✓
│   │   │   ├── evaluation_subcriteria.py # INDICADOR_COMPONENTE ✓
│   │   │   ├── class_assignment.py       # ACTIVIDAD_EVALUATIVA ✓
│   │   │   ├── grade_type.py             # TIPO_CALIFICACION ✓
│   │   │   ├── qualitative_scale.py      # ESCALA_CUALITATIVA ✓
│   │   │   ├── student_note.py           # NOTA_ACTIVIDAD ✓
│   │   │   ├── grade_change_history.py   # AUDITORIA_NOTA ✓
│   │   │   ├── period_grade_summary.py   # RESUMEN_CALIFICACION_PERIODO 🆕
│   │   │   ├── recovery_process.py       # PROCESO_RECUPERACION 🆕
│   │   │   ├── diagnostic_evaluation.py  # EVALUACION_DIAGNOSTICA 🆕
│   │   │   └── project_note.py           # NOTA_PROYECTO 🆕
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   ├── attendance/                    # 📋 Asistencia, conducta y socioemocional 🆕
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── attendance.py              # REGISTRO_ASISTENCIA ◀️ desde grading
│   │   │   ├── attendance_status.py       # ESTADO_ASISTENCIA ◀️ desde grading
│   │   │   ├── incident_type.py           # TIPO_INCIDENTE 🆕
│   │   │   ├── conduct_incident.py        # INCIDENTE_DISCIPLINARIO ◀️ desde grading
│   │   │   ├── socioemotional_skill.py    # HABILIDAD_SOCIOEMOCIONAL 🆕
│   │   │   ├── skill_evaluation.py        # EVALUACION_HABILIDAD 🆕
│   │   │   └── behavior_evaluation.py     # RESUMEN_COMPORTAMIENTO ◀️ desde grading
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   ├── scheduling/                    # 🕐 Gestión de horarios
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── time_slot.py               ✓
│   │   │   ├── schedule_template_config.py ✓
│   │   │   ├── teacher_availability.py    ✓
│   │   │   ├── subject_constraint.py      ✓
│   │   │   └── schedule_slot.py           ✓
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   └── tests/
│   │
│   └── analytics/                     # 📊 Analítica predictiva y alertas
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── urls.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── risk_factor.py             # FACTOR_RIESGO ✓
│       │   ├── student_feature_snapshot.py  # SNAPSHOT_FEATURES_ML ✓ (corregir + campos)
│       │   ├── student_risk_score.py      # PREDICCION_DESERCION ✓ (corregir FK)
│       │   ├── student_risk_factor.py     # DETALLE_FACTOR_PREDICCION ✓
│       │   └── early_alert.py             # ALERTA_TEMPRANA 🆕
│       ├── repositories/
│       ├── services/
│       ├── api/
│       ├── ml/                            # Modelos ML
│       ├── tasks.py                       # Tareas Celery
│       └── tests/
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── urls.py
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       ├── production.py
│       └── test.py
│
├── docs/
│   ├── bd_en.html
│   ├── bd.html
│   ├── DOCKER.md
│   ├── STRUCTURE.md
│   ├── USER_GUIDE.md
│   └── ANALISIS_ERD_VS_MODELOS.md        ← este archivo
│
├── diagrams/
├── logs/
├── scripts/
│   ├── entrypoint.sh
│   └── verify_docker_setup.sh
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── AGENTS.md
├── schema.yml
└── skills-lock.json
```

---

## 10. Agrupación de Modelos por App (SRP + DDD)

| App                 | Dominio ERD           | SRP (Responsabilidad Única)                                                                           | Modelos                                                                                                                                                                                                                   |
| ------------------- | --------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`core`**          | Configuración + Sync  | _Infraestructura transversal al sistema_                                                              | SystemConfig, SyncQueue🆕                                                                                                                                                                                                 |
| **`institutions`**  | Estructura Académica  | _Gestionar la estructura organizativa del centro educativo_                                           | DocumentType, School_Year, AcademicLevel, AcademicGrade, **Section** ◀️, Classroom, RoomType                                                                                                                              |
| **`academic`**      | Oferta Académica      | _Gestionar la oferta académica, periodos y proyectos interdisciplinarios_                             | Subject, SubjectAcademicConfig, SubjectOffering, Academic_Period, Teacher_Subject_Section, InterdisciplinaryProject🆕, SubjectProject🆕                                                                                   |
| **`accounts`**      | Personas y Seguridad  | _Gestionar personas, usuarios y control de acceso (RBAC)_                                             | Person, User, Role, Permission, UserRole, RolePermission                                                                                                                                                                  |
| **`students`**      | Matrículas y Familia  | _Gestionar perfiles de estudiantes, vínculos familiares y matrículas_                                 | Student, Student_Representative, Enrollment, EnrollmentStatus                                                                                                                                                             |
| **`grading`**       | Evaluaciones          | _Gestionar el proceso evaluativo: estructura de evaluación, calificaciones, recuperación y auditoría_ | EvaluationMacro, EvaluationCriteria, EvaluationSubcriteria, ClassAssignment, GradeType, QualitativeScale, StudentNote, GradeChangeHistory, PeriodGradeSummary🆕, RecoveryProcess🆕, DiagnosticEvaluation🆕, ProjectNote🆕 |
| **`attendance`** 🆕 | Asistencia y Conducta | _Gestionar asistencia, incidentes disciplinarios y desarrollo socioemocional_                         | Attendance◀️, AttendanceStatus◀️, ConductIncident◀️, BehaviorEvaluation◀️, IncidentType🆕, SocioemotionalSkill🆕, SkillEvaluation🆕                                                                                       |
| **`scheduling`**    | Horarios              | _Gestionar la planificación horaria y disponibilidad docente_                                         | TimeSlot, ScheduleTemplateConfig, TeacherAvailability, SubjectConstraint, ScheduleSlot                                                                                                                                    |
| **`analytics`**     | Analítica Predictiva  | _Generar snapshots de features, predicciones de deserción y alertas tempranas_                        | RiskFactor, StudentFeatureSnapshot, StudentRiskScore, StudentRiskFactor, EarlyAlert🆕                                                                                                                                     |

---

## 11. Mapa de Migración de Modelos

### 11.1. Modelos a mover entre apps (4)

| Modelo               | Origen     | Destino         | Acción Requerida                                                    |
| -------------------- | ---------- | --------------- | ------------------------------------------------------------------- |
| `Section`            | `academic` | `institutions`  | Mover archivo .py, actualizar imports, actualizar FKs en otras apps |
| `Attendance`         | `grading`  | `attendance` 🆕 | Crear nueva app, mover archivo, actualizar imports                  |
| `AttendanceStatus`   | `grading`  | `attendance` 🆕 | Mover archivo, actualizar imports                                   |
| `ConductIncident`    | `grading`  | `attendance` 🆕 | Mover archivo, actualizar imports                                   |
| `BehaviorEvaluation` | `grading`  | `attendance` 🆕 | Mover archivo, actualizar imports                                   |

### 11.2. Nuevos modelos a crear (11)

| Modelo                     | App             | Entidad ERD                  | Prioridad |
| -------------------------- | --------------- | ---------------------------- | :-------: |
| `IncidentType`             | `attendance` 🆕 | TIPO_INCIDENTE               |   Alta    |
| `SocioemotionalSkill`      | `attendance` 🆕 | HABILIDAD_SOCIOEMOCIONAL     |   Alta    |
| `SkillEvaluation`          | `attendance` 🆕 | EVALUACION_HABILIDAD         |   Alta    |
| `InterdisciplinaryProject` | `academic`      | PROYECTO_INTERDISCIPLINAR    |   Alta    |
| `SubjectProject`           | `academic`      | PROYECTO_ASIGNATURA          |   Alta    |
| `PeriodGradeSummary`       | `grading`       | RESUMEN_CALIFICACION_PERIODO |   Alta    |
| `RecoveryProcess`          | `grading`       | PROCESO_RECUPERACION         |   Alta    |
| `DiagnosticEvaluation`     | `grading`       | EVALUACION_DIAGNOSTICA       |   Media   |
| `ProjectNote`              | `grading`       | NOTA_PROYECTO                |   Alta    |
| `EarlyAlert`               | `analytics`     | ALERTA_TEMPRANA              |   Media   |
| `SyncQueue`                | `core`          | COLA_SINCRONIZACION          |   Media   |

### 11.3. Modelos existentes a modificar (7)

| Modelo                   | App            | Acción                       | Campos a agregar/modificar                                             |
| ------------------------ | -------------- | ---------------------------- | ---------------------------------------------------------------------- |
| `Enrollment`             | `students`     | Agregar campos               | `school_year` (FK), `is_repeat` (Boolean), `repeated_school_year` (FK) |
| `Student`                | `students`     | Agregar campos               | `has_special_needs` (Boolean), `special_needs_type` (CharField)        |
| `Academic_Period`        | `academic`     | Agregar campo                | `period_type` (CharField)                                              |
| `Attendance`             | → `attendance` | Agregar campo                | `absence_type` (CharField)                                             |
| `ConductIncident`        | → `attendance` | Modificar campo              | Reemplazar `category` por `FK → IncidentType`, agregar `actions_taken` |
| `StudentFeatureSnapshot` | `analytics`    | Corregir FK + agregar campos | FK → `Enrollment` (no Student), +8 campos                              |
| `StudentRiskScore`       | `analytics`    | Corregir FK                  | FK → `Enrollment` (no Student)                                         |

---

## 12. Plan de Implementación por Fases

### Fase 1 —冷 Creación de modelos nuevos (bajo riesgo, alto valor)

**Objetivo:** Implementar los modelos faltantes del ERD sin modificar la estructura existente.

**Tareas:**

1. Crear `IncidentType`, `SocioemotionalSkill`, `SkillEvaluation` en nueva app `attendance`
2. Crear `InterdisciplinaryProject`, `SubjectProject` en `academic`
3. Crear `PeriodGradeSummary`, `RecoveryProcess`, `DiagnosticEvaluation`, `ProjectNote` en `grading`
4. Crear `EarlyAlert` en `analytics`
5. Crear `SyncQueue` en `core`

**Migraciones necesarias:** 11 new migrations
**Riesgo:** Bajo (solo adiciones, no modificaciones)

### Fase 2 — Corrección de modelos existentes (riesgo medio)

**Objetivo:** Alinear los modelos existentes con el ERD.

**Tareas:**

1. Agregar campos a `Enrollment`: `school_year`, `is_repeat`, `repeated_school_year`
2. Agregar campos a `Student`: `has_special_needs`, `special_needs_type`
3. Agregar `period_type` a `Academic_Period`
4. Agregar `absence_type` a `Attendance`
5. Modificar `ConductIncident`: reemplazar `category` por FK a `IncidentType`, agregar `actions_taken`
6. Corregir FK de `StudentFeatureSnapshot` a `Enrollment` y agregar campos faltantes
7. Corregir FK de `StudentRiskScore` a `Enrollment`

**Migraciones necesarias:** 7 alteraciones
**Riesgo:** Medio (involucra migraciones de datos si hay registros existentes)

### Fase 3 — Refactor de apps (riesgo medio-alto)

**Objetivo:** Reorganizar modelos entre apps para cumplir SRP.

**Tareas:**

1. Migrar `Section` de `academic` → `institutions`
2. Extraer `attendance` como app independiente desde `grading`
3. Registrar `attendance` en `INSTALLED_APPS`
4. Configurar URLs de `attendance` en `config/urls.py`
5. Actualizar todos los imports en repositorios, servicios y APIs
6. Crear `apps/attendance/apps.py` con config

**Riesgo:** Medio-Alto (mover archivos puede romper imports, requiere actualización manual)

### Fase 4 — Servicios y lógica de negocio (riesgo medio)

**Objetivo:** Implementar la lógica de negocio para los nuevos modelos.

**Tareas:**

1. Servicio de cálculo de `PeriodGradeSummary` (promedios formatiovo, sumativo, final)
2. Servicio de `RecoveryProcess` (flujo completo de recuperación)
3. Servicio de `EarlyAlert` (reglas de activación de alertas)
4. Servicio de evaluación diagnóstica
5. Servicio de sincronización offline (SyncQueue)

**Dependencias:** Fases 1 y 2 completadas

### Fase 5 — Pruebas y estabilización

**Objetivo:** Asegurar que todo funciona correctamente.

**Tareas:**

1. Tests unitarios para modelos nuevos
2. Tests de migraciones
3. Tests de servicios
4. Verificación de integridad referencial
5. Validación contra el ERD completo

---

## Apéndice A: Convenciones de Nomenclatura

| Elemento               | Convención                                | Ejemplo                                   |
| ---------------------- | ----------------------------------------- | ----------------------------------------- |
| Apps                   | `snake_case` (singular)                   | `grading`, `attendance`                   |
| Modelos                | `PascalCase`                              | `StudentNote`, `PeriodGradeSummary`       |
| Campos                 | `snake_case`                              | `numeric_score`, `attendance_date`        |
| Tablas DB              | `snake_case` (plural)                     | `student_notes`, `period_grade_summaries` |
| FK fields              | `snake_case` sin `_id` (Django lo agrega) | `enrollment = FK(Enrollment)`             |
| Constantes de permisos | `<modulo>.<accion>`                       | `grading.create_note`                     |

## Apéndice B: Diagrama de Dependencias entre Apps

```
core ─────────────────────────────────────────────────┐
  │                                                    │
  ▼                                                    ▼
institutions ───► academic ───► grading ───► analytics
      │                │              │
      │                ▼              ▼
      └───► students ──► attendance ──► scheduling
              │
              ▼
           accounts
```

- Las flechas indican dirección de dependencia (FKs)
- `core` es la base (no depende de ninguna app)
- `accounts` es dependencia de casi todas (por `User` y permisos)
- `scheduling` depende de `academic` e `institutions`

---

_Documento generado automáticamente mediante análisis del ERD (`docs/bd_en.html`) y exploración de modelos Django del proyecto SIGAE._
