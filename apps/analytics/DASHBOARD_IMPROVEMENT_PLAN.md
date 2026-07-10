# Plan de Mejora: Dashboard del Director

## Resumen Ejecutivo

Este documento describe el plan para mejorar el dashboard del director, agregando nuevos análisis geográficos, de rendimiento por docente/materia/horario usando vistas materializadas sobre las tablas OLTP existentes. Tiempo estimado: **3-5 días**.

---

## 1. Análisis del Estado Actual

### 1.1 KPIs actuales en el Dashboard del Director

| Sección | Datos mostrados | Fuente |
|---|---|---|
| **Stats Cards** (4) | Total estudiantes, Asistencia global, Promedio formativo, Alertas activas | `StudentFeatureSnapshot`, `EarlyAlert` |
| **Evolución Matrículas** | Gráfico de barras por mes | `Enrollment` agrupado por mes |
| **Distribución Riesgo** | Barras rojo/amarillo/verde | `StudentRiskScore` |
| **Materias con Fracaso** | Top 5 materias con más reprobación | `PeriodGradeSummary` |
| **Factores de Riesgo** | Peso promedio de cada factor | `StudentRiskFactor` |
| **Alertas sin Atender** | Conteo por urgencia (critical/high/medium/low) | `EarlyAlert` |
| **Estudiantes Cerca del Umbral** | Lista de estudiantes a punto de cambiar de nivel | `StudentRiskScore` |
| **Estudiantes en Declive** | Top 5 con peor tendencia | `StudentFeatureSnapshot.grade_trend_slope` |
| **Riesgo por Ciudad** | Distribución por ciudad (opcional) | `StudentRiskScore` + `Person.city` |
| **Alertas Críticas** | Top 5 alertas no atendidas | `EarlyAlert` |
| **Incidentes Recientes** | Top 5 incidentes de conducta | `ConductIncident` |
| **Brecha NEE** | Comparativa con/sin NEE (opcional) | `StudentFeatureSnapshot` |

### 1.2 Problemas identificados

| # | Problema | Impacto | Estado |
|---|---|---|---|
| P1 | **Evolución de matrículas incorrecta** — Muestra puntos por mes, pero las matrículas se concentran en fechas específicas, mostrando solo 1-2 puntos | No se puede ver la evolución real ni comparar años lectivos | ✅ CORREGIDO |
| P2 | **Sin opción "Todos" para años lectivos** — No se puede ver el año lectivo completo y compararlo con otros | No hay forma de comparar años lectivos entre sí | ✅ CORREGIDO |
| P3 | **Sin análisis por parroquia** — Solo se muestra por ciudad, sin drill-down geográfico | No se puede identificar zonas específicas con mayor riesgo | Pendiente |
| P4 | **Sin rendimiento por docente** — No hay ranking ni comparativa de docentes | No se puede identificar docentes que necesitan apoyo | Pendiente |
| P5 | **Sin rendimiento por materia detallado** — Solo top 5 materias con fracaso | No hay promedio, desviación, ranking de dificultad por grado | Pendiente |
| P6 | **Sin análisis por horario** — No se sabe qué día/hora hay peor asistencia | No se pueden optimizar horarios o identificar patrones | Pendiente |
| P7 | **Sin comparativa urbano vs rural** — No se comparan zonas | No se pueden diseñar intervenciones diferenciadas | Pendiente |
| P8 | **Sin deserción por parroquia** — No se sabe de dónde desertan | No se pueden focalizar esfuerzos de retención | Pendiente |
| P9 | **Queries lentas** — Cada consulta recalcula desde tablas OLTP normalizadas | Dashboard puede tardar 500ms-2s en cargar | Pendiente |
| P10 | **Frontend: todo en un solo archivo** — `DirectorDashboard.tsx` tiene 521 líneas | Difícil de mantener, sin componentes reutilizables | Pendiente |
| P11 | **Sin tabs/secciones** — Todo el contenido en una sola página larga | Usuario tiene que hacer mucho scroll | Pendiente |
| P12 | **Sin exportación** — No se pueden exportar los datos | No se pueden generar reportes para el Ministerio | Pendiente |

### 1.3 Correcciones aplicadas

#### Corrección 1: Evolución de Matrículas Comparativa

**Problema:** La gráfica anterior mostraba matrículas por mes, pero como las matrículas se hacen en fechas específicas (inicio de año), solo se veían 1-2 puntos.

**Solución:** 
- Nueva gráfica comparativa de **total de matrículas por año lectivo**
- Selector de años lectivos con opción **"Todos los años"**
- Al seleccionar un año específico, se muestra la **evolución acumulada** de matrículas dentro de ese año

**Backend:**
- `get_enrollment_comparison_by_school_year()` — Devuelve total de matrículas por año lectivo
- `get_enrollment_cumulative_by_school_year()` — Devuelve evolución acumulada dentro de un año

**Frontend:**
- `EnrollmentComparisonChart` — Gráfica de barras comparativa entre años lectivos
- `CumulativeEnrollmentChart` — Gráfica de evolución acumulada al seleccionar un año
- Selector con botón "Todos los años" + botones por año lectivo

---

## 2. Plan de Mejora

### 2.1 Backend: Vistas materializadas sobre OLTP actual

Se crearán 7 vistas materializadas directamente sobre las tablas OLTP existentes, sin necesidad de crear nuevas tablas intermedias.

#### Vista 1: Riesgo por Parroquia

