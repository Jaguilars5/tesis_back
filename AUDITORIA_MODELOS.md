# Auditoría de Modelos — Relación con el Análisis de Deserción y Reglas de Negocio

> **Objetivo:** determinar, modelo por modelo, si cumple una función dentro del
> **análisis de deserción/riesgo académico**, dentro de una **regla de negocio**,
> si es **estructura/catálogo necesario**, un **candidato a enriquecer el análisis**,
> o un módulo **verdaderamente muerto**.
>
> **Fecha:** 2026-06-22
> **Alcance:** backend `apps/*` (Django). Análisis estático (lectura de código), sin ejecución.

---

## 1. Leyenda de clasificación

| Código | Significado |
|--------|-------------|
| **D** | **Insumo del análisis de deserción** (feature del modelo, alerta temprana, clustering o dashboard de riesgo) |
| **R** | **Regla de negocio** (validación, cálculo, transición de estado, signal) |
| **E** | **Estructural / dato maestro** (jerarquía o relación que sostiene el modelo de datos; sin regla propia pero indispensable) |
| **C** | **Catálogo descriptivo** (aporta significado/reporte; sin regla ni feature) |
| **F** | **Candidato a enriquecer el análisis** (hoy no se usa en deserción, pero tiene valor para hacerlo) |
| **X** | **Muerto** (sin regla, sin feature, sin propósito descriptivo claro) |

---

## 2. Resumen ejecutivo

- El **núcleo de la deserción** consume datos de 4 dominios: **asistencia**, **conducta**,
  **calificaciones** e **identidad del estudiante** (sección 3).
- Varios catálogos que *parecen* triviales **no son muertos**: su lógica vive en su campo
  `.code` y alimentan el motor de riesgo (`AttendanceStatus`, `AbsenceType`, `Severity`,
  `ActivityType`) o reglas (`QualitativeScale`, `QualitativeScaleSublevel`, `PeriodType`).
- **Tras tus aclaraciones**, casi ningún catálogo es "muerto": `Kinship`, `DocumentType`
  son catálogos descriptivos legítimos; `City` y `SpecialNeedsType` son **candidatos a
  enriquecer** el análisis; `AcademicLevel` es **estructural** (raíz de la jerarquía).
- Se detectaron **inconsistencias técnicas en el propio pipeline de ML** (sección 6) que son
  más relevantes para la tesis que los catálogos: **desajuste tren/inferencia**, **features
  hardcodeadas** y **doble taxonomía de asistencia**.

---

## 3. Modelos que alimentan el análisis de deserción (D)

Pipeline: `tasks.calculate_student_academic_risk_task` → `feature_builder.AcademicRiskFeatureBuilder`
→ scoring; y `early_alert_service.EarlyAlertService` para alertas tempranas.

| Modelo | Clase | Qué aporta al análisis |
|--------|:----:|------------------------|
| `students.Student` | D, R | `person.birth_date`, `has_special_needs`; provisión de Person+User |
| `students.Enrollment` | D, R | `is_repeat`, estado activo, FK a summaries; máquina de estados (matrícula/retiro/traslado) |
| `academic.AcademicPeriod` | D, R | periodo actual y previo, comparación de promedios; validaciones de fechas/cuotas |
| `institutions.SchoolYear` | D, R | `grade_level` (brecha edad-grado); año activo, solape de fechas |
| `attendance.Attendance` | D, R | % asistencia, faltas, tardanzas, faltas consecutivas; `clean()` valida sección/periodo |
| `attendance.AttendanceStatus` | D | `.code` `P/J/A/T` → cálculo de asistencia en `feature_builder` |
| `attendance.AbsenceType` | D | `.code` `unjustified/late` → **alerta temprana** de baja asistencia (<70%) |
| `behavior.ConductIncident` | D, R | conteo por severidad, `family_notified`, descripciones; base de evaluación conductual |
| `behavior.Severity` | D, R | `.code` `LEVE…MUY_GRAVE` → conduct_score, alerta conductual y umbrales de evaluación |
| `grading.StudentNote` | D, R | promedio, tendencia, materias reprobadas, último examen; `clean()` + signal de recálculo |
| `grading.EvaluativeActivity` | D, R | `max_score` (normalización), relación materia; validaciones de peso/fecha |
| `grading.ActivityType` | D | `.code == "EXAMEN"` → feature "último examen" |
| `grading.PeriodGradeSummary` | D, R | `final_avg_truncated` (periodo previo), `is_failing` (alerta); cache calculado |
| `people.Person` | D | `birth_date` para brecha edad-grado |

