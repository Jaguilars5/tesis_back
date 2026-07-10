# Plan de Migración: Arquitectura Multidimensional de Analytics

## Resumen Ejecutivo

Este documento describe la evolución incremental del sistema de analytics actual hacia una arquitectura multidimensional enfocada en análisis avanzado y predicción. La migración se realiza en **4 fases** sin interrumpir la operación actual.

**Objetivo final:** Sistema capaz de predecir múltiples outcomes de riesgo, identificar causas raíz, y proveer explicabilidad de predicciones.

**Timeline estimado:** 4-6 meses (fases secuenciales con overlap parcial)

**Principio rector:** Evolucionar, no reescribir. Cada fase agrega valor incremental sobre la arquitectura existente.

---

## Estado Actual (Baseline)

### Arquitectura existente
- **3 dimensiones de riesgo:** conducta, asistencia, calificaciones
- **15 features ML** (ver `apps/analytics/ml/features.py`)
- **Snapshot estático** por estudiante/período
- **Modelo binario** (is_failing: 0/1)
- **Tablas transaccionales** optimizadas para writes

### Tablas OLTP de análisis (se ELIMINARÁN en Fase 1)
Las siguientes tablas OLTP de análisis serán reemplazadas por tablas OLAP:
- `analytics_studentfeaturesnapshot` → reemplazado por `fact_riesgo_estudiante`
- `analytics_studentriskscore` → reemplazado por `fact_riesgo_estudiante`
- `analytics_studentriskfactor` → reemplazado por tabla nueva (si se necesita)

**Tablas OLTP que se MANTIENEN** (fuente de verdad):
- `attendance_attendance` (asistencia)
- `grading_student_note` (notas)
- `grading_period_grade_summary` (resumen de notas)
- `behavior_conduct_incident` (incidentes)
- `students_enrollment` (matrículas)
- `students_student` (estudiantes)
- `people_person`, `people_parish`, `people_city` (geolocalización)
- `academic_class_schedule` (horarios)
- `academic_teacher_subject_section` (docente-materia-sección)

**Tablas de catálogo que se MANTIENEN**:
- `analytics_riskfactor` (catálogo de factores de riesgo)
- `analytics_riskscoringconfig` (configuración singleton)
- `analytics_earlyalert` (alertas tempranas - es transaccional)

### Limitaciones identificadas
1. Sin separación OLTP/OLAP → queries analíticas lentas
2. Modelo predice un solo outcome (reprobación)
3. No captura evolución temporal (solo foto actual)
4. Sin análisis causal (correlaciones, no causas)
5. Sin explicabilidad de predicciones (SHAP)
6. Tablas OLTP de análisis duplican datos y complican el mantenimiento

---

## Fase 1: Capa Analítica OLAP (2-3 semanas)

### Objetivo
Reemplazar las tablas OLTP de análisis (`analytics_studentfeaturesnapshot`, `analytics_studentriskscore`, `analytics_studentriskfactor`) por una arquitectura OLAP completa con tablas de hechos y dimensiones. El ETL calculará el riesgo directamente desde fuentes OLTP reales (attendance, grading, behavior) sin usar snapshots OLTP intermedios. Los dashboards web leerán exclusivamente de las tablas OLAP.

### Entregables
1. **Esquema de data warehouse** sobre PostgreSQL existente
2. **Tablas OLAP** que reemplazan las tablas OLTP de análisis
3. **Vistas materializadas** actualizables periódicamente
4. **ETL** que calcula desde fuentes OLTP reales
5. **Dashboard refactorizado** para consumir capa OLAP
6. **Eliminación** de tablas OLTP de análisis obsoletas
7. **Queries 10x más rápidas** en reportes analíticos

### Diseño técnico

#### 1.1 Tablas transaccionales fuente (mapeo)

Antes de definir el esquema OLAP, documentamos las tablas transaccionales reales de las que se extraen los datos:

**Geolocalización (jerarquía):**
```
people_city (id, name, code)
    └── people_parish (id, name, code, parish_type [URBANA/RURAL], city_id)
            └── people_person (id, parish_id, document_number, birth_date, names, last_names)
                    └── iam_user (id, person_id, username)
```

**Estudiantes y matrículas:**
```
students_student (id, user_id, special_needs_type_id, student_code, has_special_needs)
    └── students_enrollment (id, student_id, section_id, enrollment_status [ACT/RET/TRS/SUS/GRA/INA], withdrawal_reason_id, is_repeat)
```

**Jerarquía académica:**
```
institutions_academic_level (id, name, code) -- ej: "Educación Básica"
    └── institutions_academic_sublevel (id, academic_level_id, name) -- ej: "Básica Superior"
            └── institutions_academic_grade (id, academic_sublevel_id, name) -- ej: "1ro BGU"
                    └── institutions_section (id, school_year_id, academic_grade_id, code, parallel)
```

**Año escolar y períodos:**
```
institutions_school_year (id, start_date, end_date)
    └── academic_academic_period (id, school_year_id, period_type_id, name, start_date, end_date, year_weight)
```

**Materias y ofertas:**
```
academic_subject (id, name, code)
    └── academic_subject_academic_config (id, subject_id, academic_grade_id, weekly_hours, is_required)
            └── academic_subject_offering (id, section_id, subject_academic_config_id)
```

**Docentes y horarios:**
```
iam_user (docente)
    └── academic_teacher_subject_section (id, user_id, subject_offering_id)
            └── academic_class_schedule (id, teacher_subject_section_id, day_of_week [1-7], start_time, end_time)
```

**Evaluaciones:**
```
academic_academic_period
    └── grading_evaluation_block (id, academic_period_id, subject_offering_id, block_type [FORMATIVA/SUMATIVA/PROJECT], weight_percentage)
            └── grading_block_component (id, evaluation_block_id, internal_weight)
                    └── grading_evaluative_activity (id, block_component_id, teacher_subject_section_id, activity_type_id, max_score, due_date)
                            └── grading_student_note (id, enrollment_id, evaluative_activity_id, numeric_score)
```

**Resumen de notas por período:**
```
grading_period_grade_summary (id, enrollment_id, subject_offering_id, academic_period_id, formative_avg, summative_avg, final_avg_truncated, is_failing)
```

**Asistencia:**
```
attendance_attendance (id, enrollment_id, teacher_subject_section_id, class_schedule_id, academic_period_id, attendance_status_id, absence_type_id, attendance_date)
```

**Conducta:**
```
behavior_conduct_incident (id, enrollment_id, academic_period_id, incident_type_id, severity_id, incident_date, family_notified)
```

#### 1.2 Dimensiones OLAP (basadas en tablas reales)

```sql
-- dim_tiempo: Granularidad temporal para agregaciones
-- Fuente: academic_academic_period, institutions_school_year
CREATE TABLE dim_tiempo (
    id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE NOT NULL,
    dia_semana INT,  -- 1=Lunes, 7=Domingo (de attendance_date)
    semana_anio INT,
    mes INT,
    trimestre INT,
    anio INT,
    -- FK a tablas transaccionales
    academic_period_id INT,  -- academic_academic_period.id
    school_year_id INT,  -- institutions_school_year.id
    -- Flags derivados
    es_dia_lectivo BOOLEAN,
    es_primer_dia_periodo BOOLEAN,
    es_ultimo_dia_periodo BOOLEAN
);

-- dim_geografia: Jerarquía geográfica completa
-- Fuente: people_city, people_parish
CREATE TABLE dim_geografia (
    id SERIAL PRIMARY KEY,
    -- Ciudad (people_city)
    city_id INT,
    city_name VARCHAR(100),
    city_code VARCHAR(10),
    -- Parroquia (people_parish)
    parish_id INT,
    parish_name VARCHAR(100),
    parish_code VARCHAR(10),
    parish_type VARCHAR(10),  -- URBANA / RURAL
    -- Nivel jerárquico (para drill-down)
    nivel VARCHAR(20)  -- 'ciudad' o 'parroquia'
);

-- dim_estudiante: Características del estudiante (desnormalizadas)
-- Fuente: students_student, iam_user, people_person, people_parish, people_city
CREATE TABLE dim_estudiante (
    id INT PRIMARY KEY,  -- students_student.id
    student_code VARCHAR(50),  -- students_student.student_code
    user_id INT,  -- iam_user.id
    -- Datos personales (de people_person via iam_user.person)
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    nombre_completo VARCHAR(200),
    fecha_nacimiento DATE,
    edad_actual INT,
    -- Geolocalización (de people_person.parish -> people_city)
    parish_id INT,  -- people_parish.id
    parish_name VARCHAR(100),
    parish_type VARCHAR(10),  -- URBANA / RURAL
    city_id INT,  -- people_city.id
    city_name VARCHAR(100),
    -- NEE (de students_student)
    has_special_needs BOOLEAN,  -- students_student.has_special_needs
    special_needs_type_id INT,  -- students_special_needs_type.id
    special_needs_type_name VARCHAR(100),
    -- Metadata
    is_active BOOLEAN  -- students_student.is_active
);

-- dim_grado_academico: Jerarquía académica (nivel -> subnivel -> grado)
-- Fuente: institutions_academic_level, institutions_academic_sublevel, institutions_academic_grade
CREATE TABLE dim_grado_academico (
    id INT PRIMARY KEY,  -- institutions_academic_grade.id
    grade_code VARCHAR(50),
    grade_name VARCHAR(100),
    -- Subnivel (institutions_academic_sublevel)
    sublevel_id INT,
    sublevel_code VARCHAR(20),
    sublevel_name VARCHAR(100),
    -- Nivel (institutions_academic_level)
    level_id INT,
    level_code VARCHAR(50),
    level_name VARCHAR(100)  -- ej: "Educación Básica", "Bachillerato"
);

-- dim_seccion: Contexto de la sección
-- Fuente: institutions_section, institutions_school_year, institutions_academic_grade
CREATE TABLE dim_seccion (
    id INT PRIMARY KEY,  -- institutions_section.id
    section_code VARCHAR(50),  -- institutions_section.code
    parallel VARCHAR(255),  -- institutions_section.parallel
    capacity INT,  -- institutions_section.capacity
    -- FK a dimensiones
    school_year_id INT,  -- institutions_school_year.id
    school_year_name VARCHAR(50),  -- derivado de start_date - end_date
    academic_grade_id INT,  -- institutions_academic_grade.id
    academic_grade_name VARCHAR(100),
    -- Metadata
    is_active BOOLEAN  -- institutions_section.is_active
);

-- dim_docente: Información de profesores
-- Fuente: iam_user, people_person
CREATE TABLE dim_docente (
    id INT PRIMARY KEY,  -- iam_user.id (docente)
    username VARCHAR(50),  -- iam_user.username
    -- Datos personales (de people_person via iam_user.person)
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    nombre_completo VARCHAR(200),
    email VARCHAR(100),  -- people_person.email
    -- Metadata
    is_active BOOLEAN  -- iam_user.is_active
);

-- dim_asignatura: Materias y configuración por grado
-- Fuente: academic_subject, academic_subject_academic_config
CREATE TABLE dim_asignatura (
    id INT PRIMARY KEY,  -- academic_subject.id
    subject_code VARCHAR(100),  -- academic_subject.code
    subject_name VARCHAR(255),  -- academic_subject.name
    -- Configuración por grado (academic_subject_academic_config)
    config_id INT,  -- academic_subject_academic_config.id
    weekly_hours INT,  -- academic_subject_academic_config.weekly_hours
    is_required BOOLEAN,  -- academic_subject_academic_config.is_required
    -- Metadata
    is_active BOOLEAN  -- academic_subject.is_active
);

-- dim_horario: Información de horarios de clase
-- Fuente: academic_class_schedule
CREATE TABLE dim_horario (
    id INT PRIMARY KEY,  -- academic_class_schedule.id
    -- FK a teacher_subject_section
    teacher_subject_section_id INT,  -- academic_teacher_subject_section.id
    -- Temporal
    day_of_week INT,  -- 1=Lunes, 7=Domingo
    day_name VARCHAR(10),  -- "Lunes", "Martes", etc.
    start_time TIME,
    end_time TIME,
    -- Clasificación temporal (derivada de start_time)
    franja_horaria VARCHAR(20),  -- "mañana" (06-12), "tarde" (12-18), "noche" (18-22)
    es_primera_hora BOOLEAN,  -- start_time < '09:00'
    es_ultima_hora BOOLEAN,  -- end_time > '16:00'
    -- Metadata
    is_active BOOLEAN  -- academic_class_schedule.is_active
);

-- dim_tipo_evento: Tipos de eventos (asistencia, incidentes)
-- Fuente: attendance_attendance_status, attendance_absence_type, behavior_incident_type, behavior_severity
CREATE TABLE dim_tipo_evento (
    id SERIAL PRIMARY KEY,
    -- Tipo principal
    categoria VARCHAR(30),  -- 'asistencia', 'ausencia', 'incidente'
    -- Subtipo (depende de categoría)
    subtipo_codigo VARCHAR(30),  -- attendance_attendance_status.code o behavior_severity.code
    subtipo_nombre VARCHAR(100),  -- attendance_attendance_status.name o behavior_severity.name
    -- Para incidentes: tipo de incidente
    incident_type_id INT,  -- behavior_incident_type.id
    incident_type_code VARCHAR(30),
    incident_type_name VARCHAR(100),
    -- Para ausencias: tipo de ausencia
    absence_type_id INT,  -- attendance_absence_type.id
    absence_type_code VARCHAR(30),
    absence_type_name VARCHAR(100)
);

-- dim_periodo_academico: Períodos y años escolares
-- Fuente: academic_academic_period, institutions_school_year, academic_period_type
CREATE TABLE dim_periodo_academico (
    id INT PRIMARY KEY,  -- academic_academic_period.id
    period_code VARCHAR(50),  -- academic_academic_period.code
    period_name VARCHAR(80),  -- academic_academic_period.name
    start_date DATE,
    end_date DATE,
    year_weight DECIMAL(5,2),  -- academic_academic_period.year_weight
    is_regular_period BOOLEAN,
    -- Tipo de período (academic_period_type)
    period_type_id INT,
    period_type_name VARCHAR(100),
    divisions_per_year INT,
    -- Año escolar (institutions_school_year)
    school_year_id INT,
    school_year_start DATE,
    school_year_end DATE,
    -- Metadata
    is_active BOOLEAN,
    grades_locked BOOLEAN
);
```

-- dim_asignatura: Materias
CREATE TABLE dim_asignatura (
    id INT PRIMARY KEY,
    codigo VARCHAR(50),
    nombre VARCHAR(200),
    area VARCHAR(100),  -- "Ciencias", "Humanidades", etc.
    tipo VARCHAR(50),  -- "Troncal", "Optativa", etc.
    creditos DECIMAL(5,2)
);