```sql
CREATE MATERIALIZED VIEW mv_director_risk_by_parish AS
SELECT 
    r.academic_period_id AS periodo_id,
    par.id AS parish_id,
    par.name AS parish_name,
    par.parish_type,
    cit.id AS city_id,
    cit.name AS city_name,
    COUNT(*) AS total_estudiantes,
    AVG(r.risk_score) AS score_promedio,
    AVG(s.attendance_rate) AS asistencia_promedio,
    AVG(s.formative_avg_normalized) AS promedio_promedio,
    AVG(s.conduct_score) AS conduct_promedio,
    COUNT(CASE WHEN r.risk_label = 'rojo' THEN 1 END) AS count_rojo,
    COUNT(CASE WHEN r.risk_label = 'amarillo' THEN 1 END) AS count_amarillo,
    COUNT(CASE WHEN r.risk_label = 'verde' THEN 1 END) AS count_verde,
    ROUND(COUNT(CASE WHEN r.risk_label = 'rojo' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tasa_riesgo_alto_pct,
    ROUND(COUNT(CASE WHEN e.enrollment_status = 'RET' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tasa_desercion_pct
FROM analytics_studentriskscore r
JOIN analytics_studentfeaturesnapshot s 
    ON r.enrollment_id = s.enrollment_id 
    AND r.academic_period_id = s.academic_period_id
    AND s.is_current = true
JOIN students_enrollment e ON r.enrollment_id = e.id
JOIN students_student st ON e.student_id = st.id
JOIN iam_user u ON st.user_id = u.id
JOIN people_person per ON u.person_id = per.id
LEFT JOIN people_parish par ON per.parish_id = par.id
LEFT JOIN people_city cit ON par.city_id = cit.id
GROUP BY r.academic_period_id, par.id, par.name, par.parish_type, cit.id, cit.name;
```

#### Vista 2: Rendimiento por Docente

```sql
CREATE MATERIALIZED VIEW mv_director_teacher_performance AS
SELECT 
    pgs.academic_period_id AS periodo_id,
    tss.user_id AS docente_id,
    u.username,
    per.names || ' ' || per.last_names AS docente_nombre,
    COUNT(DISTINCT pgs.enrollment_id) AS total_estudiantes,
    AVG(pgs.final_avg_truncated) AS promedio_general,
    AVG(pgs.formative_avg) AS promedio_formativo,
    AVG(pgs.summative_avg) AS promedio_sumativo,
    COUNT(CASE WHEN pgs.is_failing THEN 1 END) AS estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN pgs.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tasa_reprobacion_pct,
    RANK() OVER (
        PARTITION BY pgs.academic_period_id 
        ORDER BY AVG(pgs.final_avg_truncated) DESC
    ) AS ranking_periodo
FROM grading_period_grade_summary pgs
JOIN academic_subject_offering so ON pgs.subject_offering_id = so.id
JOIN academic_teacher_subject_section tss ON so.id = tss.subject_offering_id
JOIN iam_user u ON tss.user_id = u.id
JOIN people_person per ON u.person_id = per.id
GROUP BY pgs.academic_period_id, tss.user_id, u.username, per.names, per.last_names;
```

#### Vista 3: Rendimiento por Materia

```sql
CREATE MATERIALIZED VIEW mv_director_subject_performance AS
SELECT 
    pgs.academic_period_id AS periodo_id,
    sub.id AS asignatura_id,
    sub.name AS asignatura_nombre,
    sub.code AS asignatura_codigo,
    ag.id AS grado_id,
    ag.name AS grado_nombre,
    COUNT(DISTINCT pgs.enrollment_id) AS total_estudiantes,
    AVG(pgs.final_avg_truncated) AS promedio_general,
    AVG(pgs.formative_avg) AS promedio_formativo,
    AVG(pgs.summative_avg) AS promedio_sumativo,
    MIN(pgs.final_avg_truncated) AS nota_minima,
    MAX(pgs.final_avg_truncated) AS nota_maxima,
    STDDEV(pgs.final_avg_truncated) AS desviacion_estandar,
    COUNT(CASE WHEN pgs.is_failing THEN 1 END) AS estudiantes_reprobados,
    ROUND(COUNT(CASE WHEN pgs.is_failing THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tasa_reprobacion_pct,
    RANK() OVER (
        PARTITION BY pgs.academic_period_id, ag.id 
        ORDER BY AVG(pgs.final_avg_truncated) ASC
    ) AS ranking_dificultad
FROM grading_period_grade_summary pgs
JOIN academic_subject_offering so ON pgs.subject_offering_id = so.id
JOIN academic_subject_academic_config sac ON so.subject_academic_config_id = sac.id
JOIN academic_subject sub ON sac.subject_id = sub.id
JOIN institutions_section sec ON so.section_id = sec.id
JOIN institutions_academic_grade ag ON sec.academic_grade_id = ag.id
GROUP BY pgs.academic_period_id, sub.id, sub.name, sub.code, ag.id, ag.name;
```

#### Vista 4: Asistencia por Día de Semana

```sql
CREATE MATERIALIZED VIEW mv_director_attendance_by_day AS
SELECT 
    att.academic_period_id AS periodo_id,
    EXTRACT(ISODOW FROM att.attendance_date)::INT AS day_of_week,
    CASE EXTRACT(ISODOW FROM att.attendance_date)::INT
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
        WHEN 7 THEN 'Domingo'
    END AS dia_nombre,
    COUNT(*) AS total_registros,
    COUNT(CASE WHEN ast.code = 'P' THEN 1 END) AS presentes,
    COUNT(CASE WHEN ast.code = 'A' THEN 1 END) AS ausencias,
    COUNT(CASE WHEN ast.code = 'J' THEN 1 END) AS ausencias_justificadas,
    COUNT(CASE WHEN ast.code = 'T' THEN 1 END) AS tardanzas,
    ROUND(COUNT(CASE WHEN ast.code = 'P' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS asistencia_pct,
    ROUND(COUNT(CASE WHEN ast.code = 'T' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tardanza_pct
FROM attendance_attendance att
JOIN attendance_attendance_status ast ON att.attendance_status_id = ast.id
GROUP BY att.academic_period_id, EXTRACT(ISODOW FROM att.attendance_date)::INT;
```

