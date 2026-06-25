# Data Warehouse Plan — Analytics App

## Objetivo

Migrar del modelo actual (tablas embebidas `StudentFeatureSnapshot`, `DashboardMetric`) a un **modelo multidimensional real (star schema)** dentro del mismo PostgreSQL (esquema `analytics_dw`), manteniendo la capa de servicios y API intacta.

## Beneficios

| Aspecto | Hoy | Con star schema |
|---------|-----|-----------------|
| Dashboard overview | 6 queries separadas a 3+ tablas | 1 query plana al star schema |
| Feature snapshot | 4 queries a 4 apps distintas + ensamblado en Python | 1 query JOIN a dim_* |
| Early alerts | Itera TODAS las matrículas activas | Query directa a fact_period_risk_summary |
| Drill-down docente/materia/horario | Imposible (no hay modelo) | Una query con JOINs a las dimensiones |
| Escalabilidad | Atado al esquema OLTP | Independiente, migrable a ClickHouse/DuckDB |
| Mantenimiento | Lógica de negocio + analytics mezclados | Separación clara OLTP vs OLAP |

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   PostgreSQL                         │
│                                                      │
│  ┌───────── public (OLTP) ─────────┐                │
│  │  attendance_attendance           │                │
│  │  grading_studentnote             │                │
│  │  behavior_conductincident        │                │
│  │  academic_subjectoffering        │                │
│  │  academic_teachersubjectsection  │                │
│  │  ... (70+ tablas)                │                │
│  └──────────────────────────────────┘                │
│                         │                            │
│              ETL (Celery tasks)                      │
│                         │                            │
│  ┌───── analytics_dw (Star Schema) ──┐               │
│  │  dim_calendar                     │               │
│  │  dim_student          (SCD Type 2)│               │
│  │  dim_teacher          (SCD Type 2)│               │
│  │  dim_subject_academic_config      │               │
│  │  dim_section                      │               │
│  │  dim_schedule                     │               │
│  │  dim_academic_period              │               │
│  │  dim_attendance_status            │               │
│  │                                   │               │
│  │  fact_daily_attendance            │               │
│  │  fact_grades                      │               │
│  │  fact_conduct_incidents           │               │
│  │  fact_period_risk_summary         │               │
│  │                                   │               │
│  │  agg_teacher_subject_summary      │               │
│  └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

## Cambios requeridos en el OLTP (prerequisito)

Estos cambios son **condición previa** para que el star schema sea correcto y no
dependa de inferencias frágiles. Deben aplicarse en una migración del esquema OLTP
antes de la Fase 2.

| Cambio | Modelo OLTP | Motivo |
|--------|-------------|--------|
| Agregar FK `class_schedule` (nullable) a `Attendance` | `apps/attendance/models/attendance.py` | Hoy `Attendance` solo tiene `teacher_subject_section` + `attendance_date`. Un `SubjectOffering` tiene **varios** `ClassSchedule` (distintos días/franjas). Sin este FK no se puede atar una asistencia a una franja horaria real, y `dim_schedule` / Q2 / Q4 quedarían inferidos por día de semana (ambiguo y propenso a fan-out). |

> Mientras el FK no exista, `fact_daily_attendance.schedule_key` se cargará como
> `NULL` (apuntando al miembro "Desconocido" de `dim_schedule`) y las consultas por
> horario (Q2, Q4) deben tratarse como **no disponibles**, no como aproximación.

## Dimensiones

### dim_calendar

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `date_key` | `INT PK` | YYYYMMDD |
| `full_date` | `DATE NOT NULL` | |
| `year` | `INT` | |
| `month` | `INT` | |
| `month_name` | `VARCHAR(20)` | |
| `week` | `INT` | Semana del año |
| `day_of_week` | `INT` | 1=Lunes … 7=Domingo |
| `day_name` | `VARCHAR(20)` | |
| `is_weekend` | `BOOLEAN` | |
| `is_holiday` | `BOOLEAN DEFAULT FALSE` | |

Carga: una sola vez al año vía Celery task programada.