-- dim_evento: Tipos de eventos (faltas, alertas, incidentes)
CREATE TABLE dim_evento (
    id SERIAL PRIMARY KEY,
    tipo_evento VARCHAR(50),  -- "ausencia", "tardanza", "incidente", "alerta"
    subtipo VARCHAR(100),  -- "justificada", "injustificada", "grave", "leve"
    descripcion VARCHAR(500)
);
```

#### 1.3 Tablas de hechos OLAP (basadas en tablas reales)

```sql
-- fact_riesgo_estudiante: Snapshot analítico por período
-- Fuente: analytics_studentriskscore, analytics_studentfeaturesnapshot, students_enrollment
CREATE TABLE fact_riesgo_estudiante (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    estudiante_id INT REFERENCES dim_estudiante(id),  -- students_student.id
    periodo_id INT REFERENCES dim_periodo_academico(id),  -- academic_academic_period.id
    seccion_id INT REFERENCES dim_seccion(id),  -- institutions_section.id
    -- Dimensiones desnormalizadas para facilitar queries
    parroquia_id INT,  -- de dim_estudiante (drill-down geográfico)
    ciudad_id INT,  -- de dim_estudiante
    grado_id INT,  -- de dim_seccion -> dim_grado_academico
    -- Fecha de cálculo
    fecha_calculo DATE,
    
    -- Medidas de riesgo (de analytics_studentriskscore)
    score_riesgo DECIMAL(5,2),  -- risk_score
    nivel_riesgo VARCHAR(20),  -- risk_label: "rojo", "amarillo", "verde"
    version_modelo VARCHAR(50),  -- model_version
    
    -- Medidas de asistencia (de analytics_studentfeaturesnapshot)
    asistencia_pct DECIMAL(5,2),  -- attendance_rate
    faltas_justificadas INT,  -- justified_absences
    faltas_injustificadas INT,  -- unjustified_absences
    tardanzas INT,  -- tardiness_count
    max_faltas_consecutivas INT,  -- consecutive_absences_max
    
    -- Medidas académicas (de analytics_studentfeaturesnapshot)
    promedio_pond DECIMAL(4,2),  -- formative_avg_normalized + summative_avg_normalized
    materias_reprobadas INT,  -- failing_subjects_count
    tendencia_notas DECIMAL(5,2),  -- grade_trend_slope
    
    -- Medidas de conducta (de analytics_studentfeaturesnapshot)
    conduct_score DECIMAL(5,2),  -- conduct_score
    incidentes_graves INT,  -- severe_incidents_count
    
    -- Flags de estudiantes (de students_enrollment + students_student)
    tiene_nee BOOLEAN,  -- students_student.has_special_needs
    es_repetidor BOOLEAN,  -- students_enrollment.is_repeat
    estado_matricula VARCHAR(5),  -- students_enrollment.enrollment_status
    es_riesgo_alto BOOLEAN,  -- derivado: nivel_riesgo = 'rojo'
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(estudiante_id, periodo_id, fecha_calculo)
);

-- fact_asistencia: Eventos de asistencia por clase
-- Fuente: attendance_attendance
CREATE TABLE fact_asistencia (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    estudiante_id INT REFERENCES dim_estudiante(id),
    periodo_id INT REFERENCES dim_periodo_academico(id),
    seccion_id INT REFERENCES dim_seccion(id),
    docente_id INT REFERENCES dim_docente(id),  -- de attendance.teacher_subject_section.user
    asignatura_id INT REFERENCES dim_asignatura(id),  -- de teacher_subject_section.subject_offering
    horario_id INT REFERENCES dim_horario(id),  -- attendance.class_schedule
    tiempo_id INT REFERENCES dim_tiempo(id),  -- attendance.attendance_date
    evento_id INT REFERENCES dim_tipo_evento(id),  -- attendance_status + absence_type
    
    -- Contexto del evento
    attendance_date DATE,  -- attendance.attendance_date
    day_of_week INT,  -- derivado de attendance_date
    -- Estado de asistencia (attendance_attendance_status)
    attendance_status_id INT,
    attendance_status_code VARCHAR(30),  -- "P", "A", "J", "T" (Presente, Ausente, Justificado, Tardanza)
    -- Tipo de ausencia (si aplica)
    absence_type_id INT,
    absence_type_code VARCHAR(30),
    -- Observaciones
    observation TEXT,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW()
);

-- fact_calificacion: Notas por actividad evaluativa
-- Fuente: grading_student_note, grading_evaluative_activity, grading_evaluation_block
CREATE TABLE fact_calificacion (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    estudiante_id INT REFERENCES dim_estudiante(id),
    periodo_id INT REFERENCES dim_periodo_academico(id),
    seccion_id INT REFERENCES dim_seccion(id),
    docente_id INT REFERENCES dim_docente(id),  -- de evaluative_activity.teacher_subject_section.user
    asignatura_id INT REFERENCES dim_asignatura(id),  -- de teacher_subject_section.subject_offering
    horario_id INT REFERENCES dim_horario(id),  -- del teacher_subject_section (si tiene horario)
    
    -- Actividad evaluativa (grading_evaluative_activity)
    evaluative_activity_id INT,
    activity_title VARCHAR(200),
    activity_type_id INT,  -- grading_activity_type.id
    activity_type_code VARCHAR(30),  -- "EXAMEN", "TAREA", etc.
    activity_type_name VARCHAR(100),
    due_date DATE,
    
    -- Bloque de evaluación (grading_evaluation_block)
    evaluation_block_id INT,
    block_type VARCHAR(20),  -- "FORMATIVA", "SUMATIVA", "PROJECT"
    block_weight DECIMAL(5,2),  -- evaluation_block.weight_percentage
    
    -- Nota (grading_student_note)
    numeric_score DECIMAL(5,2),  -- student_note.numeric_score
    max_score DECIMAL(5,2),  -- evaluative_activity.max_score
    normalized_score DECIMAL(5,2),  -- calculado: (numeric_score / max_score) * 10
    grading_mode VARCHAR(20),  -- "NUMERIC" o "QUALITATIVE"
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(estudiante_id, evaluative_activity_id)
);

-- fact_resumen_periodo: Resumen de calificaciones por período y materia
-- Fuente: grading_period_grade_summary
CREATE TABLE fact_resumen_periodo (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    estudiante_id INT REFERENCES dim_estudiante(id),
    periodo_id INT REFERENCES dim_periodo_academico(id),
    seccion_id INT REFERENCES dim_seccion(id),
    docente_id INT REFERENCES dim_docente(id),  -- del teacher_subject_section (si se puede rastrear)
    asignatura_id INT REFERENCES dim_asignatura(id),  -- de subject_offering.subject_academic_config.subject
    
    -- Medidas (de grading_period_grade_summary)
    formative_avg DECIMAL(5,2),
    summative_avg DECIMAL(5,2),
    final_avg_truncated DECIMAL(5,2),
    is_failing BOOLEAN,
    promotion_status VARCHAR(20),  -- "approved" o "failed"
    
    -- Metadata
    calculated_at TIMESTAMP,
    creado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(estudiante_id, asignatura_id, periodo_id)
);

-- fact_incidente_conducta: Incidentes de conducta
-- Fuente: behavior_conduct_incident
CREATE TABLE fact_incidente_conducta (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    estudiante_id INT REFERENCES dim_estudiante(id),
    periodo_id INT REFERENCES dim_periodo_academico(id),
    seccion_id INT REFERENCES dim_seccion(id),
    tiempo_id INT REFERENCES dim_tiempo(id),  -- incident_date
    evento_id INT REFERENCES dim_tipo_evento(id),  -- incident_type + severity
    
    -- Contexto del incidente (behavior_conduct_incident)
    incident_date DATE,
    incident_type_id INT,  -- behavior_incident_type.id
    incident_type_code VARCHAR(30),
    incident_type_name VARCHAR(100),
    severity_id INT,  -- behavior_severity.id
    severity_code VARCHAR(30),  -- "LEVE", "MODERADA", "GRAVE", "MUY_GRAVE"
    severity_name VARCHAR(100),
    -- Acciones
    family_notified BOOLEAN,
    description TEXT,
    actions_taken TEXT,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW()
);

-- fact_rendimiento_docente: Rendimiento agregado por docente
-- Fuente: Agregación de fact_calificacion y fact_resumen_periodo
CREATE TABLE fact_rendimiento_docente (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    docente_id INT REFERENCES dim_docente(id),
    periodo_id INT REFERENCES dim_periodo_academico(id),
    seccion_id INT REFERENCES dim_seccion(id),
    asignatura_id INT REFERENCES dim_asignatura(id),
    
    -- Medidas agregadas
    total_estudiantes INT,
    promedio_general DECIMAL(5,2),
    promedio_formativo DECIMAL(5,2),
    promedio_sumativo DECIMAL(5,2),
    estudiantes_reprobados INT,
    tasa_reprobacion DECIMAL(5,2),  -- estudiantes_reprobados / total_estudiantes
    -- Asistencia promedio en sus clases
    asistencia_promedio DECIMAL(5,2),
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(docente_id, periodo_id, seccion_id, asignatura_id)
);

-- fact_rendimiento_horario: Rendimiento por horario/franja horaria
-- Fuente: Agregación de fact_asistencia y fact_calificacion
CREATE TABLE fact_rendimiento_horario (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    periodo_id INT REFERENCES dim_periodo_academico(id),
    seccion_id INT REFERENCES dim_seccion(id),
    dia_semana INT,  -- 1=Lunes, 7=Domingo
    franja_horaria VARCHAR(20),  -- "mañana", "tarde", "noche"
    
    -- Medidas de asistencia
    total_clases INT,
    clases_con_asistencia_completa INT,
    asistencia_promedio DECIMAL(5,2),
    tardanzas_promedio DECIMAL(5,2),
    
    -- Medidas de rendimiento (si hay notas en esas horas)
    promedio_notas DECIMAL(5,2),
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(periodo_id, seccion_id, dia_semana, franja_horaria)
);

-- fact_matricula: Estado de matrículas
-- Fuente: students_enrollment
CREATE TABLE fact_matricula (
    id SERIAL PRIMARY KEY,
    -- FK a dimensiones
    estudiante_id INT REFERENCES dim_estudiante(id),
    seccion_id INT REFERENCES dim_seccion(id),
    periodo_id INT REFERENCES dim_periodo_academico(id),  -- derivado de enrollment_date
    
    -- Estado de matrícula (students_enrollment)
    enrollment_status VARCHAR(5),  -- ACT, RET, TRS, SUS, GRA, INA
    enrollment_date DATE,
    withdrawal_date DATE,
    withdrawal_reason_id INT,  -- students_withdrawal_reason.id
    withdrawal_reason_code VARCHAR(20),
    withdrawal_reason_name VARCHAR(100),
    is_repeat BOOLEAN,
    
    -- Metadata
    creado_en TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(estudiante_id, seccion_id)
);
```

#### 1.4 Vistas materializadas (actualización periódica)

```sql
-- ═══════════════════════════════════════════════════════════════════════════════
-- VISTAS DE RESUMEN GENERAL
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vista: Resumen de riesgo por período
CREATE MATERIALIZED VIEW mv_resumen_riesgo_periodo AS
SELECT 
    periodo_id,
    COUNT(*) as total_estudiantes,
    AVG(score_riesgo) as score_promedio,
    COUNT(CASE WHEN nivel_riesgo = 'rojo' THEN 1 END) as count_rojo,
    COUNT(CASE WHEN nivel_riesgo = 'amarillo' THEN 1 END) as count_amarillo,
    COUNT(CASE WHEN nivel_riesgo = 'verde' THEN 1 END) as count_verde,
    AVG(asistencia_pct) as asistencia_promedio,
    AVG(promedio_pond) as promedio_promedio,
    AVG(incidentes_graves) as incidentes_graves_promedio
FROM fact_riesgo_estudiante
GROUP BY periodo_id;

-- Vista: Distribución de riesgo por grado académico
CREATE MATERIALIZED VIEW mv_riesgo_por_grado AS
SELECT 
    f.periodo_id,
    g.grade_name as grado_nombre,
    g.level_name as nivel_educativo,  -- ej: "Educación Básica", "Bachillerato"
    COUNT(*) as total_estudiantes,
    AVG(f.score_riesgo) as score_promedio,
    COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END) as count_rojo,
    COUNT(CASE WHEN f.nivel_riesgo = 'amarillo' THEN 1 END) as count_amarillo,
    COUNT(CASE WHEN f.nivel_riesgo = 'verde' THEN 1 END) as count_verde
FROM fact_riesgo_estudiante f
JOIN dim_seccion s ON f.seccion_id = s.id
JOIN dim_grado_academico g ON s.academic_grade_id = g.id
GROUP BY f.periodo_id, g.grade_name, g.level_name;

-- Vista: Estudiantes en declive (score subió > 20 puntos entre snapshots)
CREATE MATERIALIZED VIEW mv_estudiantes_declive AS
SELECT 
    f1.estudiante_id,
    f1.periodo_id,
    f1.score_riesgo as score_actual,
    f2.score_riesgo as score_anterior,
    (f1.score_riesgo - f2.score_riesgo) as cambio_score,
    f1.nivel_riesgo as nivel_actual,
    f2.nivel_riesgo as nivel_anterior
FROM fact_riesgo_estudiante f1
JOIN fact_riesgo_estudiante f2 
    ON f1.estudiante_id = f2.estudiante_id 
    AND f1.periodo_id = f2.periodo_id
WHERE f1.fecha_calculo > f2.fecha_calculo
    AND (f1.score_riesgo - f2.score_riesgo) > 20;