#### Vista 5: Asistencia por Franja Horaria

```sql
CREATE MATERIALIZED VIEW mv_director_attendance_by_schedule AS
SELECT 
    att.academic_period_id AS periodo_id,
    CASE 
        WHEN cs.start_time < '12:00:00' THEN 'mañana'
        WHEN cs.start_time < '18:00:00' THEN 'tarde'
        ELSE 'noche'
    END AS franja_horaria,
    COUNT(*) AS total_registros,
    COUNT(CASE WHEN ast.code = 'P' THEN 1 END) AS presentes,
    COUNT(CASE WHEN ast.code = 'A' THEN 1 END) AS ausencias,
    COUNT(CASE WHEN ast.code = 'T' THEN 1 END) AS tardanzas,
    ROUND(COUNT(CASE WHEN ast.code = 'P' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS asistencia_pct,
    ROUND(COUNT(CASE WHEN ast.code = 'T' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tardanza_pct
FROM attendance_attendance att
JOIN attendance_attendance_status ast ON att.attendance_status_id = ast.id
JOIN academic_class_schedule cs ON att.class_schedule_id = cs.id
GROUP BY att.academic_period_id, 
    CASE WHEN cs.start_time < '12:00:00' THEN 'mañana'
         WHEN cs.start_time < '18:00:00' THEN 'tarde'
         ELSE 'noche' END;
```

#### Vista 6: Deserción por Parroquia

```sql
CREATE MATERIALIZED VIEW mv_director_dropout_by_parish AS
SELECT 
    e.section_id,
    par.id AS parish_id,
    par.name AS parish_name,
    par.parish_type,
    cit.id AS city_id,
    cit.name AS city_name,
    COUNT(*) AS total_matriculas,
    COUNT(CASE WHEN e.enrollment_status = 'RET' THEN 1 END) AS retirados,
    ROUND(COUNT(CASE WHEN e.enrollment_status = 'RET' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tasa_desercion_pct
FROM students_enrollment e
JOIN students_student st ON e.student_id = st.id
JOIN iam_user u ON st.user_id = u.id
JOIN people_person per ON u.person_id = per.id
LEFT JOIN people_parish par ON per.parish_id = par.id
LEFT JOIN people_city cit ON par.city_id = cit.id
GROUP BY e.section_id, par.id, par.name, par.parish_type, cit.id, cit.name;
```

#### Vista 7: Comparativa Urbano vs Rural

```sql
CREATE MATERIALIZED VIEW mv_director_urban_rural AS
SELECT 
    r.academic_period_id AS periodo_id,
    par.parish_type,
    COUNT(*) AS total_estudiantes,
    AVG(r.risk_score) AS score_promedio,
    AVG(s.attendance_rate) AS asistencia_promedio,
    AVG(s.formative_avg_normalized) AS promedio_promedio,
    AVG(s.conduct_score) AS conduct_promedio,
    COUNT(CASE WHEN r.risk_label = 'rojo' THEN 1 END) AS count_rojo,
    ROUND(COUNT(CASE WHEN r.risk_label = 'rojo' THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) AS tasa_riesgo_alto_pct
FROM analytics_studentriskscore r
JOIN analytics_studentfeaturesnapshot s 
    ON r.enrollment_id = s.enrollment_id 
    AND r.academic_period_id = s.academic_period_id
    AND s.is_current = true
JOIN students_enrollment e ON r.enrollment_id = e.id
JOIN students_student st ON e.student_id = st.id
JOIN iam_user u ON st.user_id = u.id
JOIN people_person per ON u.person_id = per.id
LEFT JOIN people_parish par ON per.parish_id = par.id
WHERE par.parish_type IS NOT NULL
GROUP BY r.academic_period_id, par.parish_type;
```

### 2.2 Backend: Nuevos endpoints API

#### Nuevos métodos en `DashboardRepository`