### dim_student (SCD Type 2)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `student_key` | `SERIAL PK` | |
| `student_id` | `INT` | ID del OLTP (trazabilidad) |
| `student_code` | `VARCHAR(50)` | `Student.student_code` |
| `full_name` | `VARCHAR(200)` | Desde `Student.person` (`Person.names + last_names`) |
| `document_number` | `VARCHAR(20)` | Desde `Student.person.document_number` |
| `birth_date` | `DATE` | Desde `Student.person.birth_date` |
| `has_special_needs` | `BOOLEAN` | `Student.has_special_needs` |
| `special_needs_type` | `VARCHAR(100)` | Desde `Student.special_needs_type` (FK -> nombre) |
| `residential_zone` | `VARCHAR(100)` | Desde `Student.residential_zone` (**FK** `ResidentialZone` -> nombre) |
| `distance_km` | `DECIMAL(5,2)` | `Student.distance_to_school_km` |
| `scd_valid_from` | `DATE` | |
| `scd_valid_to` | `DATE` | |
| `scd_is_current` | `BOOLEAN DEFAULT TRUE` | |

> **Nota SCD2:** `Student.person` es OneToOne **nullable**; si `person` es `NULL`,
> `full_name`/`document_number`/`birth_date` quedan vacíos (no romper el ETL).
> **`age` NO se almacena aquí**: la edad cambia de forma continua y generaría
> versiones SCD2 espurias. La edad relevante se calcula por período en
> `fact_period_risk_summary.age_grade_gap`.

Carga: nightly ETL que detecta cambios e inserta nuevas versiones.

### dim_teacher (SCD Type 2)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `teacher_key` | `SERIAL PK` | |
| `user_id` | `INT` | ID del `iam.User` en OLTP |
| `full_name` | `VARCHAR(200)` | Desde `User.person` (`Person.names + last_names`) |
| `document_number` | `VARCHAR(20)` | Desde `User.person.document_number` |
| `email` | `VARCHAR(254)` | `User.email` (directo) |
| `is_active` | `BOOLEAN` | `User.is_active` |
| `scd_valid_from` | `DATE` | |
| `scd_valid_to` | `DATE` | |
| `scd_is_current` | `BOOLEAN DEFAULT TRUE` | |

> **Fuente:** el docente es `iam.User`. `full_name` y `document_number` **no están
> en `User`**: se obtienen vía `User.person` (OneToOne **nullable** a `people.Person`).
> Solo `email` e `is_active` están en `User`. El ETL debe hacer
> `LEFT JOIN people_person` y tolerar `person = NULL`.
> El filtro de "docentes" se determina por rol (`user_roles.role.code` en
> `DOCENTE, DIRECTOR, CONSEJERO, RECTOR`, ver `User.user_category`).

### dim_subject_academic_config

Grano: 1 fila = 1 `SubjectAcademicConfig` (configuración de una materia para un
grado/nivel). **No** a nivel `Subject` puro: `weekly_hours`, `is_required`, grado y
nivel viven en `SubjectAcademicConfig`, y un mismo `Subject` tiene varias configs.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `subject_key` | `SERIAL PK` | Surrogate (clave usada por los hechos) |
| `subject_academic_config_id` | `INT` | ID del `SubjectAcademicConfig` (trazabilidad real, único) |
| `subject_id` | `INT` | ID del `Subject` (para agrupar configs de la misma materia) |
| `code` | `VARCHAR(100)` | `Subject.code` |
| `name` | `VARCHAR(255)` | `Subject.name` |
| `academic_grade_id` | `INT` | |
| `academic_grade_name` | `VARCHAR(100)` | |
| `academic_level_id` | `INT` | |
| `academic_level_name` | `VARCHAR(100)` | |
| `weekly_hours` | `INT` | Desde `SubjectAcademicConfig` |
| `is_required` | `BOOLEAN` | Desde `SubjectAcademicConfig` |

> Para reportes "por materia" en general, agrupar por `subject_id`/`name`. Para
> reportes que dependen de horas/obligatoriedad/grado, usar la fila de config.