> **Nota:** `analytics.*` (`StudentFeatureSnapshot`, `StudentRiskScore`, `EarlyAlert`,
> `RiskFactor`, `StudentRiskFactor`) son el almacenamiento y salida del propio análisis
> (todos **D**). El clustering y los dashboards leen estas tablas, no datos crudos.

---

## 4. Catálogos que NO son muertos (lógica vía `.code` o regla)

> Esta es la sección que pediste corregir. **Sí son correctas** las afirmaciones, pero se
> precisa el matiz: estos modelos engañan porque su valor de negocio vive en el campo `.code`
> o en una validación, no en el modelo en sí.

| Modelo | Clase | Dónde vive su lógica |
|--------|:----:|----------------------|
| `attendance.AttendanceStatus` | D | `feature_builder._build_attendance` lee `.code` (`P/J/A/T`) |
| `attendance.AbsenceType` | D | `early_alert_service` lee `.code` (`unjustified/late`) vía `get_absences_summary` |
| `behavior.Severity` | D, R | `feature_builder._build_conduct` y `BehaviorEvaluationService` (umbrales) |
| `grading.ActivityType` | D | `feature_builder._last_exam_grade` filtra `.code == "EXAMEN"` |
| `grading.QualitativeScale` | R | `BehaviorEvaluationService` (mapeo `SE/SA/AC/NA`) + notas cualitativas |
| `grading.QualitativeScaleSublevel` | R | `StudentNoteSerializer.validate()` bloquea nota numérica/cualitativa según el subnivel. **Tiene regla, pero NO toca deserción.** |
| `academic.PeriodType` | R | cuotas (`divisions_per_year`) y unicidad de tipo de periodo por año |

---

## 5. Catálogos descriptivos, estructura y candidatos (con tus aclaraciones)

| Modelo | Clase | Justificación |
|--------|:----:|---------------|
| `students.Kinship` | C | **Relación representante↔representado** (madre, padre, tutor…). Catálogo descriptivo legítimo; no es feature ni regla, pero tiene propósito funcional. |
| `people.DocumentType` | C | Catálogo de tipo de documento (cédula, pasaporte…). Identidad; default `CC`. Sin regla, pero necesario. |
| `students.WithdrawalReason` | C / F | Se guarda al retirar (con fallback `OTRO`). Ninguna regla depende del valor **hoy**, pero el motivo de retiro es **alto valor analítico** para deserción → candidato. |
| `behavior.IncidentType` | C | Etiqueta de tipo de incidente; la lógica conductual la lleva `Severity`. Útil para reporte. |
| `institutions.AcademicLevel` | E | **Corrección:** NO es muerto. Es la **raíz de la jerarquía** académica (`Level → Sublevel → Grade → Section`); `AcademicSublevel` lo referencia por FK y `AcademicGrade.academic_level` se resuelve a través de él. Se usa además en `core/api/filters.py` (scoping) y como etiqueta de solo lectura. Sin regla propia, pero **estructural e indispensable**. |
| `institutions.AcademicSublevel` | E, R | Estructura; además participa en la regla de `QualitativeScaleSublevel` (modo de calificación por subnivel). |
| `institutions.AcademicGrade` | E | Estructura; se traversa en dashboards (`AcademicGrade.name`) como etiqueta de agrupación. |
| `academic.Subject` / `SubjectOffering` / `SubjectAcademicConfig` | E | Cadena estructural que `feature_builder` recorre para agrupar notas por materia (conteo de materias reprobadas). |

### Candidatos a enriquecer el análisis de deserción (F)

Hoy **no** entran al modelo, pero tienen valor directo para tu tesis:

| Modelo | Idea de uso | Estado actual |
|--------|-------------|---------------|
| `people.City` | **Ciudad de origen del estudiante** → identificar qué ciudades tienen mayor índice de deserción (variable contextual/geográfica). | Solo se guarda `city_id` en `Person`; **no** se lee en el pipeline. |
| `students.SpecialNeedsType` | Segmentar deserción por **tipo de necesidad especial** (no solo el booleano). | El pipeline usa el booleano `has_special_needs`; el catálogo de tipo **no** se consume. |
| `students.WithdrawalReason` | Analizar causas de retiro como variable objetivo/explicativa. | Se almacena pero no se analiza. |
| `behavior.IncidentType` | Segmentar riesgo conductual por tipo de incidente además de severidad. | Solo se almacena. |

> **Para `City` y `SpecialNeedsType`:** agregarlos requiere (1) exponer el campo en
> `feature_builder.build_persistence_metrics`, (2) añadir la columna a
> `StudentFeatureSnapshot`, y (3) incluirla en `FEATURE_COLUMNS` (entrenamiento) **y** en
> `_feature_vector` (inferencia) con el **mismo nombre** (ver sección 6).

---

## 6. Inconsistencias técnicas del pipeline de ML (corrección y advertencias)

> Esta es la otra sección que pediste corregir/precisar. La advertencia original era correcta
> en espíritu, pero el problema real es **más grave** de lo descrito.

### 6.1 Desajuste tren/inferencia (crítico)

- **Entrenamiento** (`apps/analytics/ml/train_model.py`, `FEATURE_COLUMNS`) usa **16 columnas**
  leídas de `StudentFeatureSnapshot`:
  `attendance_rate, consecutive_absences_max, tardiness_count, justified_absences,
  unjustified_absences, formative_avg_normalized, summative_avg_normalized, grade_trend_slope,
  failing_subjects_count, conduct_score, severe_incidents_count, family_notified_ratio,
  prev_period_avg_grade, age_grade_gap, is_repeat, has_special_needs`.
- **Inferencia** (`apps/analytics/tasks.py`, `_feature_vector`) construye **8 features con
  nombres DISTINTOS**:
  `faltas_leves, faltas_graves, porcentaje_asistencia, total_faltas, faltas_injustificadas,
  promedio_actual, materias_reprobadas, ultimo_examen`.
- **Consecuencia:** los nombres y la cantidad **no coinciden**. Al pasar un `DataFrame` con
  8 columnas mal nombradas a un modelo entrenado con 16, `scikit-learn` lanza error de
  *feature names mismatch*, capturado por el `except Exception` de `_predict_ml_score`, que
  **cae al heurístico de respaldo**. En la práctica, **el modelo ML probablemente nunca puntúa**;
  el score real proviene del cálculo por reglas (`WEIGHTS` conducta/asistencia/calificaciones).
- **`has_special_needs` SÍ es columna de entrenamiento** (a diferencia de lo que sugería la
  nota previa), pero al no llegar a inferencia, hoy es inerte.

### 6.2 Features hardcodeadas

- `tareas_entregadas` y `tareas_pendientes` están **fijas en `0`** en
  `feature_builder._build_grades`. No existe modelo de tareas/entregas que las alimente.

### 6.3 Doble taxonomía de asistencia

- `feature_builder` (riesgo) usa `attendance_status.code` (`P/J/A/T`).
- `early_alert_service` (alertas) usa `absence_type.code` (`justified/unjustified/late`).
- Son **dos catálogos paralelos** para el mismo concepto; conviene unificar la fuente canónica.

### 6.4 Doble definición de "materia reprobada"

- `feature_builder` recalcula reprobados desde `StudentNote` crudo (umbral `7.00`).
- `early_alert_service` usa `PeriodGradeSummary.is_failing`.
- Pueden divergir si el `PeriodGradeSummary` no está sincronizado.

### 6.5 Campos del snapshot que no llegan a inferencia