```python
# apps/analytics/dashboard/infrastructure/repositories.py

class DashboardRepository:
    # ... métodos existentes ...

    @classmethod
    def get_risk_by_parish(cls, academic_period_id: int) -> list:
        """Riesgo por parroquia desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT parish_id, parish_name, parish_type, city_id, city_name,
                       total_estudiantes, score_promedio, asistencia_promedio,
                       promedio_promedio, conduct_promedio,
                       count_rojo, count_amarillo, count_verde,
                       tasa_riesgo_alto_pct, tasa_desercion_pct
                FROM mv_director_risk_by_parish
                WHERE periodo_id = %s
                ORDER BY tasa_riesgo_alto_pct DESC
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def get_teacher_performance(cls, academic_period_id: int) -> list:
        """Rendimiento por docente desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT docente_id, docente_nombre, username,
                       total_estudiantes, promedio_general, promedio_formativo,
                       promedio_sumativo, estudiantes_reprobados,
                       tasa_reprobacion_pct, ranking_periodo
                FROM mv_director_teacher_performance
                WHERE periodo_id = %s
                ORDER BY ranking_periodo ASC
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def get_subject_performance(cls, academic_period_id: int) -> list:
        """Rendimiento por materia desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT asignatura_id, asignatura_nombre, asignatura_codigo,
                       grado_id, grado_nombre, total_estudiantes,
                       promedio_general, promedio_formativo, promedio_sumativo,
                       nota_minima, nota_maxima, desviacion_estandar,
                       estudiantes_reprobados, tasa_reprobacion_pct, ranking_dificultad
                FROM mv_director_subject_performance
                WHERE periodo_id = %s
                ORDER BY ranking_dificultad ASC
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def get_attendance_by_day(cls, academic_period_id: int) -> list:
        """Asistencia por día de semana desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT day_of_week, dia_nombre, total_registros,
                       presentes, ausencias, ausencias_justificadas, tardanzas,
                       asistencia_pct, tardanza_pct
                FROM mv_director_attendance_by_day
                WHERE periodo_id = %s
                ORDER BY day_of_week
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def get_attendance_by_schedule(cls, academic_period_id: int) -> list:
        """Asistencia por franja horaria desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT franja_horaria, total_registros,
                       presentes, ausencias, tardanzas,
                       asistencia_pct, tardanza_pct
                FROM mv_director_attendance_by_schedule
                WHERE periodo_id = %s
                ORDER BY CASE franja_horaria 
                    WHEN 'mañana' THEN 1 
                    WHEN 'tarde' THEN 2 
                    ELSE 3 END
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def get_dropout_by_parish(cls, academic_period_id: int) -> list:
        """Deserción por parroquia desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT parish_id, parish_name, parish_type, city_id, city_name,
                       total_matriculas, retirados, tasa_desercion_pct
                FROM mv_director_dropout_by_parish
                WHERE periodo_id = %s
                ORDER BY tasa_desercion_pct DESC
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @classmethod
    def get_urban_rural_comparison(cls, academic_period_id: int) -> dict:
        """Comparativa urbano vs rural desde vista materializada."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT parish_type, total_estudiantes, score_promedio,
                       asistencia_promedio, promedio_promedio, conduct_promedio,
                       count_rojo, tasa_riesgo_alto_pct
                FROM mv_director_urban_rural
                WHERE periodo_id = %s
            """, [academic_period_id])
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            result = {}
            for row in rows:
                result[row["parish_type"]] = row
            return result
```

#### Nuevos endpoints en `DirectorDashboardService`

```python
# apps/analytics/dashboard/domain/services.py

class DirectorDashboardService:
    # ... métodos existentes ...

    @classmethod
    def get_risk_by_parish(cls, academic_period_id: int) -> list:
        return DashboardRepository.get_risk_by_parish(academic_period_id)

    @classmethod
    def get_teacher_performance(cls, academic_period_id: int) -> list:
        return DashboardRepository.get_teacher_performance(academic_period_id)

    @classmethod
    def get_subject_performance(cls, academic_period_id: int) -> list:
        return DashboardRepository.get_subject_performance(academic_period_id)

    @classmethod
    def get_attendance_by_day(cls, academic_period_id: int) -> list:
        return DashboardRepository.get_attendance_by_day(academic_period_id)

    @classmethod
    def get_attendance_by_schedule(cls, academic_period_id: int) -> list:
        return DashboardRepository.get_attendance_by_schedule(academic_period_id)

    @classmethod
    def get_dropout_by_parish(cls, academic_period_id: int) -> list:
        return DashboardRepository.get_dropout_by_parish(academic_period_id)

    @classmethod
    def get_urban_rural_comparison(cls, academic_period_id: int) -> dict:
        return DashboardRepository.get_urban_rural_comparison(academic_period_id)
```

#### Nuevas URLs

```python
# apps/analytics/dashboard/urls.py

urlpatterns = [
    # ... existing ...
    path("director/<int:period_id>/risk-by-parish/", DirectorRiskByParishView.as_view()),
    path("director/<int:period_id>/teacher-performance/", DirectorTeacherPerformanceView.as_view()),
    path("director/<int:period_id>/subject-performance/", DirectorSubjectPerformanceView.as_view()),
    path("director/<int:period_id>/attendance-by-day/", DirectorAttendanceByDayView.as_view()),
    path("director/<int:period_id>/attendance-by-schedule/", DirectorAttendanceByScheduleView.as_view()),
    path("director/<int:period_id>/dropout-by-parish/", DirectorDropoutByParishView.as_view()),
    path("director/<int:period_id>/urban-rural/", DirectorUrbanRuralView.as_view()),
]
```

### 2.3 Backend: Task de refresh

```python
# apps/analytics/tasks.py

@shared_task
def refresh_director_dashboard_views():
    """Refresca vistas materializadas del dashboard del director."""
    from django.db import connection
    views = [
        "mv_director_risk_by_parish",
        "mv_director_teacher_performance",
        "mv_director_subject_performance",
        "mv_director_attendance_by_day",
        "mv_director_attendance_by_schedule",
        "mv_director_dropout_by_parish",
        "mv_director_urban_rural",
    ]
    with connection.cursor() as cursor:
        for view in views:
            try:
                cursor.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}")
            except Exception as e:
                logger.warning(f"Error refrescando {view}: {e}")
                cursor.execute(f"REFRESH MATERIALIZED VIEW {view}")
```

```python
# config/celery.py

CELERY_BEAT_SCHEDULE = {
    # ... existing ...
    "refresh-director-views": {
        "task": "apps.analytics.tasks.refresh_director_dashboard_views",
        "schedule": crontab(minute=0, hour="*/2"),  # Cada 2 horas
    },
}
```

---

## 3. Frontend: Mejoras en DirectorDashboard

### 3.1 Estructura de componentes propuesta