### dim_section

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `section_key` | `SERIAL PK` | |
| `section_id` | `INT` | |
| `code` | `VARCHAR(50)` | |
| `school_year_id` | `INT` | |
| `school_year_name` | `VARCHAR(255)` | |
| `academic_grade_id` | `INT` | |
| `academic_grade_name` | `VARCHAR(100)` | |
| `parallel` | `VARCHAR(255)` | Ej: "A", "B" |
| `academic_level` | `VARCHAR(100)` | |
| `academic_sublevel` | `VARCHAR(100)` | |

### dim_schedule

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `schedule_key` | `SERIAL PK` | |
| `class_schedule_id` | `INT` | |
| `day_of_week` | `INT` | |
| `day_name` | `VARCHAR(20)` | |
| `start_time` | `TIME` | |
| `end_time` | `TIME` | |
| `time_slot` | `VARCHAR(20)` | Ej: "07:00-08:30", "MAÑANA", "TARDE" |
| `classroom` | `VARCHAR(50)` | |
| `building` | `VARCHAR(50)` | |

### dim_academic_period

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `period_key` | `SERIAL PK` | |
| `period_id` | `INT` | |
| `code` | `VARCHAR(50)` | |
| `name` | `VARCHAR(80)` | |
| `period_type` | `VARCHAR(20)` | QUIMESTRE, PARCIAL |
| `school_year_id` | `INT` | |
| `school_year_name` | `VARCHAR(255)` | |
| `start_date` | `DATE` | |
| `end_date` | `DATE` | |
| `parent_period_key` | `INT FK -> self` | Para jerarquías (Quimestre -> Parcial) |
| `is_current` | `BOOLEAN` | |
| `scd_valid_from` | `DATE` | |
| `scd_valid_to` | `DATE` | |
| `scd_is_current` | `BOOLEAN DEFAULT TRUE` | |

### dim_attendance_status

Mini-dimensión que reemplaza los booleanos sueltos de asistencia. El OLTP guarda un
único `attendance_status.code` (P/J/A/T), que es mutuamente excluyente; modelarlo como
una dimensión evita combinaciones inconsistentes.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `attendance_status_key` | `SERIAL PK` | |
| `code` | `VARCHAR(5)` | P, J, A, T (`AttendanceStatus.code`) |
| `name` | `VARCHAR(50)` | Presente, Justificada, Ausente, Tardanza |
| `is_present` | `BOOLEAN` | TRUE solo para P |
| `is_absence` | `BOOLEAN` | TRUE para A y J (ambas cuentan como falta, según `feature_builder`) |
| `is_justified` | `BOOLEAN` | TRUE solo para J |
| `is_tardy` | `BOOLEAN` | TRUE solo para T |

Carga: una sola vez desde el catálogo `AttendanceStatus` (más miembro "Desconocido").

## Tablas de Hechos

### fact_daily_attendance

Grano: 1 fila = 1 registro de `Attendance` del OLTP
(`enrollment` + `teacher_subject_section` + `attendance_date`),
es decir 1 estudiante + 1 materia/sección + 1 día.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `attendance_key` | `BIGSERIAL PK` | |
| `date_key` | `INT FK -> dim_calendar` | Desde `Attendance.attendance_date` |
| `period_key` | `INT FK -> dim_academic_period` | |
| `student_key` | `INT FK -> dim_student` | Versión SCD2 vigente en `date_key` |
| `section_key` | `INT FK -> dim_section` | Desde `enrollment.section` |
| `subject_key` | `INT FK -> dim_subject_academic_config` | Vía `teacher_subject_section.subject_offering.subject_academic_config` |
| `teacher_key` | `INT FK -> dim_teacher` | Versión SCD2 vigente en `date_key` |
| `schedule_key` | `INT FK -> dim_schedule` | Desde `Attendance.class_schedule` (ver prerequisito OLTP). `NULL`/"Desconocido" si aún no existe el FK |
| `attendance_status_key` | `INT FK -> dim_attendance_status` | Reemplaza los 4 booleanos sueltos |
| `absence_type_key` | `INT` | Catálogo `AbsenceType` (FK en OLTP, nullable) |
| `source_id` | `INT` | `attendance.id` del OLTP |
| `loaded_at` | `TIMESTAMP` | |

Particionado por rango de `date_key` (mensual).