`is_repeat`, `age_grade_gap`, `prev_period_avg_grade`, `family_notified_ratio`,
`consecutive_absences_max`, `has_special_needs` se **calculan y persisten** en
`StudentFeatureSnapshot` (y se usan en entrenamiento), pero **no** se incluyen en
`_feature_vector` (inferencia). Quedan recolectados pero sin efecto en el score productivo.

---

## 7. Inventario rápido (clasificación final)

| App | Modelo | Clase |
|-----|--------|:----:|
| students | Student | D, R |
| students | Enrollment | D, R |
| students | StudentRepresentative | R |
| students | Kinship | C |
| students | WithdrawalReason | C / F |
| students | SpecialNeedsType | F |
| people | Person | D |
| people | City | F |
| people | DocumentType | C |
| academic | AcademicPeriod | D, R |
| academic | PeriodType | R |
| academic | Subject | E |
| academic | SubjectOffering | E |
| academic | SubjectAcademicConfig | E |
| academic | TeacherSubjectSection | R |
| academic | ClassSchedule | R |
| institutions | SchoolYear | D, R |
| institutions | AcademicLevel | E |
| institutions | AcademicSublevel | E, R |
| institutions | AcademicGrade | E |
| institutions | Section | R |
| attendance | Attendance | D, R |
| attendance | AttendanceStatus | D |
| attendance | AbsenceType | D |
| behavior | ConductIncident | D, R |
| behavior | Severity | D, R |
| behavior | BehaviorEvaluation | R |
| behavior | IncidentType | C |
| grading | StudentNote | D, R |
| grading | EvaluativeActivity | D, R |
| grading | EvaluationBlock | R |
| grading | BlockComponent | R |
| grading | ActivityType | D |
| grading | PeriodGradeSummary | D, R |
| grading | GradeChangeHistory | R |
| grading | QualitativeScale | R |
| grading | QualitativeScaleSublevel | R |
| iam | User | R |
| iam | Role | R |
| iam | Permission | R |
| iam | UserRole / RolePermission | E |
| analytics | StudentFeatureSnapshot | D |
| analytics | StudentRiskScore | D |
| analytics | EarlyAlert | D |
| analytics | RiskFactor / StudentRiskFactor | D |

**Conclusión:** con tus aclaraciones, **no existen modelos verdaderamente muertos (X)**.
Lo que sí existe son (a) **catálogos descriptivos** sin regla, (b) **candidatos claros a
enriquecer** la deserción (`City`, `SpecialNeedsType`, `WithdrawalReason`) y (c) **defectos
técnicos del pipeline de ML** (sección 6) que conviene corregir antes de confiar en el score.

---

## 8. Recomendaciones priorizadas

1. **Corregir el desajuste tren/inferencia** (6.1): unificar nombres/orden de features entre
   `FEATURE_COLUMNS` y `_feature_vector`. Sin esto, el ML no aporta y todo es heurístico.
2. **Unificar la taxonomía de asistencia** (6.3) y la definición de reprobado (6.4).
3. **Incorporar `City` y `SpecialNeedsType`** como features de segmentación (sección 5, F).
4. **Eliminar o implementar** `tareas_entregadas/pendientes` (6.2) — hoy son ruido fijo en `0`.
5. **Decidir** si `WithdrawalReason` e `IncidentType` se mantienen solo como catálogo de reporte
   o se promueven a variables del análisis.

---

## 9. Estudio de factibilidad: reglas y pesos configurables desde el frontend

> **Pregunta de origen:** ¿qué tan factible es que la institución configure desde el front
> **qué reglas evaluar** y **el peso de cada una**, partiendo de **parámetros preestablecidos
> seguros**? — Análisis previo a implementar (sin cambios de código aún).

### 9.1 Veredicto

**Muy factible** y alineado con el código actual. El score que realmente corre en producción
es un **motor de reglas con suma ponderada de 3 dimensiones** (conducta, asistencia,
calificaciones), expresado en constantes simples. Externalizarlo a configuración es de
complejidad **media-baja**. El **ML no se ajusta con perillas** (aprende sus pesos de los
datos), por lo que la configuración aplica al motor de reglas.

### 9.2 Qué está hardcodeado hoy (candidato a configuración)

Todo en `apps/analytics/tasks.py` (+ `early_alert_service.py`):