```
dashboards/
├── DirectorDashboard.tsx              # Container principal con tabs
├── components/
│   ├── DirectorOverviewTab.tsx        # Tab: Resumen general
│   ├── DirectorGeographicTab.tsx      # Tab: Análisis geográfico
│   ├── DirectorTeacherTab.tsx         # Tab: Rendimiento docente
│   ├── DirectorSubjectTab.tsx         # Tab: Rendimiento por materia
│   ├── DirectorScheduleTab.tsx        # Tab: Análisis horario
│   ├── DirectorAlertsTab.tsx          # Tab: Alertas e incidentes
│   ├── StatCard.tsx                   # Componente reutilizable
│   ├── RiskBar.tsx                    # Componente reutilizable
│   ├── PctBar.tsx                     # Componente reutilizable
│   ├── DataTable.tsx                  # Tabla genérica con sorting
│   └── SectionCard.tsx                # Card con título y contenido
```

### 3.2 Nuevos tipos TypeScript

```typescript
// analytics.types.ts (agregar)

export interface RiskByParishT {
  parish_id: number;
  parish_name: string;
  parish_type: "URBANA" | "RURAL";
  city_id: number;
  city_name: string;
  total_estudiantes: number;
  score_promedio: number;
  asistencia_promedio: number;
  promedio_promedio: number;
  conduct_promedio: number;
  count_rojo: number;
  count_amarillo: number;
  count_verde: number;
  tasa_riesgo_alto_pct: number;
  tasa_desercion_pct: number;
}

export interface TeacherPerformanceT {
  docente_id: number;
  docente_nombre: string;
  username: string;
  total_estudiantes: number;
  promedio_general: number;
  promedio_formativo: number;
  promedio_sumativo: number;
  estudiantes_reprobados: number;
  tasa_reprobacion_pct: number;
  ranking_periodo: number;
}

export interface SubjectPerformanceT {
  asignatura_id: number;
  asignatura_nombre: string;
  asignatura_codigo: string;
  grado_id: number;
  grado_nombre: string;
  total_estudiantes: number;
  promedio_general: number;
  promedio_formativo: number;
  promedio_sumativo: number;
  nota_minima: number;
  nota_maxima: number;
  desviacion_estandar: number;
  estudiantes_reprobados: number;
  tasa_reprobacion_pct: number;
  ranking_dificultad: number;
}

export interface AttendanceByDayT {
  day_of_week: number;
  dia_nombre: string;
  total_registros: number;
  presentes: number;
  ausencias: number;
  ausencias_justificadas: number;
  tardanzas: number;
  asistencia_pct: number;
  tardanza_pct: number;
}

export interface AttendanceByScheduleT {
  franja_horaria: "mañana" | "tarde" | "noche";
  total_registros: number;
  presentes: number;
  ausencias: number;
  tardanzas: number;
  asistencia_pct: number;
  tardanza_pct: number;
}

export interface DropoutByParishT {
  parish_id: number;
  parish_name: string;
  parish_type: "URBANA" | "RURAL";
  city_id: number;
  city_name: string;
  total_matriculas: number;
  retirados: number;
  tasa_desercion_pct: number;
}

export interface UrbanRuralT {
  URBANA?: {
    total_estudiantes: number;
    score_promedio: number;
    asistencia_promedio: number;
    promedio_promedio: number;
    conduct_promedio: number;
    count_rojo: number;
    tasa_riesgo_alto_pct: number;
  };
  RURAL?: {
    total_estudiantes: number;
    score_promedio: number;
    asistencia_promedio: number;
    promedio_promedio: number;
    conduct_promedio: number;
    count_rojo: number;
    tasa_riesgo_alto_pct: number;
  };
}
```

### 3.3 Nuevos métodos en el service

```typescript
// analytics.service.ts (agregar)

class AnalyticsService {
  // ... métodos existentes ...

  async getRiskByParish(periodId: number): Promise<RiskByParishT[]> {
    const { data } = await apiClient.get<ResponseApi<RiskByParishT[]>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_RISK_BY_PARISH(periodId)
    );
    return data.data;
  }

  async getTeacherPerformance(periodId: number): Promise<TeacherPerformanceT[]> {
    const { data } = await apiClient.get<ResponseApi<TeacherPerformanceT[]>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_TEACHER_PERFORMANCE(periodId)
    );
    return data.data;
  }

  async getSubjectPerformance(periodId: number): Promise<SubjectPerformanceT[]> {
    const { data } = await apiClient.get<ResponseApi<SubjectPerformanceT[]>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_SUBJECT_PERFORMANCE(periodId)
    );
    return data.data;
  }

  async getAttendanceByDay(periodId: number): Promise<AttendanceByDayT[]> {
    const { data } = await apiClient.get<ResponseApi<AttendanceByDayT[]>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_ATTENDANCE_BY_DAY(periodId)
    );
    return data.data;
  }

  async getAttendanceBySchedule(periodId: number): Promise<AttendanceByScheduleT[]> {
    const { data } = await apiClient.get<ResponseApi<AttendanceByScheduleT[]>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_ATTENDANCE_BY_SCHEDULE(periodId)
    );
    return data.data;
  }

  async getDropoutByParish(periodId: number): Promise<DropoutByParishT[]> {
    const { data } = await apiClient.get<ResponseApi<DropoutByParishT[]>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_DROPOUT_BY_PARISH(periodId)
    );
    return data.data;
  }

  async getUrbanRuralComparison(periodId: number): Promise<UrbanRuralT> {
    const { data } = await apiClient.get<ResponseApi<UrbanRuralT>>(
      ANALYTICS_ENDPOINTS.DIRECTOR_URBAN_RURAL(periodId)
    );
    return data.data;
  }
}
```

### 3.4 Estructura del Dashboard con Tabs