### fact_grades

Grano: 1 fila = 1 `StudentNote` (1 estudiante + 1 actividad evaluativa).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `grade_key` | `BIGSERIAL PK` | |
| `date_key` | `INT FK -> dim_calendar` | Desde `evaluative_activity.due_date` (la nota no tiene fecha propia) |
| `period_key` | `INT FK -> dim_academic_period` | |
| `student_key` | `INT FK -> dim_student` | Versión SCD2 vigente en `date_key` |
| `section_key` | `INT FK -> dim_section` | Desde `enrollment.section` |
| `subject_key` | `INT FK -> dim_subject_academic_config` | |
| `teacher_key` | `INT FK -> dim_teacher` | Vía `evaluative_activity.teacher_subject_section.user` |
| `grading_mode` | `VARCHAR(20)` | NUMERIC / QUALITATIVE (`StudentNote.grading_mode`) |
| `numeric_score` | `DECIMAL(5,2) NULL` | **Nullable**: vacío en notas cualitativas |
| `max_score` | `DECIMAL(5,2)` | `evaluative_activity.max_score` |
| `score_pct` | `DECIMAL(5,2) NULL` | `numeric_score / max_score`; NULL si cualitativa |
| `normalized_score` | `DECIMAL(5,2) NULL` | Equivalente 0-10 (`calculate_normalized_value`) |
| `qualitative_scale_code` | `VARCHAR(20) NULL` | Desde `qualitative_scale` (si cualitativa) |
| `grade_type` | `VARCHAR(20)` | Desde `GradeType` (p.ej. FORMATIVA, SUMATIVA) |
| `activity_type` | `VARCHAR(50)` | Desde `evaluative_activity.activity_type` |
| `evaluation_block` | `VARCHAR(100)` | Bloque -> Componente -> Indicador (aplanado; limitación conocida) |
| `block_weight` | `DECIMAL(5,2)` | |
| `is_recovery` | `BOOLEAN DEFAULT FALSE` | |
| `source_id` | `INT` | `student_note.id` del OLTP |
| `loaded_at` | `TIMESTAMP` | |

> **Notas cualitativas:** se cargan TODAS (numéricas y cualitativas) con su
> `grading_mode`. Los promedios (`AVG(numeric_score)` / `AVG(normalized_score)`)
> deben filtrar `grading_mode = 'NUMERIC'` para no sesgar resultados con NULLs.
> El detalle Bloque→Componente→Indicador se aplana en `evaluation_block`; si más
> adelante se requiere drill por componente, promover a `dim_evaluation_structure`.

### fact_conduct_incidents

Grano: 1 fila = 1 incidente de conducta.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `incident_key` | `BIGSERIAL PK` | |
| `date_key` | `INT FK -> dim_calendar` | Desde `incident_date` |
| `period_key` | `INT FK -> dim_academic_period` | |
| `student_key` | `INT FK -> dim_student` | Vía `enrollment.student`; "Desconocido" si `enrollment` es NULL |
| `section_key` | `INT FK -> dim_section` | Vía `enrollment.section`; "Desconocido" si `enrollment` es NULL |
| `incident_type` | `VARCHAR(20)` | Desde `IncidentType.code` |
| `severity_level` | `INT` | `severity.numeric_level` (1=leve, 2=moderada, 3=grave) |
| `severity_name` | `VARCHAR(100)` | `severity.name` |
| `family_notified` | `BOOLEAN` | `ConductIncident.family_notified` |
| `source_id` | `INT` | `conduct_incident.id` del OLTP |
| `loaded_at` | `TIMESTAMP` | |

> **`enrollment` es nullable** en `ConductIncident`. Los incidentes sin matrícula
> apuntan a los miembros "Desconocido" de `dim_student`/`dim_section` (no se descartan
> ni rompen el ETL).

### fact_period_risk_summary