-- ═══════════════════════════════════════════════════════════════════════════════
-- VISTAS DE ANÁLISIS GEOGRÁFICO (por parroquia y ciudad)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vista: Riesgo por parroquia (análisis granular)
CREATE MATERIALIZED VIEW mv_riesgo_por_parroquia AS
SELECT 
    f.periodo_id,
    e.parish_id,
    e.parish_name,
    e.parish_type,  -- URBANA / RURAL
    e.city_id,
    e.city_name,
    COUNT(*) as total_estudiantes,
    AVG(f.score_riesgo) as score_promedio,
    AVG(f.asistencia_pct) as asistencia_promedio,
    AVG(f.promedio_pond) as promedio_promedio,
    AVG(f.conduct_score) as conduct_promedio,
    COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END) as count_rojo,
    COUNT(CASE WHEN f.nivel_riesgo = 'amarillo' THEN 1 END) as count_amarillo,
    COUNT(CASE WHEN f.nivel_riesgo = 'verde' THEN 1 END) as count_verde,
    -- Tasas
    ROUND(COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_riesgo_alto_pct,
    ROUND(COUNT(CASE WHEN f.estado_matricula = 'RET' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_desercion_pct
FROM fact_riesgo_estudiante f
JOIN dim_estudiante e ON f.estudiante_id = e.id
GROUP BY f.periodo_id, e.parish_id, e.parish_name, e.parish_type, e.city_id, e.city_name;

-- Vista: Riesgo por ciudad (agregación de parroquias)
CREATE MATERIALIZED VIEW mv_riesgo_por_ciudad AS
SELECT 
    f.periodo_id,
    e.city_id,
    e.city_name,
    COUNT(DISTINCT e.parish_id) as total_parroquias,
    COUNT(*) as total_estudiantes,
    AVG(f.score_riesgo) as score_promedio,
    AVG(f.asistencia_pct) as asistencia_promedio,
    AVG(f.promedio_pond) as promedio_promedio,
    COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END) as count_rojo,
    COUNT(CASE WHEN f.nivel_riesgo = 'amarillo' THEN 1 END) as count_amarillo,
    COUNT(CASE WHEN f.nivel_riesgo = 'verde' THEN 1 END) as count_verde,
    ROUND(COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_riesgo_alto_pct,
    ROUND(COUNT(CASE WHEN f.estado_matricula = 'RET' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_desercion_pct
FROM fact_riesgo_estudiante f
JOIN dim_estudiante e ON f.estudiante_id = e.id
GROUP BY f.periodo_id, e.city_id, e.city_name;

-- Vista: Comparativa urbano vs rural
CREATE MATERIALIZED VIEW mv_riesgo_urbano_rural AS
SELECT 
    f.periodo_id,
    e.parish_type,  -- URBANA / RURAL
    COUNT(*) as total_estudiantes,
    AVG(f.score_riesgo) as score_promedio,
    AVG(f.asistencia_pct) as asistencia_promedio,
    AVG(f.promedio_pond) as promedio_promedio,
    AVG(f.conduct_score) as conduct_promedio,
    COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END) as count_rojo,
    ROUND(COUNT(CASE WHEN f.nivel_riesgo = 'rojo' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_riesgo_alto_pct
FROM fact_riesgo_estudiante f
JOIN dim_estudiante e ON f.estudiante_id = e.id
WHERE e.parish_type IS NOT NULL
GROUP BY f.periodo_id, e.parish_type;

-- ═══════════════════════════════════════════════════════════════════════════════
-- VISTAS DE RENDIMIENTO POR DOCENTE
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vista: Rendimiento por docente (agregado por período)
CREATE MATERIALIZED VIEW mv_rendimiento_docente AS
SELECT 
    r.periodo_id,
    r.docente_id,
    d.nombre_completo as docente_nombre,
    d.username,
    COUNT(DISTINCT r.seccion_id) as total_secciones,
    COUNT(DISTINCT r.asignatura_id) as total_asignaturas,
    COUNT(DISTINCT r.estudiante_id) as total_estudiantes,
    -- Promedios generales
    AVG(r.final_avg_truncated) as promedio_general,
    AVG(r.formative_avg) as promedio_formativo,
    AVG(r.summative_avg) as promedio_sumativo,
    -- Reprobación
    COUNT(CASE WHEN r.is_failing THEN 1 END) as estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN r.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_reprobacion_pct,
    -- Ranking (se calculará en vista separada)
    RANK() OVER (PARTITION BY r.periodo_id ORDER BY AVG(r.final_avg_truncated) DESC) as ranking_periodo
FROM fact_resumen_periodo r
JOIN dim_docente d ON r.docente_id = d.id
WHERE r.docente_id IS NOT NULL
GROUP BY r.periodo_id, r.docente_id, d.nombre_completo, d.username;

-- Vista: Rendimiento por docente y materia (detalle)
CREATE MATERIALIZED VIEW mv_rendimiento_docente_materia AS
SELECT 
    r.periodo_id,
    r.docente_id,
    d.nombre_completo as docente_nombre,
    r.asignatura_id,
    a.subject_name as asignatura_nombre,
    r.seccion_id,
    s.parallel as paralelo,
    COUNT(DISTINCT r.estudiante_id) as total_estudiantes,
    AVG(r.final_avg_truncated) as promedio_general,
    COUNT(CASE WHEN r.is_failing THEN 1 END) as estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN r.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_reprobacion_pct
FROM fact_resumen_periodo r
JOIN dim_docente d ON r.docente_id = d.id
JOIN dim_asignatura a ON r.asignatura_id = a.id
JOIN dim_seccion s ON r.seccion_id = s.id
WHERE r.docente_id IS NOT NULL
GROUP BY r.periodo_id, r.docente_id, d.nombre_completo, r.asignatura_id, a.subject_name, r.seccion_id, s.parallel;

-- Vista: Comparativa de docentes por materia (mismo grado, diferente docente)
CREATE MATERIALIZED VIEW mv_comparativa_docentes_materia AS
SELECT 
    r.periodo_id,
    r.asignatura_id,
    a.subject_name as asignatura_nombre,
    g.grade_name as grado_nombre,
    r.docente_id,
    d.nombre_completo as docente_nombre,
    COUNT(DISTINCT r.estudiante_id) as total_estudiantes,
    AVG(r.final_avg_truncated) as promedio_general,
    COUNT(CASE WHEN r.is_failing THEN 1 END) as estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN r.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_reprobacion_pct
FROM fact_resumen_periodo r
JOIN dim_docente d ON r.docente_id = d.id
JOIN dim_asignatura a ON r.asignatura_id = a.id
JOIN dim_seccion s ON r.seccion_id = s.id
JOIN dim_grado_academico g ON s.academic_grade_id = g.id
WHERE r.docente_id IS NOT NULL
GROUP BY r.periodo_id, r.asignatura_id, a.subject_name, g.grade_name, r.docente_id, d.nombre_completo;

-- ═══════════════════════════════════════════════════════════════════════════════
-- VISTAS DE RENDIMIENTO POR MATERIA
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vista: Rendimiento por materia (agregado por período y grado)
CREATE MATERIALIZED VIEW mv_rendimiento_materia AS
SELECT 
    r.periodo_id,
    r.asignatura_id,
    a.subject_name as asignatura_nombre,
    a.subject_code,
    g.grade_id,
    g.grade_name as grado_nombre,
    g.level_name as nivel_educativo,
    COUNT(DISTINCT r.estudiante_id) as total_estudiantes,
    AVG(r.final_avg_truncated) as promedio_general,
    AVG(r.formative_avg) as promedio_formativo,
    AVG(r.summative_avg) as promedio_sumativo,
    -- Estadísticas de distribución
    MIN(r.final_avg_truncated) as nota_minima,
    MAX(r.final_avg_truncated) as nota_maxima,
    STDDEV(r.final_avg_truncated) as desviacion_estandar,
    -- Reprobación
    COUNT(CASE WHEN r.is_failing THEN 1 END) as estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN r.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_reprobacion_pct,
    -- Ranking de dificultad (menor promedio = más difícil)
    RANK() OVER (PARTITION BY r.periodo_id, g.grade_id ORDER BY AVG(r.final_avg_truncated) ASC) as ranking_dificultad
FROM fact_resumen_periodo r
JOIN dim_asignatura a ON r.asignatura_id = a.id
JOIN dim_seccion s ON r.seccion_id = s.id
JOIN dim_grado_academico g ON s.academic_grade_id = g.id
GROUP BY r.periodo_id, r.asignatura_id, a.subject_name, a.subject_code, g.grade_id, g.grade_name, g.level_name;

-- Vista: Materias con mayor tasa de reprobación (top 10)
CREATE MATERIALIZED VIEW mv_materias_mas_dificiles AS
SELECT 
    r.periodo_id,
    r.asignatura_id,
    a.subject_name as asignatura_nombre,
    g.grade_name as grado_nombre,
    COUNT(DISTINCT r.estudiante_id) as total_estudiantes,
    COUNT(CASE WHEN r.is_failing THEN 1 END) as estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN r.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_reprobacion_pct,
    AVG(r.final_avg_truncated) as promedio_general
FROM fact_resumen_periodo r
JOIN dim_asignatura a ON r.asignatura_id = a.id
JOIN dim_seccion s ON r.seccion_id = s.id
JOIN dim_grado_academico g ON s.academic_grade_id = g.id
GROUP BY r.periodo_id, r.asignatura_id, a.subject_name, g.grade_name
ORDER BY tasa_reprobacion_pct DESC
LIMIT 10;

-- ═══════════════════════════════════════════════════════════════════════════════
-- VISTAS DE RENDIMIENTO POR HORARIO
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vista: Asistencia y rendimiento por día de semana
CREATE MATERIALIZED VIEW mv_rendimiento_por_dia AS
SELECT 
    a.periodo_id,
    a.day_of_week,
    CASE a.day_of_week
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
        WHEN 7 THEN 'Domingo'
    END as dia_nombre,
    COUNT(*) as total_registros,
    -- Asistencia
    COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END) as presentes,
    COUNT(CASE WHEN a.attendance_status_code = 'A' THEN 1 END) as ausencias,
    COUNT(CASE WHEN a.attendance_status_code = 'J' THEN 1 END) as ausencias_justificadas,
    COUNT(CASE WHEN a.attendance_status_code = 'T' THEN 1 END) as tardanzas,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as asistencia_pct,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'T' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tardanza_pct
FROM fact_asistencia a
GROUP BY a.periodo_id, a.day_of_week;

-- Vista: Asistencia y rendimiento por franja horaria
CREATE MATERIALIZED VIEW mv_rendimiento_por_franja AS
SELECT 
    a.periodo_id,
    h.franja_horaria,
    COUNT(*) as total_clases,
    -- Asistencia
    COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END) as presentes,
    COUNT(CASE WHEN a.attendance_status_code = 'A' THEN 1 END) as ausencias,
    COUNT(CASE WHEN a.attendance_status_code = 'T' THEN 1 END) as tardanzas,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as asistencia_pct,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'T' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tardanza_pct,
    -- Incidentes de conducta en esa franja
    COUNT(DISTINCT CASE WHEN i.severity_code IN ('GRAVE', 'MUY_GRAVE') THEN i.id END) as incidentes_graves
FROM fact_asistencia a
JOIN dim_horario h ON a.horario_id = h.id
LEFT JOIN fact_incidente_conducta i 
    ON a.estudiante_id = i.estudiante_id 
    AND a.periodo_id = i.periodo_id
    AND a.attendance_date = i.incident_date
GROUP BY a.periodo_id, h.franja_horaria;

-- Vista: Horas específicas con peor rendimiento (análisis fino)
CREATE MATERIALIZED VIEW mv_horas_peor_rendimiento AS
SELECT 
    a.periodo_id,
    h.day_of_week,
    CASE h.day_of_week
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
        WHEN 7 THEN 'Domingo'
    END as dia_nombre,
    h.start_time,
    h.end_time,
    h.franja_horaria,
    COUNT(*) as total_registros,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as asistencia_pct,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'A' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as ausencia_pct,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'T' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tardanza_pct,
    -- Ranking de peor asistencia
    RANK() OVER (PARTITION BY a.periodo_id ORDER BY COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END)::NUMERIC / COUNT(*) ASC) as ranking_peor_asistencia
FROM fact_asistencia a
JOIN dim_horario h ON a.horario_id = h.id
GROUP BY a.periodo_id, h.day_of_week, h.start_time, h.end_time, h.franja_horaria
HAVING COUNT(*) >= 10  -- Solo horas con al menos 10 registros
ORDER BY asistencia_pct ASC;

-- Vista: Primera hora vs última hora del día
CREATE MATERIALIZED VIEW mv_primera_vs_ultima_hora AS
SELECT 
    a.periodo_id,
    h.es_primera_hora,
    h.es_ultima_hora,
    CASE 
        WHEN h.es_primera_hora THEN 'Primera hora'
        WHEN h.es_ultima_hora THEN 'Última hora'
        ELSE 'Hora intermedia'
    END as tipo_hora,
    COUNT(*) as total_registros,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'P' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as asistencia_pct,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'A' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as ausencia_pct,
    ROUND(COUNT(CASE WHEN a.attendance_status_code = 'T' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tardanza_pct
FROM fact_asistencia a
JOIN dim_horario h ON a.horario_id = h.id
GROUP BY a.periodo_id, h.es_primera_hora, h.es_ultima_hora;

-- ═══════════════════════════════════════════════════════════════════════════════
-- VISTAS DE DESECIÓN
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vista: Deserción por parroquia
CREATE MATERIALIZED VIEW mv_desercion_por_parroquia AS
SELECT 
    m.periodo_id,
    e.parish_id,
    e.parish_name,
    e.parish_type,
    e.city_id,
    e.city_name,
    COUNT(*) as total_matriculas,
    COUNT(CASE WHEN m.enrollment_status = 'RET' THEN 1 END) as retirados,
    ROUND(COUNT(CASE WHEN m.enrollment_status = 'RET' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as tasa_desercion_pct
FROM fact_matricula m
JOIN dim_estudiante e ON m.estudiante_id = e.id
GROUP BY m.periodo_id, e.parish_id, e.parish_name, e.parish_type, e.city_id, e.city_name;

-- Vista: Motivos de retiro más comunes
CREATE MATERIALIZED VIEW mv_motivos_retiro AS
SELECT 
    m.periodo_id,
    m.withdrawal_reason_id,
    m.withdrawal_reason_code,
    m.withdrawal_reason_name,
    COUNT(*) as total_retiros,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM fact_matricula WHERE enrollment_status = 'RET' AND periodo_id = m.periodo_id) * 100, 2) as porcentaje_del_total
FROM fact_matricula m
WHERE m.enrollment_status = 'RET' AND m.withdrawal_reason_id IS NOT NULL
GROUP BY m.periodo_id, m.withdrawal_reason_id, m.withdrawal_reason_code, m.withdrawal_reason_name
ORDER BY total_retiros DESC;
```

#### 1.5 Pipeline de actualización

```python
# apps/analytics/management/commands/refresh_analytics_layer.py

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Refresca vistas materializadas y tablas de hechos analíticas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Reconstruye todo desde cero (lento)",
        )
        parser.add_argument(
            "--period-id",
            type=int,
            help="Solo refresca este período académico",
        )

    def handle(self, *args, **options):
        full = options["full"]
        period_id = options.get("period_id")

        if full:
            self.stdout.write("Reconstruyendo capa analítica completa...")
            self._rebuild_fact_tables(period_id)
        
        self.stdout.write("Refrescando vistas materializadas...")
        self._refresh_materialized_views()

        self.stdout.write(self.style.SUCCESS("Capa analítica actualizada"))

    def _rebuild_fact_tables(self, period_id):
        """
        ETL: Calcula riesgo y puebla tablas OLAP directamente desde fuentes OLTP reales.
        NO usa snapshots OLTP intermedios (analytics_studentfeaturesnapshot).
        """
        from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
        from apps.analytics.student_risk.domain.risk_engine import calculate_risk
        
        # ── 1. Calcular riesgo y poblar fact_riesgo_estudiante ──
        # Se calcula en memoria desde fuentes OLTP reales (attendance, grading, behavior)
        self._calculate_and_populate_risk(period_id)
        
        # ── 2. Copiar datos eventuales desde fuentes OLTP ──
        with connection.cursor() as cursor:
            # fact_asistencia (desde attendance_attendance)
            cursor.execute("""
                INSERT INTO fact_asistencia (
                    estudiante_id, periodo_id, seccion_id, docente_id, asignatura_id,
                    horario_id, tiempo_id, attendance_date, day_of_week,
                    attendance_status_id, attendance_status_code,
                    absence_type_id, absence_type_code, observation
                )
                SELECT 
                    att.enrollment_id,
                    att.academic_period_id,
                    tss.subject_offering.section_id,
                    tss.user_id,
                    so.subject_academic_config.subject_id,
                    att.class_schedule_id,
                    NULL,  -- tiempo_id (se puede poblar después)
                    att.attendance_date,
                    EXTRACT(ISODOW FROM att.attendance_date)::INT,
                    ast.id,
                    ast.code,
                    at.id,
                    at.code,
                    att.observation
                FROM attendance_attendance att
                JOIN attendance_attendance_status ast ON att.attendance_status_id = ast.id
                LEFT JOIN attendance_absence_type at ON att.absence_type_id = at.id
                JOIN academic_teacher_subject_section tss ON att.teacher_subject_section_id = tss.id
                JOIN academic_subject_offering so ON tss.subject_offering_id = so.id
                WHERE (%s IS NULL OR att.academic_period_id = %s)
                ON CONFLICT DO NOTHING
            """, [period_id, period_id])

            # fact_calificacion (desde grading_student_note)
            cursor.execute("""
                INSERT INTO fact_calificacion (
                    estudiante_id, periodo_id, seccion_id, docente_id, asignatura_id,
                    evaluative_activity_id, activity_title, activity_type_id,
                    activity_type_code, activity_type_name, due_date,
                    evaluation_block_id, block_type, block_weight,
                    numeric_score, max_score, normalized_score, grading_mode
                )
                SELECT 
                    sn.enrollment_id,
                    eb.academic_period_id,
                    tss.subject_offering.section_id,
                    tss.user_id,
                    so.subject_academic_config.subject_id,
                    ea.id,
                    ea.title,
                    ea.activity_type_id,
                    at.code,
                    at.name,
                    ea.due_date,
                    eb.id,
                    eb.block_type,
                    eb.weight_percentage,
                    sn.numeric_score,
                    ea.max_score,
                    sn.calculate_normalized_value(),
                    sn.grading_mode
                FROM grading_student_note sn
                JOIN grading_evaluative_activity ea ON sn.evaluative_activity_id = ea.id
                JOIN grading_block_component bc ON ea.block_component_id = bc.id
                JOIN grading_evaluation_block eb ON bc.evaluation_block_id = eb.id
                JOIN academic_teacher_subject_section tss ON ea.teacher_subject_section_id = tss.id
                JOIN academic_subject_offering so ON tss.subject_offering_id = so.id
                LEFT JOIN grading_activity_type at ON ea.activity_type_id = at.id
                WHERE (%s IS NULL OR eb.academic_period_id = %s)
                ON CONFLICT (estudiante_id, evaluative_activity_id) DO NOTHING
            """, [period_id, period_id])

            # fact_resumen_periodo (desde grading_period_grade_summary)
            cursor.execute("""
                INSERT INTO fact_resumen_periodo (
                    estudiante_id, periodo_id, seccion_id, docente_id, asignatura_id,
                    formative_avg, summative_avg, final_avg_truncated,
                    is_failing, promotion_status, calculated_at
                )
                SELECT 
                    pgs.enrollment_id,
                    pgs.academic_period_id,
                    so.section_id,
                    tss.user_id,
                    so.subject_academic_config.subject_id,
                    pgs.formative_avg,
                    pgs.summative_avg,
                    pgs.final_avg_truncated,
                    pgs.is_failing,
                    pgs.promotion_status,
                    pgs.calculated_at
                FROM grading_period_grade_summary pgs
                JOIN academic_subject_offering so ON pgs.subject_offering_id = so.id
                LEFT JOIN academic_teacher_subject_section tss 
                    ON so.id = tss.subject_offering_id
                WHERE (%s IS NULL OR pgs.academic_period_id = %s)
                ON CONFLICT (estudiante_id, asignatura_id, periodo_id) DO NOTHING
            """, [period_id, period_id])

            # fact_incidente_conducta (desde behavior_conduct_incident)
            cursor.execute("""
                INSERT INTO fact_incidente_conducta (
                    estudiante_id, periodo_id, seccion_id, incident_date,
                    incident_type_id, incident_type_code, incident_type_name,
                    severity_id, severity_code, severity_name,
                    family_notified, description, actions_taken
                )
                SELECT 
                    ci.enrollment_id,
                    ci.academic_period_id,
                    e.section_id,
                    ci.incident_date,
                    it.id,
                    it.code,
                    it.name,
                    s.id,
                    s.code,
                    s.name,
                    ci.family_notified,
                    ci.description,
                    ci.actions_taken
                FROM behavior_conduct_incident ci
                JOIN behavior_incident_type it ON ci.incident_type_id = it.id
                JOIN behavior_severity s ON ci.severity_id = s.id
                JOIN students_enrollment e ON ci.enrollment_id = e.id
                WHERE (%s IS NULL OR ci.academic_period_id = %s)
                ON CONFLICT DO NOTHING
            """, [period_id, period_id])

            # fact_matricula (desde students_enrollment)
            cursor.execute("""
                INSERT INTO fact_matricula (
                    estudiante_id, seccion_id, periodo_id,
                    enrollment_status, enrollment_date, withdrawal_date,
                    withdrawal_reason_id, withdrawal_reason_code, withdrawal_reason_name,
                    is_repeat
                )
                SELECT 
                    e.student_id,
                    e.section_id,
                    ap.id,  -- periodo_id (aproximado por enrollment_date)
                    e.enrollment_status,
                    e.enrollment_date,
                    e.withdrawal_date,
                    wr.id,
                    wr.code,
                    wr.name,
                    e.is_repeat
                FROM students_enrollment e
                LEFT JOIN students_withdrawal_reason wr ON e.withdrawal_reason_id = wr.id
                LEFT JOIN academic_academic_period ap 
                    ON e.enrollment_date BETWEEN ap.start_date AND ap.end_date
                WHERE (%s IS NULL OR ap.id = %s)
                ON CONFLICT (estudiante_id, seccion_id) DO NOTHING
            """, [period_id, period_id])

    def _refresh_materialized_views(self):
        """Refresca vistas materializadas concurrentemente."""
        views = [
            # General
            "mv_resumen_riesgo_periodo",
            "mv_riesgo_por_grado",
            "mv_estudiantes_declive",
            # Geográfico
            "mv_riesgo_por_parroquia",
            "mv_riesgo_por_ciudad",
            "mv_riesgo_urbano_rural",
            # Docente
            "mv_rendimiento_docente",
            "mv_rendimiento_docente_materia",
            "mv_comparativa_docentes_materia",
            # Materia
            "mv_rendimiento_materia",
            "mv_materias_mas_dificiles",
            # Horario
            "mv_rendimiento_por_dia",
            "mv_rendimiento_por_franja",
            "mv_horas_peor_rendimiento",
            "mv_primera_vs_ultima_hora",
            # Deserción
            "mv_desercion_por_parroquia",
            "mv_motivos_retiro",
        ]
        with connection.cursor() as cursor:
            for view in views:
                try:
                    cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error refrescando {view}: {e}"))
                    # Si falla CONCURRENTLY, intentar sin CONCURRENTLY
                    cursor.execute(f"REFRESH MATERIALIZED VIEW {view}")

    def _calculate_and_populate_risk(self, period_id):
        """
        Calcula riesgo académico directamente desde fuentes OLTP reales.
        
        Flujo:
        1. AcademicRiskFeatureBuilder lee de attendance_attendance, grading_student_note,
           behavior_conduct_incident (tablas OLTP reales)
        2. risk_engine.calculate_risk() calcula score y nivel
        3. Se inserta directamente en fact_riesgo_estudiante (OLAP)
        
        NO se usan snapshots OLTP intermedios.
        """
        from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
        from apps.analytics.student_risk.domain.risk_engine import calculate_risk
        from apps.students.repositories.enrollment_repo import EnrollmentRepository
        from apps.academic.academic_period.infrastructure.repositories import AcademicPeriodRepository
        
        if not period_id:
            period = AcademicPeriodRepository.get_all(active_only=True).first()
            if not period:
                self.stdout.write(self.style.WARNING("No hay período activo"))
                return
            period_id = period.id
        
        enrollments = EnrollmentRepository.get_all()
        enrollments = [e for e in enrollments if e.enrollment_status == "ACT"]
        
        self.stdout.write(f"Calculando riesgo para {len(enrollments)} estudiantes...")
        
        with connection.cursor() as cursor:
            for enrollment in enrollments:
                try:
                    # 1. Construir features desde fuentes OLTP reales
                    builder = AcademicRiskFeatureBuilder(
                        student_id=enrollment.student_id,
                        academic_period_id=period_id
                    )
                    snapshot = builder.build()
                    metrics = builder.build_persistence_metrics(snapshot)
                    
                    # 2. Calcular riesgo
                    analysis = calculate_risk(snapshot, metrics)
                    
                    # 3. Obtener dimensiones desnormalizadas
                    student = enrollment.student
                    person = getattr(getattr(student, 'user', None), 'person', None)
                    parish_id = getattr(person, 'parish_id', None) if person else None
                    city_id = None
                    if parish_id:
                        cursor.execute(
                            "SELECT city_id FROM people_parish WHERE id = %s", [parish_id]
                        )
                        row = cursor.fetchone()
                        city_id = row[0] if row else None
                    
                    # 4. Insertar en OLAP
                    cursor.execute("""
                        INSERT INTO fact_riesgo_estudiante (
                            estudiante_id, periodo_id, seccion_id, parroquia_id, ciudad_id,
                            grado_id, fecha_calculo,
                            score_riesgo, nivel_riesgo, version_modelo,
                            asistencia_pct, faltas_justificadas, faltas_injustificadas,
                            tardanzas, max_faltas_consecutivas,
                            promedio_pond, materias_reprobadas, tendencia_notas,
                            conduct_score, incidentes_graves,
                            tiene_nee, es_repetidor, estado_matricula, es_riesgo_alto
                        )
                        VALUES (
                            %s, %s, %s, %s, %s,
                            %s, CURRENT_DATE,
                            %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                        ON CONFLICT (estudiante_id, periodo_id, fecha_calculo)
                        DO UPDATE SET
                            score_riesgo = EXCLUDED.score_riesgo,
                            nivel_riesgo = EXCLUDED.nivel_riesgo,
                            version_modelo = EXCLUDED.version_modelo,
                            asistencia_pct = EXCLUDED.asistencia_pct,
                            faltas_justificadas = EXCLUDED.faltas_justificadas,
                            faltas_injustificadas = EXCLUDED.faltas_injustificadas,
                            tardanzas = EXCLUDED.tardanzas,
                            max_faltas_consecutivas = EXCLUDED.max_faltas_consecutivas,
                            promedio_pond = EXCLUDED.promedio_pond,
                            materias_reprobadas = EXCLUDED.materias_reprobadas,
                            tendencia_notas = EXCLUDED.tendencia_notas,
                            conduct_score = EXCLUDED.conduct_score,
                            incidentes_graves = EXCLUDED.incidentes_graves,
                            es_riesgo_alto = EXCLUDED.es_riesgo_alto
                    """, [
                        enrollment.student_id,
                        period_id,
                        enrollment.section_id,
                        parish_id,
                        city_id,
                        enrollment.section.academic_grade_id if enrollment.section else None,
                        analysis["semaforo_riesgo"]["puntaje_riesgo"],
                        analysis["semaforo_riesgo"]["nivel"],
                        analysis["model_version"],
                        metrics.get("attendance_rate", 0),
                        metrics.get("justified_absences", 0),
                        metrics.get("unjustified_absences", 0),
                        metrics.get("tardiness_count", 0),
                        metrics.get("consecutive_absences_max", 0),
                        metrics.get("avg_grade_normalized", 0),
                        metrics.get("failing_subjects_count", 0),
                        metrics.get("grade_trend_slope", 0),
                        metrics.get("conduct_score", 0),
                        metrics.get("severe_incidents_count", 0),
                        metrics.get("has_special_needs", False),
                        enrollment.is_repeat,
                        enrollment.enrollment_status,
                        analysis["semaforo_riesgo"]["nivel"] == "rojo",
                    ])
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"Error calculando riesgo para student {enrollment.student_id}: {e}"
                    ))
```

#### 1.6 Scheduler (Celery Beat)

```python
# config/celery.py (agregar a CELERY_BEAT_SCHEDULE)

CELERY_BEAT_SCHEDULE = {
    # ... existing schedules ...
    "refresh-analytics-layer": {
        "task": "apps.analytics.tasks.refresh_analytics_layer",
        "schedule": crontab(hour=2, minute=0),  # 2 AM diario
    },
}

# apps/analytics/tasks.py (agregar)

@shared_task
def refresh_analytics_layer():
    """Refresca capa analítica OLAP (ejecutado por Celery Beat)."""
    from django.core.management import call_command
    call_command("refresh_analytics_layer")
```

#### 1.7 Refactor de DashboardRepository

```python
# apps/analytics/dashboard/infrastructure/repositories.py (refactorizar)

class DashboardRepository:
    @staticmethod
    def get_snapshot_aggregates(academic_period_id):
        """AHORA: Lee de vista materializada (1 query, ~10ms)"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    total_estudiantes,
                    asistencia_promedio as attendance_rate_avg,
                    promedio_promedio as formative_avg,
                    count_rojo,
                    count_amarillo,
                    count_verde
                FROM mv_resumen_riesgo_periodo
                WHERE periodo_id = %s
            """, [academic_period_id])
            
            row = cursor.fetchone()
            if not row:
                return {"total_students": 0, ...}
            
            return {
                "total_students": row[0],
                "attendance_rate_avg": row[1],
                "formative_avg": row[2],
                "risk_distribution": {
                    "rojo": row[3],
                    "amarillo": row[4],
                    "verde": row[5],
                },
            }

    @staticmethod
    def get_risk_by_parish(academic_period_id):
        """Análisis de riesgo por parroquia."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    parish_id,
                    parish_name,
                    parish_type,
                    city_name,
                    total_estudiantes,
                    score_promedio,
                    asistencia_promedio,
                    promedio_promedio,
                    count_rojo,
                    count_amarillo,
                    count_verde,
                    tasa_riesgo_alto_pct,
                    tasa_desercion_pct
                FROM mv_riesgo_por_parroquia
                WHERE periodo_id = %s
                ORDER BY tasa_riesgo_alto_pct DESC
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_teacher_performance(academic_period_id):
        """Rendimiento por docente."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    docente_id,
                    docente_nombre,
                    username,
                    total_secciones,
                    total_asignaturas,
                    total_estudiantes,
                    promedio_general,
                    promedio_formativo,
                    promedio_sumativo,
                    estudiantes_reprobados,
                    tasa_reprobacion_pct,
                    ranking_periodo
                FROM mv_rendimiento_docente
                WHERE periodo_id = %s
                ORDER BY ranking_periodo ASC
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_subject_performance(academic_period_id):
        """Rendimiento por materia."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    asignatura_id,
                    asignatura_nombre,
                    grado_nombre,
                    nivel_educativo,
                    total_estudiantes,
                    promedio_general,
                    promedio_formativo,
                    promedio_sumativo,
                    nota_minima,
                    nota_maxima,
                    desviacion_estandar,
                    estudiantes_reprobados,
                    tasa_reprobacion_pct,
                    ranking_dificultad
                FROM mv_rendimiento_materia
                WHERE periodo_id = %s
                ORDER BY ranking_dificultad ASC
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_schedule_performance(academic_period_id):
        """Rendimiento por horario (día y franja)."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Por día de semana
            cursor.execute("""
                SELECT 
                    day_of_week,
                    dia_nombre,
                    total_registros,
                    presentes,
                    ausencias,
                    ausencias_justificadas,
                    tardanzas,
                    asistencia_pct,
                    tardanza_pct
                FROM mv_rendimiento_por_dia
                WHERE periodo_id = %s
                ORDER BY day_of_week
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            by_day = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Por franja horaria
            cursor.execute("""
                SELECT 
                    franja_horaria,
                    total_clases,
                    presentes,
                    ausencias,
                    tardanzas,
                    asistencia_pct,
                    tardanza_pct,
                    incidentes_graves
                FROM mv_rendimiento_por_franja
                WHERE periodo_id = %s
                ORDER BY 
                    CASE franja_horaria
                        WHEN 'mañana' THEN 1
                        WHEN 'tarde' THEN 2
                        WHEN 'noche' THEN 3
                    END
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            by_schedule = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Horas con peor rendimiento
            cursor.execute("""
                SELECT 
                    dia_nombre,
                    start_time,
                    end_time,
                    franja_horaria,
                    total_registros,
                    asistencia_pct,
                    ausencia_pct,
                    tardanza_pct,
                    ranking_peor_asistencia
                FROM mv_horas_peor_rendimiento
                WHERE periodo_id = %s AND ranking_peor_asistencia <= 10
                ORDER BY ranking_peor_asistencia ASC
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            worst_hours = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return {
                "by_day": by_day,
                "by_schedule": by_schedule,
                "worst_hours": worst_hours,
            }

    @staticmethod
    def get_dropout_by_parish(academic_period_id):
        """Deserción por parroquia."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    parish_id,
                    parish_name,
                    parish_type,
                    city_name,
                    total_matriculas,
                    retirados,
                    tasa_desercion_pct
                FROM mv_desercion_por_parroquia
                WHERE periodo_id = %s
                ORDER BY tasa_desercion_pct DESC
            """, [academic_period_id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

#### 1.8 Ejemplos de queries para análisis específicos

##### Análisis por parroquia (drill-down geográfico)

```sql
-- Top 10 parroquias con mayor riesgo
SELECT 
    parish_name,
    parish_type,
    city_name,
    total_estudiantes,
    score_promedio,
    tasa_riesgo_alto_pct,
    tasa_desercion_pct
FROM mv_riesgo_por_parroquia
WHERE periodo_id = 1
ORDER BY tasa_riesgo_alto_pct DESC
LIMIT 10;

-- Comparativa urbano vs rural
SELECT 
    parish_type,
    COUNT(*) as total_parroquias,
    SUM(total_estudiantes) as total_estudiantes,
    AVG(score_promedio) as score_promedio_ponderado,
    AVG(tasa_riesgo_alto_pct) as tasa_riesgo_promedio,
    AVG(tasa_desercion_pct) as tasa_desercion_promedio
FROM mv_riesgo_por_parroquia
WHERE periodo_id = 1
GROUP BY parish_type;

-- Parroquias con más de 50 estudiantes y tasa de riesgo > 30%
SELECT 
    parish_name,
    parish_type,
    city_name,
    total_estudiantes,
    tasa_riesgo_alto_pct
FROM mv_riesgo_por_parroquia
WHERE periodo_id = 1 
    AND total_estudiantes >= 50
    AND tasa_riesgo_alto_pct > 30
ORDER BY tasa_riesgo_alto_pct DESC;
```

##### Rendimiento por docente

```sql
-- Ranking de docentes por período
SELECT 
    docente_nombre,
    total_secciones,
    total_estudiantes,
    promedio_general,
    tasa_reprobacion_pct,
    ranking_periodo
FROM mv_rendimiento_docente
WHERE periodo_id = 1
ORDER BY ranking_periodo ASC;

-- Comparativa de docentes que enseñan la misma materia en el mismo grado
SELECT 
    asignatura_nombre,
    grado_nombre,
    docente_nombre,
    total_estudiantes,
    promedio_general,
    tasa_reprobacion_pct
FROM mv_comparativa_docentes_materia
WHERE periodo_id = 1 AND asignatura_nombre = 'Matemáticas'
ORDER BY promedio_general DESC;

-- Docentes con mayor tasa de reprobación (posible problema de enseñanza)
SELECT 
    docente_nombre,
    total_estudiantes,
    promedio_general,
    tasa_reprobacion_pct
FROM mv_rendimiento_docente
WHERE periodo_id = 1 
    AND total_estudiantes >= 20
    AND tasa_reprobacion_pct > 30
ORDER BY tasa_reprobacion_pct DESC;
```

##### Rendimiento por materia

```sql
-- Top 10 materias más difíciles (mayor tasa de reprobación)
SELECT 
    asignatura_nombre,
    grado_nombre,
    total_estudiantes,
    promedio_general,
    tasa_reprobacion_pct
FROM mv_rendimiento_materia
WHERE periodo_id = 1
ORDER BY tasa_reprobacion_pct DESC
LIMIT 10;

-- Materias con menor promedio por grado
SELECT 
    grado_nombre,
    asignatura_nombre,
    promedio_general,
    ranking_dificultad
FROM mv_rendimiento_materia
WHERE periodo_id = 1 AND grado_nombre = '1ro BGU'
ORDER BY ranking_dificultad ASC;

-- Comparativa formativa vs sumativa por materia
SELECT 
    asignatura_nombre,
    grado_nombre,
    promedio_formativo,
    promedio_sumativo,
    (promedio_sumativo - promedio_formativo) as diferencia,
    total_estudiantes
FROM mv_rendimiento_materia
WHERE periodo_id = 1
ORDER BY diferencia ASC;  -- Materias donde hay mayor caída de formativa a sumativa
```

##### Rendimiento por horario

```sql
-- Día de la semana con peor asistencia
SELECT 
    dia_nombre,
    total_registros,
    asistencia_pct,
    tardanza_pct
FROM mv_rendimiento_por_dia
WHERE periodo_id = 1
ORDER BY asistencia_pct ASC;

-- Franja horaria con peor rendimiento
SELECT 
    franja_horaria,
    total_clases,
    asistencia_pct,
    tardanza_pct,
    incidentes_graves
FROM mv_rendimiento_por_franja
WHERE periodo_id = 1
ORDER BY asistencia_pct ASC;

-- Horas específicas con peor asistencia (top 10)
SELECT 
    dia_nombre,
    start_time,
    end_time,
    franja_horaria,
    asistencia_pct,
    ausencia_pct,
    tardanza_pct
FROM mv_horas_peor_rendimiento
WHERE periodo_id = 1
ORDER BY ranking_peor_asistencia ASC
LIMIT 10;

-- Primera hora vs última hora del día
SELECT 
    tipo_hora,
    total_registros,
    asistencia_pct,
    ausencia_pct,
    tardanza_pct
FROM mv_primera_vs_ultima_hora
WHERE periodo_id = 1;
```

##### Queries para Power BI

```sql
-- Dataset completo para dashboard ejecutivo en Power BI
SELECT 
    p.period_name,
    p.school_year_start,
    g.level_name,
    g.grade_name,
    e.parish_name,
    e.parish_type,
    e.city_name,
    f.total_estudiantes,
    f.score_promedio,
    f.asistencia_promedio,
    f.promedio_promedio,
    f.count_rojo,
    f.count_amarillo,
    f.count_verde,
    f.tasa_riesgo_alto_pct,
    f.tasa_desercion_pct
FROM mv_riesgo_por_parroquia f
JOIN dim_periodo_academico p ON f.periodo_id = p.id
JOIN dim_estudiante e ON f.parish_id = e.parish_id
JOIN dim_seccion s ON f.seccion_id = s.id
JOIN dim_grado_academico g ON s.academic_grade_id = g.id;

-- Dataset para análisis de deserción en Power BI
SELECT 
    p.period_name,
    e.city_name,
    e.parish_name,
    e.parish_type,
    m.total_matriculas,
    m.retirados,
    m.tasa_desercion_pct,
    wr.withdrawal_reason_name,
    wr.total_retiros
FROM mv_desercion_por_parroquia m
JOIN dim_periodo_academico p ON m.periodo_id = p.id
JOIN dim_estudiante e ON m.parish_id = e.parish_id
LEFT JOIN mv_motivos_retiro wr ON m.periodo_id = wr.periodo_id;
```

### Checklist de implementación

- [ ] Crear migración Django con tablas de dimensiones (dim_tiempo, dim_geografia, dim_estudiante, dim_grado_academico, dim_seccion, dim_docente, dim_asignatura, dim_horario, dim_tipo_evento, dim_periodo_academico)
- [ ] Crear migración Django con tablas de hechos (fact_riesgo_estudiante, fact_asistencia, fact_calificacion, fact_resumen_periodo, fact_incidente_conducta, fact_rendimiento_docente, fact_rendimiento_horario, fact_matricula)
- [ ] Crear vistas materializadas (17 vistas: resumen general, geográficas, docente, materia, horario, deserción)
- [ ] Implementar comando `refresh_analytics_layer` con ETL que calcula riesgo desde fuentes OLTP reales
- [ ] Agregar task de Celery para refresh automático (cada 2h)
- [ ] Refactorizar `DashboardRepository` para usar vistas materializadas
- [ ] Agregar nuevos métodos al repository: `get_risk_by_parish`, `get_teacher_performance`, `get_subject_performance`, `get_schedule_performance`, `get_dropout_by_parish`
- [ ] Migrar datos existentes de tablas OLTP de análisis a tablas OLAP
- [ ] Eliminar tablas OLTP de análisis obsoletas (ver sección 1.9)
- [ ] Benchmark: comparar tiempos de queries antes/después
- [ ] Documentar esquema en `apps/analytics/DW_SCHEMA.md`
- [ ] Configurar índices en tablas de hechos para queries frecuentes
- [ ] Probar integración con Power BI (conexión directa a vistas materializadas)

#### 1.9 Eliminación de tablas OLTP de análisis obsoletas

Después de migrar los datos existentes y validar que las tablas OLAP funcionan correctamente, se eliminan las tablas OLTP de análisis que fueron reemplazadas:

```python
# apps/analytics/management/commands/drop_obsolete_oltp_tables.py

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Elimina tablas OLTP de análisis que fueron reemplazadas por OLAP"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirma la eliminación (sin esto solo muestra qué se eliminaría)",
        )

    def handle(self, *args, **options):
        tables_to_drop = [
            "analytics_studentfeaturesnapshot",  # Reemplazado por fact_riesgo_estudiante
            "analytics_studentriskscore",         # Reemplazado por fact_riesgo_estudiante
            "analytics_studentriskfactor",        # Reemplazado por tabla nueva (si se necesita)
        ]
        
        tables_to_keep = [
            "analytics_riskfactor",               # Catálogo (se mantiene)
            "analytics_riskscoringconfig",         # Configuración singleton (se mantiene)
            "analytics_earlyalert",                # Transaccional (se mantiene)
        ]

        self.stdout.write("Tablas que se ELIMINARÁN:")
        for table in tables_to_drop:
            self.stdout.write(f"  - {table}")
        
        self.stdout.write("\nTablas que se MANTENDRÁN:")
        for table in tables_to_keep:
            self.stdout.write(f"  - {table}")

        if not options["confirm"]:
            self.stdout.write(self.style.WARNING(
                "\nEjecuta con --confirm para eliminar las tablas"
            ))
            return

        with connection.cursor() as cursor:
            for table in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    self.stdout.write(self.style.SUCCESS(f"Eliminada: {table}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error eliminando {table}: {e}"))
```

#### 1.10 Migración de datos existentes

```python
# apps/analytics/management/commands/migrate_oltp_to_olap.py

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Migra datos de tablas OLTP de análisis a tablas OLAP"

    def handle(self, *args, **options):
        self.stdout.write("Migrando datos de OLTP a OLAP...")
        
        with connection.cursor() as cursor:
            # Migrar analytics_studentriskscore + analytics_studentfeaturesnapshot
            # → fact_riesgo_estudiante
            self.stdout.write("Migrando risk scores y snapshots...")
            cursor.execute("""
                INSERT INTO fact_riesgo_estudiante (
                    estudiante_id, periodo_id, seccion_id, parroquia_id, ciudad_id,
                    grado_id, fecha_calculo,
                    score_riesgo, nivel_riesgo, version_modelo,
                    asistencia_pct, faltas_justificadas, faltas_injustificadas,
                    tardanzas, max_faltas_consecutivas,
                    promedio_pond, materias_reprobadas, tendencia_notas,
                    conduct_score, incidentes_graves,
                    tiene_nee, es_repetidor, estado_matricula, es_riesgo_alto
                )
                SELECT 
                    r.enrollment_id,
                    r.academic_period_id,
                    e.section_id,
                    per.parish_id,
                    p.city_id,
                    sec.academic_grade_id,
                    r.calculated_at::DATE,
                    r.risk_score,
                    r.risk_label,
                    r.model_version,
                    s.attendance_rate,
                    s.justified_absences,
                    s.unjustified_absences,
                    s.tardiness_count,
                    s.consecutive_absences_max,
                    s.formative_avg_normalized,
                    s.failing_subjects_count,
                    s.grade_trend_slope,
                    s.conduct_score,
                    s.severe_incidents_count,
                    s.has_special_needs,
                    e.is_repeat,
                    e.enrollment_status,
                    (r.risk_label = 'rojo')
                FROM analytics_studentriskscore r
                JOIN analytics_studentfeaturesnapshot s 
                    ON r.enrollment_id = s.enrollment_id 
                    AND r.academic_period_id = s.academic_period_id
                JOIN students_enrollment e ON r.enrollment_id = e.id
                JOIN students_student st ON e.student_id = st.id
                JOIN iam_user u ON st.user_id = u.id
                LEFT JOIN people_person per ON u.person_id = per.id
                LEFT JOIN people_parish p ON per.parish_id = p.id
                JOIN institutions_section sec ON e.section_id = sec.id
                ON CONFLICT (estudiante_id, periodo_id, fecha_calculo) DO NOTHING
            """)
            self.stdout.write(self.style.SUCCESS(
                f"Migrados {cursor.rowcount} risk scores"
            ))
            
            # Migrar attendance_attendance → fact_asistencia
            self.stdout.write("Migrando asistencias...")
            cursor.execute("""
                INSERT INTO fact_asistencia (
                    estudiante_id, periodo_id, seccion_id, docente_id, asignatura_id,
                    horario_id, attendance_date, day_of_week,
                    attendance_status_id, attendance_status_code,
                    absence_type_id, absence_type_code, observation
                )
                SELECT 
                    att.enrollment_id,
                    att.academic_period_id,
                    tss.subject_offering.section_id,
                    tss.user_id,
                    so.subject_academic_config.subject_id,
                    att.class_schedule_id,
                    att.attendance_date,
                    EXTRACT(ISODOW FROM att.attendance_date)::INT,
                    ast.id,
                    ast.code,
                    at.id,
                    at.code,
                    att.observation
                FROM attendance_attendance att
                JOIN attendance_attendance_status ast ON att.attendance_status_id = ast.id
                LEFT JOIN attendance_absence_type at ON att.absence_type_id = at.id
                JOIN academic_teacher_subject_section tss 
                    ON att.teacher_subject_section_id = tss.id
                JOIN academic_subject_offering so ON tss.subject_offering_id = so.id
                ON CONFLICT DO NOTHING
            """)
            self.stdout.write(self.style.SUCCESS(
                f"Migradas {cursor.rowcount} asistencias"
            ))
            
            # Migrar grading_student_note → fact_calificacion
            self.stdout.write("Migrando calificaciones...")
            cursor.execute("""
                INSERT INTO fact_calificacion (
                    estudiante_id, periodo_id, seccion_id, docente_id, asignatura_id,
                    evaluative_activity_id, activity_title, activity_type_id,
                    numeric_score, max_score, grading_mode
                )
                SELECT 
                    sn.enrollment_id,
                    eb.academic_period_id,
                    tss.subject_offering.section_id,
                    tss.user_id,
                    so.subject_academic_config.subject_id,
                    ea.id,
                    ea.title,
                    ea.activity_type_id,
                    sn.numeric_score,
                    ea.max_score,
                    sn.grading_mode
                FROM grading_student_note sn
                JOIN grading_evaluative_activity ea ON sn.evaluative_activity_id = ea.id
                JOIN grading_block_component bc ON ea.block_component_id = bc.id
                JOIN grading_evaluation_block eb ON bc.evaluation_block_id = eb.id
                JOIN academic_teacher_subject_section tss 
                    ON ea.teacher_subject_section_id = tss.id
                JOIN academic_subject_offering so ON tss.subject_offering_id = so.id
                ON CONFLICT (estudiante_id, evaluative_activity_id) DO NOTHING
            """)
            self.stdout.write(self.style.SUCCESS(
                f"Migradas {cursor.rowcount} calificaciones"
            ))
            
            # Migrar grading_period_grade_summary → fact_resumen_periodo
            self.stdout.write("Migrando resúmenes de período...")
            cursor.execute("""
                INSERT INTO fact_resumen_periodo (
                    estudiante_id, periodo_id, seccion_id, asignatura_id,
                    formative_avg, summative_avg, final_avg_truncated,
                    is_failing, promotion_status, calculated_at
                )
                SELECT 
                    pgs.enrollment_id,
                    pgs.academic_period_id,
                    so.section_id,
                    so.subject_academic_config.subject_id,
                    pgs.formative_avg,
                    pgs.summative_avg,
                    pgs.final_avg_truncated,
                    pgs.is_failing,
                    pgs.promotion_status,
                    pgs.calculated_at
                FROM grading_period_grade_summary pgs
                JOIN academic_subject_offering so ON pgs.subject_offering_id = so.id
                ON CONFLICT (estudiante_id, asignatura_id, periodo_id) DO NOTHING
            """)
            self.stdout.write(self.style.SUCCESS(
                f"Migrados {cursor.rowcount} resúmenes"
            ))
            
            # Migrar behavior_conduct_incident → fact_incidente_conducta
            self.stdout.write("Migrando incidentes de conducta...")
            cursor.execute("""
                INSERT INTO fact_incidente_conducta (
                    estudiante_id, periodo_id, seccion_id, incident_date,
                    incident_type_id, incident_type_code, incident_type_name,
                    severity_id, severity_code, severity_name,
                    family_notified, description, actions_taken
                )
                SELECT 
                    ci.enrollment_id,
                    ci.academic_period_id,
                    e.section_id,
                    ci.incident_date,
                    it.id,
                    it.code,
                    it.name,
                    s.id,
                    s.code,
                    s.name,
                    ci.family_notified,
                    ci.description,
                    ci.actions_taken
                FROM behavior_conduct_incident ci
                JOIN behavior_incident_type it ON ci.incident_type_id = it.id
                JOIN behavior_severity s ON ci.severity_id = s.id
                JOIN students_enrollment e ON ci.enrollment_id = e.id
                ON CONFLICT DO NOTHING
            """)
            self.stdout.write(self.style.SUCCESS(
                f"Migrados {cursor.rowcount} incidentes"
            ))
            
            # Migrar students_enrollment → fact_matricula
            self.stdout.write("Migrando matrículas...")
            cursor.execute("""
                INSERT INTO fact_matricula (
                    estudiante_id, seccion_id,
                    enrollment_status, enrollment_date, withdrawal_date,
                    withdrawal_reason_id, withdrawal_reason_code, withdrawal_reason_name,
                    is_repeat
                )
                SELECT 
                    e.student_id,
                    e.section_id,
                    e.enrollment_status,
                    e.enrollment_date,
                    e.withdrawal_date,
                    wr.id,
                    wr.code,
                    wr.name,
                    e.is_repeat
                FROM students_enrollment e
                LEFT JOIN students_withdrawal_reason wr ON e.withdrawal_reason_id = wr.id
                ON CONFLICT (estudiante_id, seccion_id) DO NOTHING
            """)
            self.stdout.write(self.style.SUCCESS(
                f"Migradas {cursor.rowcount} matrículas"
            ))
        
        self.stdout.write(self.style.SUCCESS("Migración completada"))
        self.stdout.write(self.style.WARNING(
            "Ahora ejecuta: python manage.py drop_obsolete_oltp_tables --confirm"
        ))
```

### Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Vistas materializadas desactualizadas | Media | Medio | Refresh cada 2h + botón "recalcular ahora" |
| Migración larga en producción | Alta | Alto | Ejecutar en horario nocturno, monitorear locks |
|Queries complejas en refresh | Media | Medio | Indexar columnas de join, particionar por período |

---

## Fase 2: Modelo Multi-Outcome (3-4 semanas)

### Objetivo
Extender el motor de predicción para predecir múltiples outcomes simultáneamente, no solo "reprobará/no reprobará".

### Entregables
1. **Modelo multi-output** que predice 4 outcomes
2. **API extendida** para exponer predicciones múltiples
3. **Dashboard actualizado** con breakdown de predicciones
4. **Baseline comparado** vs modelo actual

### Diseño técnico

#### 2.1 Definición de outcomes

```python
# apps/analytics/ml/outcomes.py

from dataclasses import dataclass
from enum import Enum


class OutcomeType(Enum):
    FAILING = "failing"  # Reprobará al menos 1 materia
    DROPOUT = "dropout"  # Desertará en próximos 30 días
    IMPROVEMENT = "improvement"  # Mejorará si interviene
    EXPECTED_GRADE = "expected_grade"  # Nota final esperada


@dataclass
class MultiOutcomePrediction:
    """Predicción multi-outcome para un estudiante."""
    student_id: int
    period_id: int
    
    # Probabilidades (0-1)
    p_failing: float
    p_dropout: float
    p_improvement: float
    
    # Nota esperada (0-10)
    expected_grade: float
    
    # Confidence intervals (95%)
    confidence_failing: tuple[float, float]
    confidence_dropout: tuple[float, float]
    confidence_grade: tuple[float, float]
    
    # Metadata
    model_version: str
    predicted_at: str
```

#### 2.2 Dataset de entrenamiento multi-outcome

```python
# apps/analytics/ml/train_multi_outcome.py

import pandas as pd
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from django.db import connection


def build_multi_outcome_dataset(period_id):
    """
    Construye dataset con múltiples targets desde tablas OLAP.
    
    Returns:
        X: Features (desde fact_riesgo_estudiante)
        y: DataFrame con 4 columnas target
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.estudiante_id,
                f.asistencia_pct,
                f.max_faltas_consecutivas,
                f.tardanzas,
                f.faltas_justificadas,
                f.faltas_injustificadas,
                f.promedio_pond,
                f.tendencia_notas,
                f.materias_reprobadas,
                f.conduct_score,
                f.incidentes_graves,
                f.tiene_nee,
                f.es_repetidor,
                -- Targets
                CASE WHEN f.materias_reprobadas > 0 THEN 1 ELSE 0 END as target_failing,
                CASE WHEN f.estado_matricula = 'RET' THEN 1 ELSE 0 END as target_dropout,
                -- Target improvement: comparar con período anterior
                0 as target_improvement,  -- Se calcula después
                f.promedio_pond as target_grade
            FROM fact_riesgo_estudiante f
            WHERE f.periodo_id = %s
                AND f.fecha_calculo = (
                    SELECT MAX(fecha_calculo) 
                    FROM fact_riesgo_estudiante 
                    WHERE estudiante_id = f.estudiante_id 
                        AND periodo_id = f.periodo_id
                )
        """, [period_id])
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    df = pd.DataFrame(rows)
    
    # Calcular target_improvement comparando con período anterior
    # (requiere datos de períodos anteriores en OLAP)
    
    feature_cols = [
        "asistencia_pct", "max_faltas_consecutivas", "tardanzas",
        "faltas_justificadas", "faltas_injustificadas",
        "promedio_pond", "tendencia_notas", "materias_reprobadas",
        "conduct_score", "incidentes_graves", "tiene_nee", "es_repetidor",
    ]
    target_cols = ["target_failing", "target_dropout", "target_improvement", "target_grade"]
    
    X = df[feature_cols]
    y = df[target_cols]
    
    return X, y


def train_multi_outcome_model(period_id):
    """Entrena modelo multi-output desde datos OLAP."""
    X, y = build_multi_outcome_dataset(period_id)
    
    # Modelo para clasificación (3 outcomes binarios)
    classifier = MultiOutputRegressor(
        GradientBoostingClassifier(n_estimators=100, random_state=42)
    )
    classifier.fit(X, y[["target_failing", "target_dropout", "target_improvement"]])
    
    # Modelo para regresión (1 outcome continuo)
    regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
    regressor.fit(X, y["target_grade"])
    
    artifact = {
        "classifier": classifier,
        "regressor": regressor,
        "features": list(X.columns),
        "model_version": "multi-outcome-v1",
    }
    
    joblib.dump(artifact, MODEL_PATH_MULTI_OUTCOME)
    return artifact
```

#### 2.3 Inferencia multi-outcome

```python
# apps/analytics/ml/predict_multi_outcome.py

import joblib
import pandas as pd
from pathlib import Path

MODEL_PATH_MULTI_OUTCOME = Path(__file__).parent / "multi_outcome_model.joblib"


def predict_multi_outcome(features_dict):
    """
    Predice múltiples outcomes para un estudiante.
    
    Args:
        features_dict: Dict con 15 features (mismo formato que modelo actual)
    
    Returns:
        MultiOutcomePrediction
    """
    if not MODEL_PATH_MULTI_OUTCOME.exists():
        return None
    
    artifact = joblib.load(MODEL_PATH_MULTI_OUTCOME)
    classifier = artifact["classifier"]
    regressor = artifact["regressor"]
    feature_cols = artifact["features"]
    
    X = pd.DataFrame([features_dict], columns=feature_cols)
    
    # Predicciones
    probas = classifier.predict_proba(X)
    grade_pred = regressor.predict(X)[0]
    
    # Extraer probabilidades (asumiendo binary classification)
    p_failing = probas[0][1]  # P(target_failing=1)
    p_dropout = probas[1][1]  # P(target_dropout=1)
    p_improvement = probas[2][1]  # P(target_improvement=1)
    
    # Confidence intervals (bootstrap simplificado)
    # En producción: usar conformal prediction o Bayesian bootstrap
    confidence_failing = (max(0, p_failing - 0.1), min(1, p_failing + 0.1))
    confidence_dropout = (max(0, p_dropout - 0.1), min(1, p_dropout + 0.1))
    confidence_grade = (max(0, grade_pred - 1.0), min(10, grade_pred + 1.0))
    
    return MultiOutcomePrediction(
        student_id=features_dict.get("student_id"),
        period_id=features_dict.get("period_id"),
        p_failing=p_failing,
        p_dropout=p_dropout,
        p_improvement=p_improvement,
        expected_grade=grade_pred,
        confidence_failing=confidence_failing,
        confidence_dropout=confidence_dropout,
        confidence_grade=confidence_grade,
        model_version=artifact["model_version"],
        predicted_at=timezone.now().isoformat(),
    )
```

#### 2.4 Integración con risk_engine

```python
# apps/analytics/student_risk/domain/risk_engine.py (extender)

def calculate_risk_multi_outcome(snapshot, metrics=None, config=None):
    """
    Calcula riesgo con predicciones multi-outcome.
    
    Returns:
        Dict con estructura extendida:
        {
            "estudiante_id": ...,
            "periodo": ...,
            "semaforo_riesgo": {...},  # Mismo que antes
            "predicciones": {
                "p_reprobar": 0.75,
                "p_desertar": 0.30,
                "p_mejorar": 0.20,
                "nota_esperada": 6.5,
                "confidence_intervals": {...}
            },
            "detalle_por_variable": {...},
            "model_version": "multi-outcome-v1"
        }
    """
    # Calcular riesgo base (lógica actual)
    base_analysis = calculate_risk(snapshot, metrics, config)
    
    # Agregar predicciones multi-outcome
    from apps.analytics.ml.predict_multi_outcome import predict_multi_outcome
    
    features = _feature_vector(snapshot, metrics)
    multi_pred = predict_multi_outcome(features)
    
    if multi_pred:
        base_analysis["predicciones"] = {
            "p_reprobar": round(multi_pred.p_failing, 3),
            "p_desertar": round(multi_pred.p_dropout, 3),
            "p_mejorar": round(multi_pred.p_improvement, 3),
            "nota_esperada": round(multi_pred.expected_grade, 2),
            "confidence_intervals": {
                "reprobar": multi_pred.confidence_failing,
                "desertar": multi_pred.confidence_dropout,
                "nota": multi_pred.confidence_grade,
            },
        }
        base_analysis["model_version"] = multi_pred.model_version
    else:
        base_analysis["predicciones"] = None
    
    return base_analysis
```

#### 2.5 API extendida

```python
# apps/analytics/api/views.py (agregar endpoint)

class StudentRiskMultiOutcomeView(APIView):
    """Predicción multi-outcome para un estudiante."""
    
    permission_classes = [IsAuthenticated, HasPermission]
    
    def get(self, request, student_id, period_id):
        builder = AcademicRiskFeatureBuilder(student_id, period_id)
        snapshot = builder.build()
        metrics = builder.build_persistence_metrics(snapshot)
        
        analysis = calculate_risk_multi_outcome(snapshot, metrics)
        
        return ok_response({
            "student_id": student_id,
            "period_id": period_id,
            "risk_level": analysis["semaforo_riesgo"]["nivel"],
            "predictions": analysis.get("predicciones"),
            "critical_factors": analysis["semaforo_riesgo"]["factores_criticos"],
            "recommendations": analysis["semaforo_riesgo"]["recomendaciones"],
        })
```

### Checklist de implementación

- [ ] Definir outcomes y estructura `MultiOutcomePrediction`
- [ ] Implementar `build_multi_outcome_dataset` para extraer targets históricos
- [ ] Entrenar modelo multi-output con datos existentes
- [ ] Implementar `predict_multi_outcome` para inferencia
- [ ] Extender `risk_engine.py` con `calculate_risk_multi_outcome`
- [ ] Agregar endpoint API `/api/analytics/students/{id}/risk-multi-outcome/`
- [ ] Actualizar frontend para mostrar predicciones múltiples
- [ ] Benchmark: comparar accuracy vs modelo actual (baseline)
- [ ] Documentar en `apps/analytics/ml/MULTI_OUTCOME.md`

### Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Dataset insuficiente para multi-outcome | Alta | Alto | Empezar con 2 outcomes (failing + dropout), expandir después |
| Modelo sobreajustado | Media | Alto | Cross-validation estratificado, regularización |
| Targets mal definidos (dropout) | Media | Medio | Validar definición con stakeholders, usar proxy (enrollment_status) |

---

## Fase 3: Análisis Temporal (4-6 semanas)

### Objetivo
Capturar evolución temporal del riesgo mediante series temporales, permitiendo predecir tendencias y detectar cambios temprano.

### Entregables
1. **Snapshots periódicos** (no solo el último)
2. **Modelo de series temporales** (LSTM o Prophet)
3. **API de tendencias** (últimos 6 meses)
4. **Alertas de cambio** (cuando estudiante cambia de nivel)

### Diseño técnico

#### 3.1 Esquema OLAP: Snapshots históricos en fact_riesgo_estudiante

La tabla `fact_riesgo_estudiante` ya soporta múltiples snapshots por período gracias a su constraint `UNIQUE(estudiante_id, periodo_id, fecha_calculo)`. El ETL genera un nuevo registro cada vez que se ejecuta, capturando la evolución temporal automáticamente.

```sql
-- fact_riesgo_estudiante ya permite múltiples snapshots por período
-- UNIQUE(estudiante_id, periodo_id, fecha_calculo)

-- Ejemplo: consultar evolución de un estudiante
SELECT 
    fecha_calculo,
    score_riesgo,
    nivel_riesgo,
    asistencia_pct,
    promedio_pond,
    conduct_score
FROM fact_riesgo_estudiante
WHERE estudiante_id = 123 AND periodo_id = 1
ORDER BY fecha_calculo ASC;
```

#### 3.2 Task: ETL frecuente para capturar evolución temporal

```python
# apps/analytics/tasks.py (modificar)

@shared_task
def refresh_analytics_layer_frequent():
    """
    ETL frecuente: calcula riesgo y actualiza fact_riesgo_estudiante.
    Cada ejecución genera un nuevo snapshot con fecha actual.
    Ejecutado por Celery Beat cada 2 horas.
    """
    from django.core.management import call_command
    call_command("refresh_analytics_layer")


# config/celery.py (modificar CELERY_BEAT_SCHEDULE)

CELERY_BEAT_SCHEDULE = {
    # ... existing schedules ...
    "refresh-analytics-olap-frequent": {
        "task": "apps.analytics.tasks.refresh_analytics_layer_frequent",
        "schedule": crontab(minute=0, hour="*/2"),  # Cada 2 horas
    },
}
```

#### 3.3 Modelo de series temporales

```python
# apps/analytics/ml/temporal_model.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from django.db import connection


def build_temporal_dataset(student_id, period_id, lookback=8):
    """
    Construye dataset de series temporales desde fact_riesgo_estudiante (OLAP).
    
    Args:
        student_id: ID del estudiante
        period_id: ID del período
        lookback: Número de snapshots históricos a usar
    
    Returns:
        X: Secuencia de features (lookback, n_features)
        y: Target (próximo score de riesgo)
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                asistencia_pct,
                conduct_score,
                promedio_pond,
                materias_reprobadas,
                incidentes_graves,
                score_riesgo
            FROM fact_riesgo_estudiante
            WHERE estudiante_id = %s AND periodo_id = %s
            ORDER BY fecha_calculo ASC
        """, [student_id, period_id])
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    if len(rows) < lookback + 1:
        return None, None  # No hay suficientes datos
    
    # Extraer features
    features_list = []
    for row in rows:
        features = [
            float(row["asistencia_pct"]),
            float(row["conduct_score"]),
            float(row["promedio_pond"]),
            float(row["materias_reprobadas"]),
            float(row["incidentes_graves"]),
        ]
        features_list.append(features)
    
    # Crear secuencias (sliding window)
    X, y = [], []
    for i in range(len(features_list) - lookback):
        X.append(features_list[i:i+lookback])
        y.append(features_list[i+lookback][0])  # Predecir próximo attendance_rate
    
    return np.array(X), np.array(y)


def train_temporal_model(period_id):
    """Entrena modelo LSTM para predecir tendencias."""
    from apps.students.repositories.enrollment_repo import EnrollmentRepository
    
    enrollments = EnrollmentRepository.get_active_by_period(period_id)
    
    all_X, all_y = [], []
    for enrollment in enrollments:
        X, y = build_temporal_dataset(enrollment.student_id, period_id)
        if X is not None:
            all_X.append(X)
            all_y.append(y)
    
    if not all_X:
        raise ValueError("No hay suficientes datos temporales")
    
    X = np.vstack(all_X)
    y = np.concatenate(all_y)
    
    # Normalizar
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X.reshape(-1, X.shape[2])).reshape(X.shape)
    
    # Modelo LSTM
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer="adam", loss="mse")
    model.fit(X_scaled, y, epochs=50, batch_size=32, validation_split=0.2)
    
    artifact = {
        "model": model,
        "scaler": scaler,
        "lookback": X.shape[1],
        "model_version": "temporal-lstm-v1",
    }
    
    joblib.dump(artifact, MODEL_PATH_TEMPORAL)
    return artifact


def predict_trend(student_id, period_id, horizon=4):
    """
    Predice tendencia de riesgo para próximas N semanas.
    
    Args:
        student_id: ID del estudiante
        period_id: ID del período
        horizon: Número de semanas a predecir
    
    Returns:
        List de predicciones (score de riesgo para cada semana)
    """
    if not MODEL_PATH_TEMPORAL.exists():
        return None
    
    artifact = joblib.load(MODEL_PATH_TEMPORAL)
    model = artifact["model"]
    scaler = artifact["scaler"]
    lookback = artifact["lookback"]
    
    X, _ = build_temporal_dataset(student_id, period_id, lookback)
    if X is None:
        return None
    
    X_scaled = scaler.transform(X.reshape(-1, X.shape[2])).reshape(X.shape)
    
    # Predicción iterativa (auto-regresiva)
    predictions = []
    current_input = X_scaled
    
    for _ in range(horizon):
        pred = model.predict(current_input, verbose=0)[0, 0]
        predictions.append(pred)
        
        # Shift window (agregar predicción, remover primer elemento)
        next_step = np.zeros_like(current_input[:, -1:, :])
        next_step[:, 0, 0] = pred
        current_input = np.append(current_input[:, 1:, :], next_step, axis=1)
    
    # Desnormalizar
    predictions = scaler.inverse_transform(
        np.array(predictions).reshape(-1, 1)
    ).flatten()
    
    return predictions.tolist()
```

#### 3.4 Detección de cambios de nivel

```python
# apps/analytics/tasks.py (agregar)

@shared_task
def detect_risk_level_changes():
    """
    Detecta estudiantes que cambiaron de nivel de riesgo.
    Compara el último snapshot con el anterior en fact_riesgo_estudiante (OLAP).
    Genera alertas tempranas automáticamente.
    """
    from apps.analytics.early_alert.infrastructure.models import EarlyAlert, UrgencyLevelChoices
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Obtener pares de snapshots (actual vs anterior) por estudiante
        cursor.execute("""
            SELECT 
                actual.estudiante_id,
                actual.periodo_id,
                actual.nivel_riesgo as nivel_actual,
                anterior.nivel_riesgo as nivel_anterior,
                actual.score_riesgo as score_actual,
                anterior.score_riesgo as score_anterior
            FROM fact_riesgo_estudiante actual
            JOIN fact_riesgo_estudiante anterior
                ON actual.estudiante_id = anterior.estudiante_id
                AND actual.periodo_id = anterior.periodo_id
            WHERE actual.fecha_calculo = (
                SELECT MAX(fecha_calculo)
                FROM fact_riesgo_estudiante
                WHERE estudiante_id = actual.estudiante_id
                    AND periodo_id = actual.periodo_id
            )
            AND anterior.fecha_calculo = (
                SELECT MAX(fecha_calculo)
                FROM fact_riesgo_estudiante
                WHERE estudiante_id = actual.estudiante_id
                    AND periodo_id = actual.periodo_id
                    AND fecha_calculo < actual.fecha_calculo
            )
            AND actual.nivel_riesgo != anterior.nivel_riesgo
        """)
        
        changes = cursor.fetchall()
    
    for row in changes:
        estudiante_id, periodo_id, nivel_actual, nivel_anterior, score_actual, score_anterior = row
        
        # Determinar urgencia
        if nivel_actual == "rojo":
            urgency = UrgencyLevelChoices.HIGH
        elif nivel_actual == "amarillo":
            urgency = UrgencyLevelChoices.MEDIUM
        else:
            urgency = UrgencyLevelChoices.LOW
        
        # Crear alerta (si no existe una similar hoy)
        alert_exists = EarlyAlert.objects.filter(
            enrollment__student_id=estudiante_id,
            academic_period_id=periodo_id,
            alert_type="risk_level_change",
            detected_at__date=timezone.now().date(),
        ).exists()
        
        if not alert_exists:
            from apps.students.infrastructure.models import Enrollment
            enrollment = Enrollment.objects.get(
                student_id=estudiante_id,
                enrollment_status="ACT"
            )
            EarlyAlert.objects.create(
                enrollment=enrollment,
                academic_period_id=periodo_id,
                alert_type="risk_level_change",
                description=f"Estudiante cambió de nivel {nivel_anterior} → {nivel_actual}",
                urgency_level=urgency,
            )
```

#### 3.5 API de tendencias

```python
# apps/analytics/api/views.py (agregar)

class StudentRiskTrendView(APIView):
    """Tendencia de riesgo para un estudiante (desde OLAP)."""
    
    permission_classes = [IsAuthenticated, HasPermission]
    
    def get(self, request, student_id, period_id):
        from apps.analytics.ml.temporal_model import predict_trend
        from django.db import connection
        
        # Histórico real desde fact_riesgo_estudiante (OLAP)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    fecha_calculo,
                    score_riesgo,
                    nivel_riesgo,
                    asistencia_pct,
                    conduct_score,
                    promedio_pond
                FROM fact_riesgo_estudiante
                WHERE estudiante_id = %s AND periodo_id = %s
                ORDER BY fecha_calculo ASC
            """, [student_id, period_id])
            
            columns = [col[0] for col in cursor.description]
            history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Formatear fechas
        for h in history:
            h["date"] = h["fecha_calculo"].isoformat() if h["fecha_calculo"] else None
        
        # Predicción de tendencia (próximas 4 semanas)
        predictions = predict_trend(student_id, period_id, horizon=4)
        
        return ok_response({
            "student_id": student_id,
            "period_id": period_id,
            "history": history,
            "predictions": predictions,
        })
```

### Checklist de implementación

- [ ] Verificar que `fact_riesgo_estudiante` soporta múltiples snapshots (constraint UNIQUE ya existe)
- [ ] Configurar ETL frecuente (cada 2h) para capturar evolución temporal
- [ ] Implementar `build_temporal_dataset` leyendo desde `fact_riesgo_estudiante`
- [ ] Entrenar modelo LSTM con datos históricos de OLAP
- [ ] Implementar `predict_trend` para inferencia
- [ ] Implementar task `detect_risk_level_changes` leyendo de OLAP
- [ ] Agregar endpoint API `/api/analytics/students/{id}/risk-trend/`
- [ ] Actualizar frontend con gráfico de tendencia (Chart.js o Recharts)
- [ ] Documentar en `apps/analytics/ml/TEMPORAL_MODEL.md`

### Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| LSTM requiere muchos datos | Alta | Alto | Empezar con modelos más simples (ARIMA, Prophet) si hay < 100 estudiantes |
| Snapshots ocupan mucho espacio | Media | Medio | Particionar por período, archivar períodos antiguos |
| Predicciones poco precisas | Media | Medio | Validar con backtesting, ajustar hiperparámetros |

---

## Fase 4: Análisis Causal (2-3 meses)

### Objetivo
Identificar causas raíz de riesgo mediante análisis de mediación, permitiendo recomendaciones de intervención específicas.

### Entregables
1. **Modelo causal** que identifica cadenas causa-efecto
2. **Sistema de recomendaciones** basado en causa raíz
3. **Dashboard de causas** (no solo síntomas)
4. **Integración con alertas tempranas**

### Diseño técnico

#### 4.1 Framework de análisis causal

```python
# apps/analytics/causal/graph.py

from dataclasses import dataclass
from typing import List, Dict
import networkx as nx


@dataclass
class CausalNode:
    """Nodo en grafo causal."""
    variable: str
    label: str
    node_type: str  # "root_cause", "mediator", "outcome"


@dataclass
class CausalEdge:
    """Arista en grafo causal (relación causa-efecto)."""
    source: str
    target: str
    weight: float  # Fuerza de la relación (0-1)
    mediation_effect: float  # Efecto de mediación


class CausalGraph:
    """
    Grafo causal que representa relaciones entre variables de riesgo.
    
    Ejemplo:
        problema_transporte → falta_asistencia → bajo_rendimiento → riesgo_alto
        problema_familiar → falta_asistencia → bajo_rendimiento → riesgo_alto
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_relationship(self, source: str, target: str, weight: float):
        """Agrega relación causal."""
        self.graph.add_edge(source, target, weight=weight)
    
    def find_root_causes(self, outcome: str) -> List[str]:
        """
        Encuentra causas raíz de un outcome (nodos sin predecessors).
        """
        if outcome not in self.graph:
            return []
        
        # BFS hacia atrás para encontrar ancestros
        ancestors = nx.ancestors(self.graph, outcome)
        
        # Causas raíz = ancestros sin predecessors
        root_causes = [
            node for node in ancestors 
            if self.graph.in_degree(node) == 0
        ]
        
        return root_causes
    
    def compute_mediation_effects(self, outcome: str) -> Dict[str, float]:
        """
        Calcula efecto de mediación de cada variable intermedia.
        
        Ejemplo: Si A → B → C, ¿cuánto de A→C es mediado por B?
        """
        mediation_effects = {}
        
        for node in self.graph.nodes():
            if node == outcome:
                continue
            
            # Calcular paths de node a outcome
            paths = list(nx.all_simple_paths(self.graph, node, outcome))
            
            if not paths:
                continue
            
            # Efecto total = producto de pesos en path más fuerte
            total_effect = max(
                np.prod([self.graph[u][v]["weight"] for u, v in zip(path[:-1], path[1:])])
                for path in paths
            )
            
            mediation_effects[node] = total_effect
        
        return mediation_effects
```

#### 4.2 Aprendizaje de grafo causal desde datos

```python
# apps/analytics/causal/learn.py

from causallearn.search.ConstraintBased.PC import pc
from causallearn.utils.PCUtils import GraphUtils
import pandas as pd
from django.db import connection


def learn_causal_structure(period_id):
    """
    Aprende estructura causal desde datos OLAP usando PC algorithm.
    
    Returns:
        CausalGraph con relaciones aprendidas
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                asistencia_pct,
                conduct_score,
                promedio_pond,
                materias_reprobadas,
                incidentes_graves,
                tiene_nee,
                es_repetidor
            FROM fact_riesgo_estudiante
            WHERE periodo_id = %s
                AND fecha_calculo = (
                    SELECT MAX(fecha_calculo)
                    FROM fact_riesgo_estudiante f2
                    WHERE f2.estudiante_id = fact_riesgo_estudiante.estudiante_id
                        AND f2.periodo_id = %s
                )
        """, [period_id, period_id])
        
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    df = pd.DataFrame(rows)
    
    # PC algorithm (constraint-based causal discovery)
    cg = pc(df.values, alpha=0.05, indep_test="fisherz", stable=True, uc_rule=0, uc_priority=2)
    
    # Convertir a CausalGraph
    causal_graph = CausalGraph()
    
    for i, j in cg.G.get_edges():
        if cg.G[i][j]["weight"] > 0.5:  # Solo relaciones fuertes
            causal_graph.add_relationship(
                source=df.columns[i],
                target=df.columns[j],
                weight=cg.G[i][j]["weight"]
            )
    
    return causal_graph


def identify_root_causes_for_student(student_id, period_id):
    """
    Identifica causas raíz de riesgo para un estudiante específico desde OLAP.
    
    Returns:
        List de causas raíz con efectos de mediación
    """
    # Cargar grafo causal global (aprendido de datos OLAP del período)
    causal_graph = learn_causal_structure(period_id)
    
    # Obtener features del estudiante desde fact_riesgo_estudiante (OLAP)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                asistencia_pct,
                conduct_score,
                promedio_pond,
                materias_reprobadas,
                incidentes_graves,
                tiene_nee,
                es_repetidor
            FROM fact_riesgo_estudiante
            WHERE estudiante_id = %s AND periodo_id = %s
                AND fecha_calculo = (
                    SELECT MAX(fecha_calculo)
                    FROM fact_riesgo_estudiante
                    WHERE estudiante_id = %s AND periodo_id = %s
                )
        """, [student_id, period_id, student_id, period_id])
        
        row = cursor.fetchone()
    
    if not row:
        return []
    
    columns = ["asistencia_pct", "conduct_score", "promedio_pond", 
               "materias_reprobadas", "incidentes_graves", "tiene_nee", "es_repetidor"]
    student_data = dict(zip(columns, row))
    
    # Identificar variables problemáticas
    problem_variables = []
    if student_data["asistencia_pct"] < 70:
        problem_variables.append("asistencia_pct")
    if student_data["conduct_score"] < 5:
        problem_variables.append("conduct_score")
    if student_data["materias_reprobadas"] > 0:
        problem_variables.append("materias_reprobadas")
    
    # Para cada variable problemática, encontrar causas raíz
    root_causes = []
    for var in problem_variables:
        causes = causal_graph.find_root_causes(var)
        mediation = causal_graph.compute_mediation_effects(var)
        
        for cause in causes:
            root_causes.append({
                "cause": cause,
                "affected_variable": var,
                "mediation_effect": mediation.get(cause, 0),
            })
    
    # Ordenar por efecto de mediación (más impacto primero)
    root_causes.sort(key=lambda x: x["mediation_effect"], reverse=True)
    
    return root_causes
```

#### 4.3 Sistema de recomendaciones basado en causas

```python
# apps/analytics/causal/recommendations.py

CAUSE_TO_INTERVENTION = {
    "has_special_needs": {
        "label": "Necesidades educativas especiales",
        "interventions": [
            "Coordinar con departamento de NEE para plan de adaptación",
            "Asignar tutoría especializada",
            "Evaluar recursos de apoyo adicionales",
        ],
    },
    "is_repeat": {
        "label": "Estudiante repitente",
        "interventions": [
            "Reunión con representante para identificar dificultades previas",
            "Plan de nivelación en materias críticas",
            "Monitoreo quincenal de progreso",
        ],
    },
    "low_attendance_root": {
        "label": "Problemas de asistencia (causa raíz)",
        "interventions": [
            "Entrevista con representante para identificar causa (transporte, salud, familiar)",
            "Coordinar con DECE si es problema socioemocional",
            "Evaluar opciones de transporte escolar si aplica",
        ],
    },
    "low_conduct_root": {
        "label": "Problemas de conducta (causa raíz)",
        "interventions": [
            "Reunión con DECE para evaluación socioemocional",
            "Implementar plan de mejora conductual con docente tutor",
            "Coordinar con representante para seguimiento en casa",
        ],
    },
}


def generate_causal_recommendations(root_causes):
    """
    Genera recomendaciones de intervención basadas en causas raíz.
    
    Args:
        root_causes: Lista de causas raíz con efectos de mediación
    
    Returns:
        List de recomendaciones priorizadas
    """
    recommendations = []
    
    for cause_data in root_causes[:3]:  # Top 3 causas
        cause = cause_data["cause"]
        mediation = cause_data["mediation_effect"]
        
        if cause in CAUSE_TO_INTERVENTION:
            intervention_data = CAUSE_TO_INTERVENTION[cause]
            recommendations.append({
                "cause": intervention_data["label"],
                "mediation_effect": round(mediation, 3),
                "interventions": intervention_data["interventions"],
                "priority": "alta" if mediation > 0.5 else "media",
            })
    
    return recommendations
```

#### 4.4 API de análisis causal

```python
# apps/analytics/api/views.py (agregar)

class StudentCausalAnalysisView(APIView):
    """Análisis causal de riesgo para un estudiante."""
    
    permission_classes = [IsAuthenticated, HasPermission]
    
    def get(self, request, student_id, period_id):
        from apps.analytics.causal.learn import identify_root_causes_for_student
        from apps.analytics.causal.recommendations import generate_causal_recommendations
        
        # Identificar causas raíz
        root_causes = identify_root_causes_for_student(student_id, period_id)
        
        # Generar recomendaciones
        recommendations = generate_causal_recommendations(root_causes)
        
        return ok_response({
            "student_id": student_id,
            "period_id": period_id,
            "root_causes": [
                {
                    "cause": rc["cause"],
                    "affected_variable": rc["affected_variable"],
                    "mediation_effect": rc["mediation_effect"],
                }
                for rc in root_causes
            ],
            "recommendations": recommendations,
        })
```

### Checklist de implementación

- [ ] Instalar dependencias: `causal-learn`, `networkx`
- [ ] Implementar `CausalGraph` con operaciones básicas
- [ ] Implementar `learn_causal_structure` con PC algorithm
- [ ] Implementar `identify_root_causes_for_student`
- [ ] Definir mapping `CAUSE_TO_INTERVENTION` con stakeholders
- [ ] Implementar `generate_causal_recommendations`
- [ ] Agregar endpoint API `/api/analytics/students/{id}/causal-analysis/`
- [ ] Validar grafo causal con expertos (docentes, DECE)
- [ ] Actualizar frontend con visualización de grafo causal (D3.js)
- [ ] Documentar en `apps/analytics/causal/CAUSAL_ANALYSIS.md`

### Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| PC algorithm requiere muchos datos | Alta | Alto | Usar método más simple (correlación + dominio experto) si n < 200 |
| Grafo causal incorrecto | Media | Alto | Validar con expertos, permitir edición manual |
| Recomendaciones genéricas | Media | Medio | Personalizar con contexto institucional (entrevistas con docentes) |

---

## Roadmap Consolidado

| Fase | Duración | Dependencias | Entregable clave |
|---|---|---|---|
| **Fase 1: OLAP** | 2-3 semanas | Ninguna | Tablas OLAP reemplazan OLTP de análisis + ETL desde fuentes reales + eliminación de tablas obsoletas |
| **Fase 2: Multi-Outcome** | 3-4 semanas | Fase 1 | Modelo predice 4 outcomes simultáneos (lee de OLAP) |
| **Fase 3: Temporal** | 4-6 semanas | Fase 1 | Evolución temporal desde OLAP + predicción de tendencias |
| **Fase 4: Causal** | 2-3 meses | Fase 2, 3 | Análisis de causas raíz + recomendaciones (lee de OLAP) |

**Total estimado:** 4-6 meses (con overlap parcial entre fases)

### Orden de ejecución

```
1. Crear tablas OLAP (dimensiones + hechos)
2. Implementar ETL (calcula desde fuentes OLTP reales → OLAP)
3. Migrar datos existentes (OLTP análisis → OLAP)
4. Validar que dashboards leen correctamente de OLAP
5. Eliminar tablas OLTP de análisis obsoletas
6. Continuar con Fases 2, 3, 4 (todas leen de OLAP)
```

---

## Métricas de éxito

### Fase 1
- [ ] Queries de dashboard < 100ms (actualmente ~500ms)
- [ ] Soporte para > 10,000 estudiantes sin degradación
- [ ] Refresh automático cada 2h sin intervención manual

### Fase 2
- [ ] Accuracy multi-outcome > 75% (vs 70% baseline actual)
- [ ] Predicción de dropout con recall > 80% (capturar 8 de 10 desertores)
- [ ] API responde en < 200ms

### Fase 3
- [ ] Detección de cambios de nivel con < 24h de延迟
- [ ] Predicción de tendencia con MAE < 10% (error < 10 puntos)
- [ ] Gráfico de tendencia visible en dashboard

### Fase 4
- [ ] Causas raíz identificadas con precisión > 70% (validación con expertos)
- [ ] Recomendaciones de intervención implementadas en > 50% de casos
- [ ] Reducción de 15% en tasa de deserción (medido en 1 año lectivo)

---

## Consideraciones técnicas

### Stack tecnológico

**Actual:**
- Django 4.x + DRF
- PostgreSQL 15
- scikit-learn (GradientBoosting)
- Celery + Redis

**Nuevo (agregar):**
- PostgreSQL materialized views (ya incluido en PG 15)
- TensorFlow/Keras (LSTM para series temporales)
- causal-learn (análisis causal)
- networkx (grafos causales)
- SHAP (explicabilidad de modelos)

### Arquitectura de datos

**Tablas OLTP que se MANTIENEN** (fuente de verdad para escritura):
- `attendance_attendance`, `grading_student_note`, `grading_period_grade_summary`
- `behavior_conduct_incident`, `students_enrollment`, `students_student`
- `people_person`, `people_parish`, `people_city`
- `academic_class_schedule`, `academic_teacher_subject_section`
- `analytics_riskfactor`, `analytics_riskscoringconfig`, `analytics_earlyalert`

**Tablas OLTP que se ELIMINAN** (reemplazadas por OLAP):
- ~~`analytics_studentfeaturesnapshot`~~ → `fact_riesgo_estudiante`
- ~~`analytics_studentriskscore`~~ → `fact_riesgo_estudiante`
- ~~`analytics_studentriskfactor`~~ → (si se necesita, tabla nueva en OLAP)

**Tablas OLAP** (fuente de verdad para lectura/dashboards):
- `fact_riesgo_estudiante`, `fact_asistencia`, `fact_calificacion`
- `fact_resumen_periodo`, `fact_incidente_conducta`, `fact_matricula`
- `dim_estudiante`, `dim_docente`, `dim_asignatura`, `dim_horario`
- `dim_seccion`, `dim_grado_academico`, `dim_geografia`, `dim_tiempo`
- `dim_periodo_academico`, `dim_tipo_evento`

### Flujo de datos

```
┌──────────────┐      ┌─────────┐      ┌─────────┐      ┌──────────────┐
│  App Web     │ ───► │  OLTP   │ ───► │   ETL   │ ───► │     OLAP     │
│ (escritura)  │      │(fuente) │      │(Celery) │      │(fuente de   │
└──────────────┘      └─────────┘      └─────────┘      │  verdad para│
                                                         │  dashboards)│
                                                         └──────────────┘
                                                                │
                                                                ▼
                                                         ┌──────────────┐
                                                         │  Dashboards  │
                                                         │  (lectura)   │
                                                         └──────────────┘
```

### Infraestructura

**Requisitos adicionales:**
- GPU opcional (acelera entrenamiento LSTM 5-10x)
- Almacenamiento: +50 GB para datos OLAP históricos (estimado para 5,000 estudiantes × 3 años)
- Backup: tablas OLAP + modelos entrenados

### Seguridad y privacidad

- Tablas OLAP contienen datos sensibles → mismas políticas de acceso que tablas transaccionales
- Modelos ML no exponen datos de entrenamiento, solo predicciones
- Análisis causal puede revelar patrones demográficos → revisar con comité de ética

---

## Próximos pasos inmediatos

1. **Revisar este plan con stakeholders** (docentes, DECE, dirección)
2. **Priorizar fases** según necesidades institucionales
3. **Asignar recursos** (desarrollador backend + data scientist part-time)
4. **Comenzar Fase 1** (menor riesgo, mayor impacto inmediato)

---

## Referencias

- Kim, R., et al. (2020). "Temporal Dependency Modeling for Student Performance Prediction"
- Zhang, K., et al. (2022). "Causal Discovery in Educational Data Mining"
- Lundberg, S.M., Lee, S.I. (2017). "A Unified Approach to Interpreting Model Predictions" (SHAP)
- Spirtes, P., et al. (2000). "Causation, Prediction, and Search" (PC algorithm)

---

**Documento creado:** 2026-03-07  
**Última actualización:** 2026-03-07  
**Versión:** 2.0 — Arquitectura OLAP reemplaza tablas OLTP de análisis