```tsx
// DirectorDashboard.tsx (refactorizado)

export function DirectorDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  
  const tabs = [
    { id: "overview", label: "Resumen", icon: LayoutDashboard },
    { id: "geographic", label: "Geográfico", icon: MapPin },
    { id: "teachers", label: "Docentes", icon: Users },
    { id: "subjects", label: "Materias", icon: BookOpen },
    { id: "schedule", label: "Horario", icon: Clock },
    { id: "alerts", label: "Alertas", icon: Bell },
  ];

  return (
    <div>
      <PageHeader title="Dashboard" description="..." />
      
      {/* Selector de período */}
      <PeriodSelector />
      
      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 mb-6">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 -mb-px",
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-slate-500 hover:text-slate-700"
            )}
          >
            <tab.icon className="size-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contenido del tab activo */}
      {activeTab === "overview" && <DirectorOverviewTab />}
      {activeTab === "geographic" && <DirectorGeographicTab />}
      {activeTab === "teachers" && <DirectorTeacherTab />}
      {activeTab === "subjects" && <DirectorSubjectTab />}
      {activeTab === "schedule" && <DirectorScheduleTab />}
      {activeTab === "alerts" && <DirectorAlertsTab />}
    </div>
  );
}
```

### 3.5 Componente: Tab Geográfico

```tsx
// DirectorGeographicTab.tsx

export function DirectorGeographicTab() {
  const { effectivePeriodId } = useDashboardContext();
  const [riskByParish, setRiskByParish] = useState<RiskByParishT[]>([]);
  const [dropoutByParish, setDropoutByParish] = useState<DropoutByParishT[]>([]);
  const [urbanRural, setUrbanRural] = useState<UrbanRuralT>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!effectivePeriodId) return;
    setIsLoading(true);
    Promise.all([
      analyticsService.getRiskByParish(effectivePeriodId),
      analyticsService.getDropoutByParish(effectivePeriodId),
      analyticsService.getUrbanRuralComparison(effectivePeriodId),
    ]).then(([risk, dropout, ur]) => {
      setRiskByParish(risk);
      setDropoutByParish(dropout);
      setUrbanRural(ur);
      setIsLoading(false);
    });
  }, [effectivePeriodId]);

  return (
    <div className="space-y-6">
      {/* Comparativa Urbano vs Rural */}
      <SectionCard title="Comparativo Urbano vs Rural" icon={MapPin}>
        <div className="grid grid-cols-2 gap-4">
          <UrbanRuralCard type="URBANA" data={urbanRural.URBANA} />
          <UrbanRuralCard type="RURAL" data={urbanRural.RURAL} />
        </div>
      </SectionCard>

      {/* Riesgo por Parroquia */}
      <SectionCard title="Riesgo por Parroquia" icon={AlertTriangle}>
        <DataTable
          data={riskByParish}
          columns={[
            { key: "parish_name", label: "Parroquia" },
            { key: "parish_type", label: "Tipo", render: (v) => <Badge>{v}</Badge> },
            { key: "city_name", label: "Ciudad" },
            { key: "total_estudiantes", label: "Estudiantes" },
            { key: "tasa_riesgo_alto_pct", label: "% Riesgo Alto", render: (v) => <PctBar pct={v} /> },
            { key: "tasa_desercion_pct", label: "% Deserción", render: (v) => <PctBar pct={v} /> },
          ]}
          sortable
        />
      </SectionCard>

      {/* Deserción por Parroquia */}
      <SectionCard title="Deserción por Parroquia" icon={TrendingDown}>
        <DataTable
          data={dropoutByParish}
          columns={[
            { key: "parish_name", label: "Parroquia" },
            { key: "parish_type", label: "Tipo" },
            { key: "total_matriculas", label: "Matrículas" },
            { key: "retirados", label: "Retirados" },
            { key: "tasa_desercion_pct", label: "Tasa", render: (v) => <PctBar pct={v} /> },
          ]}
          sortable
        />
      </SectionCard>
    </div>
  );
}
```

### 3.6 Componente: Tab Docentes

```tsx
// DirectorTeacherTab.tsx

export function DirectorTeacherTab() {
  const { effectivePeriodId } = useDashboardContext();
  const [teachers, setTeachers] = useState<TeacherPerformanceT[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!effectivePeriodId) return;
    setIsLoading(true);
    analyticsService.getTeacherPerformance(effectivePeriodId)
      .then(setTeachers)
      .finally(() => setIsLoading(false));
  }, [effectivePeriodId]);

  return (
    <div className="space-y-6">
      {/* Ranking de Docentes */}
      <SectionCard title="Ranking de Docentes" icon={Users}>
        <DataTable
          data={teachers}
          columns={[
            { key: "ranking_periodo", label: "#", render: (v) => <Badge>{v}</Badge> },
            { key: "docente_nombre", label: "Docente" },
            { key: "total_estudiantes", label: "Estudiantes" },
            { key: "promedio_general", label: "Promedio", render: (v) => v.toFixed(1) },
            { key: "promedio_formativo", label: "Formativo", render: (v) => v.toFixed(1) },
            { key: "promedio_sumativo", label: "Sumativo", render: (v) => v.toFixed(1) },
            { key: "tasa_reprobacion_pct", label: "% Reprobación", render: (v) => <PctBar pct={v} /> },
          ]}
          sortable
        />
      </SectionCard>

      {/* Docentes con mayor tasa de reprobación */}
      <SectionCard title="Docentes con Mayor Tasa de Reprobación" icon={AlertTriangle} iconColor="text-red-600">
        <div className="space-y-3">
          {teachers
            .filter(t => t.total_estudiantes >= 20 && t.tasa_reprobacion_pct > 30)
            .sort((a, b) => b.tasa_reprobacion_pct - a.tasa_reprobacion_pct)
            .slice(0, 5)
            .map(t => (
              <div key={t.docente_id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="font-medium">{t.docente_nombre}</span>
                <span className="text-red-600 font-bold">{t.tasa_reprobacion_pct.toFixed(1)}%</span>
              </div>
            ))}
        </div>
      </SectionCard>
    </div>
  );
}
```