Grano: 1 fila = 1 estudiante + 1 período académico.
Esta tabla reemplaza a `StudentFeatureSnapshot` + `StudentRiskScore` + `StudentRiskFactor`.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `risk_key` | `BIGSERIAL PK` | |
| `period_key` | `INT FK -> dim_academic_period` | |
| `student_key` | `INT FK -> dim_student` | |
| `section_key` | `INT FK -> dim_section` | |
| `attendance_rate` | `DECIMAL(5,2)` | |
| `total_absences` | `INT` | |
| `max_consecutive_absences` | `INT` | |
| `tardiness_count` | `INT` | |
| `justified_absences` | `INT` | |
| `unjustified_absences` | `INT` | |
| `formative_avg` | `DECIMAL(5,2)` | |
| `summative_avg` | `DECIMAL(5,2)` | |
| `grade_trend_slope` | `DECIMAL(5,2)` | |
| `failing_subjects` | `INT` | |
| `requires_recovery` | `BOOLEAN` | |
| `conduct_score` | `DECIMAL(5,2)` | |
| `severe_incidents` | `INT` | |
| `total_incidents` | `INT` | |
| `family_notified_ratio` | `DECIMAL(5,2)` | |
| `prev_period_avg_grade` | `DECIMAL(5,2)` | |
| `age_grade_gap` | `INT` | |
| `is_repeat` | `BOOLEAN` | |
| `has_special_needs` | `BOOLEAN` | |
| `risk_score` | `DECIMAL(5,2)` | Output del modelo ML |
| `risk_label` | `VARCHAR(20)` | BAJO, MEDIO, ALTO, CRITICO |
| `model_version` | `VARCHAR(50)` | |
| `loaded_at` | `TIMESTAMP` | |

Índices: `(period_key, risk_label)`, `(period_key, section_key)`, `(student_key)`.

## Tablas de Agregados (para dashboards)

### agg_teacher_subject_summary

Refrescada periódicamente vía Celery (*no* en tiempo real).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `agg_key` | `BIGSERIAL PK` | |
| `period_key` | `INT FK -> dim_academic_period` | |
| `teacher_key` | `INT FK -> dim_teacher` | |
| `subject_key` | `INT FK -> dim_subject_academic_config` | |
| `section_key` | `INT FK -> dim_section` | |
| `student_count` | `INT` | |
| `avg_attendance_rate` | `DECIMAL(5,2)` | |
| `avg_formative_score` | `DECIMAL(5,2)` | |
| `avg_summative_score` | `DECIMAL(5,2)` | |
| `failing_rate` | `DECIMAL(5,2)` | % estudiantes que requieren recuperación |
| `incident_count` | `INT` | |
| `avg_risk_score` | `DECIMAL(5,2)` | |
| `high_risk_count` | `INT` | |
| `calculated_at` | `TIMESTAMP` | |
| `UNIQUE(period_key, teacher_key, subject_key, section_key)` | | |

## Consultas Habilitadas

### Q1: Peores docentes + materia (calificaciones)

```sql
SELECT  t.full_name, s.name, AVG(g.numeric_score) as avg_score
FROM    analytics_dw.fact_grades g
JOIN    analytics_dw.dim_teacher t ON g.teacher_key = t.teacher_key
JOIN    analytics_dw.dim_subject_academic_config s ON g.subject_key = s.subject_key
WHERE   g.period_key = :periodo_actual
  AND   g.grading_mode = 'NUMERIC'   -- evita NULLs de notas cualitativas
GROUP BY t.full_name, s.name
ORDER BY avg_score ASC
LIMIT  10;
```

### Q2: Horario con más ausentismo

> Requiere el prerequisito OLTP (`Attendance.class_schedule`). Sin él, `schedule_key`
> es "Desconocido" y esta consulta no es representativa.

```sql
SELECT  sl.day_name, sl.time_slot,
        COUNT(*) FILTER (WHERE st.is_absence) * 100.0 / COUNT(*) as absence_rate
FROM    analytics_dw.fact_daily_attendance a
JOIN    analytics_dw.dim_schedule sl ON a.schedule_key = sl.schedule_key
JOIN    analytics_dw.dim_attendance_status st ON a.attendance_status_key = st.attendance_status_key
WHERE   a.period_key = :periodo_actual
GROUP BY sl.day_name, sl.time_slot
ORDER BY absence_rate DESC;
```

### Q3: Dashboard de riesgo por sección (1 query)