| Elemento | Ubicación | Valor actual |
|----------|-----------|--------------|
| Pesos de dimensión | `WEIGHTS` | conducta `0.30`, asistencia `0.35`, calificaciones `0.35` |
| Umbral del semáforo | `_risk_level` | rojo si asistencia `<70` / promedio `<6.0` / graves `>3` |
| Umbral por dimensión | `_conduct_level`, `_attendance_level`, `_grades_level` | varios cortes 70/85, 6.0/7.0 |
| Sub-scores | `_fallback_risk_score` | leve `×5`, moderada `×10`, grave `×25`, reprobada `×15` |
| Reglas de alerta | `early_alert_service.py` | asistencia `<0.7`, `≥2` reprobadas, `≥2` graves |
| Pesos de factores | `_populate_risk_factors` | `0.35/0.35/0.20/0.10` |

> Pista de diseño existente: el modelo `RiskFactor` y `StudentRiskFactor.contribution_weight`
> sugieren que el sistema se pensó para factores con peso; hoy esos pesos están fijos en código.

### 9.3 Sutileza clave (pesos vs. clasificación)

Los **pesos solo cambian el puntaje numérico** (`_fallback_risk_score`). La **etiqueta del
semáforo** (rojo/amarillo/verde) la decide `_risk_level` con **umbrales**. Por eso, para que
el peso de una dimensión **afecte realmente la clasificación**, hay que hacer configurables
**también los umbrales** (decisión tomada, ver 9.5).

### 9.4 Garantía de "parámetros preestablecidos seguros"

- **Presets cerrados**: perfiles "Conservador / Equilibrado / Estricto" como punto de partida.
- **Rangos acotados** por parámetro (p. ej. peso `10%–60%`, nunca `0`).
- **Invariantes validadas en backend**: pesos **suman 100%**; umbrales coherentes
  (rojo `<` amarillo `<` verde); dominios válidos (asistencia 0–100, notas 0–10).
- **Defaults seguros**: si falta config, se usan los valores actuales.
- **Versionado/auditoría**: registrar qué config produjo cada score (`model_version` ya existe)
  para reproducibilidad — relevante para la tesis.

### 9.5 Decisiones tomadas

| Decisión | Elección |
|----------|----------|
| **Alcance** | **Global** (una sola configuración para toda la institución, tipo *singleton*) |
| **Motor** | **Ambos** — la config incluye un selector `engine` (`ML` \| `reglas`) |
| **Qué se configura** | **Pesos + umbrales del semáforo** (para que el peso sí afecte la clasificación) |

> Nota: con `engine = ML` los pesos/umbrales del motor de reglas se ignoran; y mientras
> persista el desajuste tren/inferencia (6.1), seleccionar ML cae al heurístico.

### 9.6 Arquitectura propuesta (pendiente de implementar)

**Backend**
- Modelo `RiskScoringConfig` (global): `engine`, `weight_conducta/asistencia/calificaciones`,
  umbrales del semáforo (cortes de asistencia, promedio y faltas graves para rojo/amarillo).
- Migración + seed con los valores actuales como preset por defecto.
- Repositorio + servicio de lectura que `tasks.py` consulte en lugar de las constantes.
- Validadores (suma de pesos = 100%, rangos, coherencia de umbrales).
- ViewSet (GET/PATCH) con permisos siguiendo el patrón del repo.

**Frontend**
- Módulo en patrón *flat* (slice, controller, service, página): sliders de pesos + inputs de
  umbrales + selector de motor, con validación Yup (suma 100%, rangos).

### 9.7 Esfuerzo y riesgos

- **Backend** ~1–2 días; **Frontend** ~1–2 días.
- **Riesgo principal**: reproducibilidad de scores históricos al cambiar la config
  (decidir entre **congelar** el score con su config o **recalcular**).
- **Recomendación de posicionamiento**: para una institución educativa, el **motor de reglas
  configurable y explicable** es preferible como motor principal; el ML como señal
  complementaria/futura una vez corregido el desajuste tren/inferencia.

> **Estado:** documentado como factibilidad. Implementación **no iniciada**.