### 3.7 Componente: Tab Materias

```tsx
// DirectorSubjectTab.tsx

export function DirectorSubjectTab() {
  const { effectivePeriodId } = useDashboardContext();
  const [subjects, setSubjects] = useState<SubjectPerformanceT[]>([]);
  const [filterGrade, setFilterGrade] = useState<string>("");

  useEffect(() => {
    if (!effectivePeriodId) return;
    analyticsService.getSubjectPerformance(effectivePeriodId).then(setSubjects);
  }, [effectivePeriodId]);

  const filteredSubjects = filterGrade
    ? subjects.filter(s => s.grado_nombre === filterGrade)
    : subjects;

  const grades = [...new Set(subjects.map(s => s.grado_nombre))];

  return (
    <div className="space-y-6">
      {/* Filtro por grado */}
      <div className="flex gap-2">
        <button onClick={() => setFilterGrade("")} className={cn("px-3 py-1 rounded", !filterGrade && "bg-primary text-white")}>
          Todos
        </button>
        {grades.map(g => (
          <button key={g} onClick={() => setFilterGrade(g)} className={cn("px-3 py-1 rounded", filterGrade === g && "bg-primary text-white")}>
            {g}
          </button>
        ))}
      </div>

      {/* Materias más difíciles */}
      <SectionCard title="Materias con Mayor Tasa de Reprobación" icon={AlertCircle}>
        <DataTable
          data={filteredSubjects}
          columns={[
            { key: "ranking_dificultad", label: "#", render: (v) => <Badge>{v}</Badge> },
            { key: "asignatura_nombre", label: "Materia" },
            { key: "grado_nombre", label: "Grado" },
            { key: "total_estudiantes", label: "Estudiantes" },
            { key: "promedio_general", label: "Promedio", render: (v) => v.toFixed(1) },
            { key: "tasa_reprobacion_pct", label: "% Reprobación", render: (v) => <PctBar pct={v} /> },
            { key: "desviacion_estandar", label: "Desv. Est.", render: (v) => v.toFixed(2) },
          ]}
          sortable
        />
      </SectionCard>

      {/* Comparativa Formativo vs Sumativo */}
      <SectionCard title="Caída de Formativo a Sumativo" icon={TrendingDown}>
        <DataTable
          data={filteredSubjects
            .map(s => ({ ...s, diferencia: s.promedio_sumativo - s.promedio_formativo }))
            .sort((a, b) => a.diferencia - b.diferencia)
            .slice(0, 10)}
          columns={[
            { key: "asignatura_nombre", label: "Materia" },
            { key: "grado_nombre", label: "Grado" },
            { key: "promedio_formativo", label: "Formativo", render: (v) => v.toFixed(1) },
            { key: "promedio_sumativo", label: "Sumativo", render: (v) => v.toFixed(1) },
            { key: "diferencia", label: "Diferencia", render: (v) => (
              <span className={cn("font-bold", v < -1 ? "text-red-600" : v > 0 ? "text-green-600" : "")}>
                {v > 0 ? "+" : ""}{v.toFixed(1)}
              </span>
            )},
          ]}
        />
      </SectionCard>
    </div>
  );
}
```

### 3.8 Componente: Tab Horario