```sql
SELECT  sec.parallel, sec.academic_grade_name,
        COUNT(*) as total_students,
        AVG(r.risk_score) as avg_risk,
        COUNT(*) FILTER (WHERE r.risk_label = 'ALTO') as high_risk_count,
        AVG(r.attendance_rate) as avg_attendance,
        AVG(r.formative_avg) as avg_formative
FROM    analytics_dw.fact_period_risk_summary r
JOIN    analytics_dw.dim_section sec ON r.section_key = sec.section_key
WHERE   r.period_key = :periodo_actual
GROUP BY sec.parallel, sec.academic_grade_name;
```

### Q4: Correlación completa docente + materia + horario

> Se agrega cada hecho **por separado** antes de unir, para evitar el producto
> cartesiano (asistencia × notas) que infla los conteos.

```sql
WITH att AS (
    SELECT  teacher_key, subject_key, schedule_key,
            COUNT(*) as clases_dictadas,
            SUM((st.is_absence)::int) * 100.0 / COUNT(*) as tasa_ausentismo
    FROM    analytics_dw.fact_daily_attendance a
    JOIN    analytics_dw.dim_attendance_status st
            ON a.attendance_status_key = st.attendance_status_key
    WHERE   a.period_key = :periodo_actual
    GROUP BY teacher_key, subject_key, schedule_key
),
grd AS (
    SELECT  teacher_key, subject_key, AVG(numeric_score) as promedio_notas
    FROM    analytics_dw.fact_grades
    WHERE   period_key = :periodo_actual AND grading_mode = 'NUMERIC'
    GROUP BY teacher_key, subject_key
)
SELECT  t.full_name as docente,
        sub.name as materia,
        sl.day_name || ' ' || sl.time_slot as horario,
        att.clases_dictadas,
        att.tasa_ausentismo,
        grd.promedio_notas
FROM    att
JOIN    analytics_dw.dim_teacher t                 ON att.teacher_key = t.teacher_key
JOIN    analytics_dw.dim_subject_academic_config sub ON att.subject_key = sub.subject_key
JOIN    analytics_dw.dim_schedule sl               ON att.schedule_key = sl.schedule_key
LEFT JOIN grd ON grd.teacher_key = att.teacher_key AND grd.subject_key = att.subject_key
ORDER BY att.tasa_ausentismo DESC, grd.promedio_notas ASC
LIMIT  20;
```

### Q5: Secciones con más riesgo conductual por docente

> El docente no está en `fact_conduct_incidents`; se relaciona con la sección a través
> de las clases que dicta. Usamos un bridge docente↔sección derivado de la asistencia.

```sql
WITH teacher_section AS (   -- qué docente dicta en qué sección este período
    SELECT DISTINCT teacher_key, section_key, period_key
    FROM   analytics_dw.fact_daily_attendance
    WHERE  period_key = :periodo_actual
),
inc AS (                    -- incidentes agregados por sección
    SELECT section_key, period_key,
           COUNT(*) as incidentes,
           AVG(severity_level) as severidad_promedio
    FROM   analytics_dw.fact_conduct_incidents
    WHERE  period_key = :periodo_actual
    GROUP BY section_key, period_key
)
SELECT  t.full_name, sec.parallel,
        inc.incidentes, inc.severidad_promedio
FROM    inc
JOIN    teacher_section ts ON ts.section_key = inc.section_key
                          AND ts.period_key = inc.period_key
JOIN    analytics_dw.dim_teacher t  ON ts.teacher_key = t.teacher_key
JOIN    analytics_dw.dim_section sec ON inc.section_key = sec.section_key
ORDER BY inc.incidentes DESC;
```

## Pipeline ETL (Celery Tasks)

### Tareas nuevas