```tsx
// DirectorScheduleTab.tsx

export function DirectorScheduleTab() {
  const { effectivePeriodId } = useDashboardContext();
  const [byDay, setByDay] = useState<AttendanceByDayT[]>([]);
  const [bySchedule, setBySchedule] = useState<AttendanceByScheduleT[]>([]);

  useEffect(() => {
    if (!effectivePeriodId) return;
    Promise.all([
      analyticsService.getAttendanceByDay(effectivePeriodId),
      analyticsService.getAttendanceBySchedule(effectivePeriodId),
    ]).then(([day, schedule]) => {
      setByDay(day);
      setBySchedule(schedule);
    });
  }, [effectivePeriodId]);

  const worstDay = byDay.reduce((min, d) => d.asistencia_pct < min.asistencia_pct ? d : min, byDay[0]);
  const bestDay = byDay.reduce((max, d) => d.asistencia_pct > max.asistencia_pct ? d : max, byDay[0]);

  return (
    <div className="space-y-6">
      {/* Resumen rápido */}
      <div className="grid grid-cols-2 gap-4">
        <StatCard 
          label="Mejor día" 
          value={`${bestDay?.dia_nombre} (${bestDay?.asistencia_pct.toFixed(1)}%)`}
          icon={TrendingUp}
        />
        <StatCard 
          label="Peor día" 
          value={`${worstDay?.dia_nombre} (${worstDay?.asistencia_pct.toFixed(1)}%)`}
          icon={TrendingDown}
        />
      </div>

      {/* Asistencia por día */}
      <SectionCard title="Asistencia por Día de la Semana" icon={Calendar}>
        <div className="space-y-3">
          {byDay.map(d => (
            <div key={d.day_of_week}>
              <div className="flex justify-between text-sm mb-1">
                <span>{d.dia_nombre}</span>
                <span className="font-medium">{d.asistencia_pct.toFixed(1)}%</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className={cn("h-full rounded-full", 
                    d.asistencia_pct >= 90 ? "bg-green-500" : 
                    d.asistencia_pct >= 75 ? "bg-amber-400" : "bg-red-500"
                  )}
                  style={{ width: `${d.asistencia_pct}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>{d.tardanzas} tardanzas</span>
                <span>{d.ausencias} ausencias</span>
              </div>
            </div>
          ))}
        </div>
      </SectionCard>

      {/* Asistencia por franja horaria */}
      <SectionCard title="Asistencia por Franja Horaria" icon={Clock}>
        <div className="grid grid-cols-3 gap-4">
          {bySchedule.map(s => (
            <div key={s.franja_horaria} className="text-center p-4 rounded-lg bg-slate-50">
              <p className="text-2xl font-bold">{s.asistencia_pct.toFixed(1)}%</p>
              <p className="text-sm text-slate-600 capitalize">{s.franja_horaria}</p>
              <p className="text-xs text-slate-500 mt-2">{s.tardanzas} tardanzas</p>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
```

---

## 4. Plan de Implementación

### ✅ Fase 0: Correcciones críticas (COMPLETADO)

| Tarea | Estado | Archivos modificados |
|---|---|---|
| Corregir evolución de matrículas para mostrar comparativa entre años lectivos | ✅ | `repositories.py`, `services.py`, `views.py` |
| Agregar opción "Todos" para años lectivos | ✅ | `DirectorDashboard.tsx` |
| Agregar endpoint `enrollment_comparison` | ✅ | `views.py` |
| Agregar endpoint `enrollment_cumulative` | ✅ | `views.py` |
| Agregar tipos `SchoolYearEnrollmentT`, `CumulativeEnrollmentPointT` | ✅ | `analytics.types.ts` |
| Agregar métodos en service | ✅ | `analytics.service.ts` |
| Agregar endpoints en constants | ✅ | `analytics.constants.ts` |
| Crear componente `EnrollmentComparisonChart` | ✅ | `DirectorDashboard.tsx` |
| Crear componente `CumulativeEnrollmentChart` | ✅ | `DirectorDashboard.tsx` |

### Fase 1: Backend - Vistas materializadas (2-3 días)

| Día | Tarea | Entregable |
|---|---|---|
| **Día 1** | Crear migración con las 7 vistas materializadas | `0003_director_dashboard_views.py` |
| **Día 1** | Ejecutar migración y verificar datos | Vistas creadas y pobladas |
| **Día 2** | Agregar métodos en `DashboardRepository` | 7 nuevos métodos |
| **Día 2** | Agregar métodos en `DirectorDashboardService` | 7 nuevos métodos |
| **Día 2** | Crear vistas API para nuevos endpoints | 7 nuevas vistas |
| **Día 2** | Agregar URLs | 7 nuevas URLs |
| **Día 3** | Implementar task de refresh | `refresh_director_dashboard_views` |
| **Día 3** | Configurar Celery Beat | Refresh cada 2h |
| **Día 3** | Probar endpoints con Postman/curl | Todos funcionando |

### Fase 2: Frontend (2-3 días)

| Día | Tarea | Entregable |
|---|---|---|
| **Día 4** | Agregar tipos TypeScript | Nuevos tipos en `analytics.types.ts` |
| **Día 4** | Agregar métodos en service | 7 nuevos métodos en `analytics.service.ts` |
| **Día 4** | Agregar endpoints en constants | Nuevas URLs en `analytics.constants.ts` |
| **Día 5** | Crear componentes reutilizables | `StatCard`, `PctBar`, `DataTable`, `SectionCard` |
| **Día 5** | Refactorizar `DirectorDashboard.tsx` con tabs | Estructura con 6 tabs |
| **Día 6** | Implementar `DirectorGeographicTab` | Análisis por parroquia |
| **Día 6** | Implementar `DirectorTeacherTab` | Ranking de docentes |
| **Día 7** | Implementar `DirectorSubjectTab` | Rendimiento por materia |
| **Día 7** | Implementar `DirectorScheduleTab` | Análisis horario |
| **Día 7** | Mover contenido existente a `DirectorOverviewTab` | Tab resumen |
| **Día 7** | Mover alertas a `DirectorAlertsTab` | Tab alertas |

### Fase 3: Pruebas y ajustes (1 día)

| Día | Tarea |
|---|---|
| **Día 8** | Pruebas end-to-end |
| **Día 8** | Ajustes de UI/UX |
| **Día 8** | Optimización de queries |
| **Día 8** | Documentación |

---

## 5. Métricas de éxito

| Métrica | Antes | Después |
|---|---|---|
| Tiempo de carga del dashboard | ~500ms-2s | <100ms |
| KPIs mostrados | 12 | 25+ |
| Análisis geográfico | Solo ciudad | Ciudad + Parroquia + Urbano/Rural |
| Análisis docente | No existe | Ranking + Comparativa |
| Análisis por materia | Top 5 | Ranking completo + Estadísticas |
| Análisis horario | No existe | Por día + Por franja |
| Evolución de matrículas | 1-2 puntos por año | Comparativa entre años + Evolución acumulada |
| Opción "Todos" para años lectivos | No existe | Selector con opción "Todos los años" |
| Componentes reutilizables | 0 | 7+ (StatCard, PctBar, DataTable, SectionCard, EnrollmentComparisonChart, CumulativeEnrollmentChart) |
| Líneas en DirectorDashboard.tsx | 521 | ~100 (container) |

---

## 6. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Vistas materializadas desactualizadas | Media | Medio | Refresh cada 2h + botón "recargar" |
| Queries lentas en vistas | Baja | Medio | Índices en columnas de join |
| Frontend muy grande | Media | Bajo | Dividir en tabs con lazy loading |
| Breaking changes en API | Baja | Alto | Mantener endpoints existentes, agregar nuevos |

---

**Documento creado:** 2026-03-07  
**Última actualización:** 2026-03-07  
**Versión:** 1.1 — Correcciones de evolución de matrículas aplicadas