```python
# apps/analytics/etl/__init__.py

@shared_task
def etl_load_dim_calendar(year: int):
    """Carga 365 días de dim_calendar. Se ejecuta 1 vez por año."""

@shared_task
def etl_load_dim_students():
    """SCD Type 2: detecta cambios en Student y Person, inserta nuevas versiones."""

@shared_task
def etl_load_dim_teachers():
    """SCD Type 2: User (rol DOCENTE/DIRECTOR/CONSEJERO/RECTOR)
       LEFT JOIN Person para full_name/document_number (person nullable)."""

@shared_task
def etl_load_dim_subject_academic_config():
    """Carga SubjectAcademicConfig + Subject + AcademicGrade + AcademicLevel.
       Grano: 1 fila por SubjectAcademicConfig."""

@shared_task
def etl_load_dim_sections():
    """Carga Section + SchoolYear + AcademicGrade (+ AcademicLevel/Sublevel)."""

@shared_task
def etl_load_dim_schedules():
    """Carga ClassSchedule + DayOfWeek (+ miembro 'Desconocido')."""

@shared_task
def etl_load_dim_academic_periods():
    """Carga AcademicPeriod con jerarquía parent_period."""

@shared_task
def etl_load_dim_attendance_status():
    """Carga el catálogo AttendanceStatus (P/J/A/T) + miembro 'Desconocido'.
       Mapea is_present/is_absence/is_justified/is_tardy."""
```

> **Resolución temporal SCD2 (crítico).** Como `dim_student` y `dim_teacher` tienen
> varias filas por persona, los ETL de hechos **no** deben unir por `*_id` a secas
> (causaría fan-out o asociaría la versión equivocada). Deben resolver la `*_key` de
> la versión **vigente en `date_key`**:
>
> ```sql
> JOIN analytics_dw.dim_student ds
>   ON ds.student_id = src.student_id
>  AND src.event_date >= ds.scd_valid_from
>  AND (src.event_date < ds.scd_valid_to OR ds.scd_valid_to IS NULL)
> ```
>
> Para hechos de período (`fact_period_risk_summary`) sin fecha exacta, usar la versión
> vigente al `period.end_date`.

### Tareas de hechos

```python
@shared_task
def etl_load_fact_attendance(period_id: int):
    """INSERT INTO analytics_dw.fact_daily_attendance
       SELECT ... FROM attendance_attendance aa
       JOIN dim_* ON ...
       WHERE aa.academic_period_id = period_id
       ON CONFLICT DO NOTHING"""

@shared_task
def etl_load_fact_grades(period_id: int):
    """Carga StudentNote + EvaluativeActivity del período."""

@shared_task
def etl_load_fact_conduct_incidents(period_id: int):
    """Carga ConductIncident del período."""

@shared_task
def etl_load_fact_period_risk_summary(period_id: int):
    """Agrega desde fact_daily_attendance, fact_grades, fact_conduct_incidents
       + ejecuta modelo ML de riesgo.
       Reemplaza por completo a AcademicRiskFeatureBuilder."""

@shared_task
def etl_refresh_agg_teacher_subject():
    """REFRESH MATERIALIZED VIEW o TRUNCATE + INSERT en agg_teacher_subject_summary."""
```

### Tarea orquestadora

```python
@shared_task
def etl_refresh_all(period_id: int):
    """Ejecuta todo el pipeline ETL en orden:
       1. Dimensiones (si hay cambios)
       2. Hechos
       3. Agregados
    """
```

## Migración desde el modelo actual

### Fase 0: Prerequisito OLTP (0.5 día)

1. Migración: agregar FK `class_schedule` (nullable) a `Attendance` (ver sección
   "Cambios requeridos en el OLTP"). Backfill cuando sea posible.
2. Sin esto, `dim_schedule`/Q2/Q4 quedan deshabilitados (no aproximados).

### Fase 1: Crear schema y dimensiones (2-3 días)

1. `CREATE SCHEMA IF NOT EXISTS analytics_dw`
2. DDL de las 9 dimensiones (incluye `dim_subject_academic_config` y `dim_attendance_status`)
3. ETL inicial para cada dimensión (con miembros "Desconocido" donde aplique)
4. Task `etl_refresh_all` orquestadora
5. Tests de integridad (cada dim tiene la misma cantidad de registros que el OLTP)

### Fase 2: Fact tables + ETL (4-5 días)

1. `fact_daily_attendance` particionada (estado vía `dim_attendance_status`)
2. `fact_grades` (numéricas + cualitativas con `grading_mode`)
3. `fact_conduct_incidents` (maneja `enrollment` NULL)
4. `fact_period_risk_summary`
5. Tasks ETL para cada una, con **resolución SCD2 por fecha del hecho**
6. Tests: los agregados del star schema coinciden con los cálculos actuales

### Fase 3: Migrar servicios (3-4 días)

1. **`DashboardService`**: reemplazar las 6 queries actuales por 1 query a `fact_period_risk_summary` + `agg_teacher_subject_summary`
2. **`AcademicRiskFeatureBuilder`**: reemplazar las 4 queries a apps distintas por 1 query JOIN al star schema. El builder se convierte en un mapper simple.
3. **`EarlyAlertService`**: `evaluate_student()` ya no itera — hace query a `fact_period_risk_summary` + `fact_conduct_incidents`.
4. **`StudentClusteringService`**: lee features de `fact_period_risk_summary` en lugar de `StudentFeatureSnapshot`.
5. **`CSVExportService`**: cambia source de `StudentRiskScore`/`StudentFeatureSnapshot` a `fact_period_risk_summary`.

### Fase 4: Agregados + Dashboards (2 días)

1. `agg_teacher_subject_summary` con refresco periódico
2. Nuevos endpoints en `DashboardViewSet`:
   - `teacher-performance/` → Q1
   - `schedule-attendance/` → Q2
   - `teacher-subject-correlation/` → Q4
3. Migrar endpoints existentes a usar el star schema

### Fase 5: Deprecar modelos antiguos (1 día)

1. Marcar `StudentFeatureSnapshot`, `StudentRiskScore`, `StudentRiskFactor`, `DashboardMetric` como deprecated
2. Agregar `managed = False` o migración para dejarlos como vistas del star schema
3. Actualizar `README.md` y `STRUCTURE.md`

## Cronograma estimado

| Fase | Días |
|------|------|
| 0. Prerequisito OLTP (`Attendance.class_schedule`) | 0.5 |
| 1. Schema + dimensiones | 3 |
| 2. Fact tables + ETL | 5 |
| 3. Migrar servicios | 4 |
| 4. Agregados + dashboards | 2 |
| 5. Deprecar modelos | 1 |
| **Total** | **~15.5 días hábiles** |

## Lo que NO cambia

- `apps/analytics/api/` — los endpoints son los mismos
- `apps/analytics/api/views.py` — los ViewSets no se tocan, solo cambia el service layer
- `apps/analytics/tasks.py` — las tareas Celery existentes se refactorizan por dentro pero la interfaz es la misma
- `apps/analytics/ml/` — el modelo ML sigue funcionando, solo lee features de `fact_period_risk_summary`
- `StudentClusteringService` — misma API, solo cambia el source de datos
- Permisos, roles, tests existentes — nada cambia en seguridad

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Datos fuera de sincronía entre OLTP y DW | Baja | ETL transaccional (misma DB, misma transacción virtual via batch). Validación periódica con checksums. |
| Performance de carga ETL en horario laboral | Media | Ejecutar ETL en ventana nocturna vía Celery beat. Las cargas son incrementales (solo nuevo período). |
| Cambios en esquema OLTP rompen ETL | Media | Tests de integración que verifican que las columnas del OLTP existen. Mapeo explícito columna a columna. |
| Queries existentes que aún usan modelos viejos | Alta | Mantener ambos esquemas durante la Fase 5. Deprecación gradual con warnings. |
| Resolución SCD2 incorrecta (versión equivocada / fan-out) | Media | Unir hechos a `dim_*` por `*_id` + vigencia respecto a la fecha del hecho (no por `scd_is_current`). Tests que verifican 1 sola versión por hecho. |
| Notas cualitativas sesgan promedios | Media | `fact_grades` guarda `grading_mode`; todos los `AVG` numéricos filtran `grading_mode = 'NUMERIC'`. |
| `schedule_key`/`enrollment` nulos (horario sin FK, incidentes sin matrícula) | Media | Miembros "Desconocido" en `dim_schedule`/`dim_student`/`dim_section`; Q2/Q4 deshabilitadas hasta completar Fase 0. |
