# Módulo `analytics` — Análisis de Riesgo Académico y Alertas

> Procesamiento de datos académicos, de asistencia y conducta para generar snapshots de métricas, calcular perfiles de riesgo, alertas tempranas, dashboard institucional y clustering de estudiantes.

## Modelos (5)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `RiskFactor` | Catálogo de factores de riesgo | `code` (unique), `name`, `description`. Ordenado por `name` |
| `StudentFeatureSnapshot` | Instantánea de métricas por estudiante y período | `enrollment` (FK), `academic_period` (FK), `attendance_rate`, `consecutive_absences_max`, `tardiness_count`, `justified_absences`, `unjustified_absences`, `formative_avg_normalized`, `summative_avg_normalized`, `grade_trend_slope`, `failing_subjects_count`, `conduct_score`, `severe_incidents_count`, `family_notified_ratio`, `prev_period_avg_grade`, `age_grade_gap`, `is_repeat`, `has_special_needs`, `active_alerts`, `is_current`, `snapshot_trigger` (MANUAL/AUTO/BATCH), `calculated_at`. Unique: `(enrollment, academic_period)` |
| `StudentRiskScore` | Puntaje de riesgo calculado | `enrollment` (FK), `academic_period` (FK), `risk_score` (0-100), `risk_label`, `model_version`, `calculated_at`. Unique: `(enrollment, academic_period)` |
| `StudentRiskFactor` | Factor de riesgo vinculado a un score | `student_risk_score` (FK), `risk_factor` (FK), `contribution_weight`. Unique: `(student_risk_score, risk_factor)` |
| `EarlyAlert` | Alerta temprana | `enrollment` (FK), `academic_period` (FK), `alert_type` (CharField con TextChoices), `description`, `urgency_level` (CharField con TextChoices), `attended`, `attended_by_user` (FK), `detected_at`, `attended_at`, `response_actions`. Hereda `TimeStampedModel` + `SyncableModel` |

> **Nota:** `AlertType` y `UrgencyLevel` **no existen** como modelos. Son `TextChoices` dentro de `EarlyAlert` (`AlertTypeChoices`, `UrgencyLevelChoices`). Tampoco existe `DashboardMetric`. El clustering persiste sus resultados como respuesta JSON, no en base de datos.

## Repositorios (5)

| Repositorio | Métodos adicionales |
|-------------|---------------------|
| `StudentRiskScoreRepository` | `get_all()` ordenado por `-id`; `get_latest_by_enrollment()`, `get_latest_by_student()`, `list_high_risk()`, `create_score()` |
| `StudentFeatureSnapshotRepository` | `get_all()` ordenado por `-id`; `get_by_enrollment_period()`, `get_by_student_period()`, `create_snapshot()` |
| `EarlyAlertRepository` | `get_pending_alerts()` (filtrable por urgency_level), `get_by_enrollment()`, `count_active_by_enrollment()` |
| `RiskFactorRepository` | `get_all()` ordenado por `name`; `get_by_code()` |
| `StudentRiskFactorRepository` | `get_all()` con `select_related` |

## Servicios (6)

| Servicio | Métodos principales | Descripción |
|----------|-------------------|-------------|
| `AnalyticsService` | `get_student_risk_profile(student_id)`, `list_priority_students(academic_period_id)` | Perfil completo de riesgo + estudiantes prioritarios |
| `AcademicRiskFeatureBuilder` | `build()`, `build_persistence_metrics(snapshot)` | Construye snapshot (conducta, asistencia, calificaciones) y extrae métricas planas |
| `EarlyAlertService` | `evaluate_student(enrollment, academic_period)`, `mark_as_attended(alert_id, user_id, response_actions)` | Evalúa 3 reglas (asistencia <70%, ≥2 materias recuperación, ≥2 incidentes graves) |
| `DashboardService` | `get_overview(period_id)`, `get_risk_distribution_by_grade(period_id)`, `get_students_at_risk(period_id, risk_label)` | KPIs globales, distribución semáforo por grado, lista estudiantes en riesgo |
| `CSVExportService` | `generate_csv(export_type, period_id)` | Exporta risk o attendance a CSV |
| `StudentClusteringService` | `cluster_students(period_id, n_clusters=4)` | KMeans clustering sobre snapshots |

## API — Endpoints Registrados

| Método | Endpoint | ViewSet |
|--------|----------|---------|
| GET | `/api/analytics/student-risk-scores/` | StudentRiskScoreViewSet |
| GET | `/api/analytics/student-risk-scores/{id}/` | StudentRiskScoreViewSet |
| POST | `/api/analytics/student-risk-scores/calculate/` | StudentRiskScoreViewSet |
| POST | `/api/analytics/student-risk-scores/batch_calculate/` | StudentRiskScoreViewSet |
| GET | `/api/analytics/feature-snapshots/` | StudentFeatureSnapshotViewSet |
| GET | `/api/analytics/feature-snapshots/{id}/` | StudentFeatureSnapshotViewSet |
| GET | `/api/analytics/risk-factors/` | RiskFactorViewSet (read-only) |
| GET | `/api/analytics/risk-factors/{id}/` | RiskFactorViewSet (read-only) |
| GET | `/api/analytics/student-risk-factors/` | StudentRiskFactorViewSet (read-only) |
| GET | `/api/analytics/student-risk-factors/{id}/` | StudentRiskFactorViewSet (read-only) |
| GET/POST | `/api/analytics/early-alerts/` | EarlyAlertViewSet |
| GET/PUT/PATCH/DEL | `/api/analytics/early-alerts/{id}/` | EarlyAlertViewSet |
| POST | `/api/analytics/early-alerts/{id}/mark_attended/` | EarlyAlertViewSet |
| GET | `/api/analytics/dashboard/overview/?period_id=` | DashboardViewSet |
| GET | `/api/analytics/dashboard/risk-distribution/?period_id=` | DashboardViewSet |
| GET | `/api/analytics/dashboard/students-at-risk/?period_id=&risk_label=` | DashboardViewSet |
| GET | `/api/analytics/dashboard/export-csv/?type=&period_id=` | DashboardViewSet |
| GET | `/api/analytics/dashboard/section-summary/?section_id=` | DashboardViewSet |

## Pipeline de Riesgo: Reglas del Semáforo

| Nivel | Condiciones |
|-------|-------------|
| Rojo | Asistencia < 70% **o** promedio < 6.0 **o** > 3 incidentes graves |
| Amarillo | Asistencia 70-85% **o** promedio 6.0-7.0 **o** > 5 incidentes leves |
| Verde | Asistencia > 85% **y** promedio > 7.0 **y** sin graves |

**Ponderación fallback:** Conducta 30%, Asistencia 35%, Calificaciones 35%.

## ML y Clustering

| Componente | Descripción |
|------------|-------------|
| `ml/train_model.py` | `RiskModelTrainer` con GradientBoostingClassifier, 16 features |
| `management/commands/train_risk_model.py` | `python manage.py train_risk_model --period-id=X` |
| `services/clustering_service.py` | KMeans (4 clusters) sobre 6 variables de snapshot |

## Tareas Celery (5)

| Tarea | Descripción |
|-------|-------------|
| `calculate_student_academic_risk_task` | Calcula riesgo de un estudiante (snapshot + score + risk_factors) |
| `batch_calculate_academic_risk` | Batch para múltiples estudiantes |
| `auto_generate_early_alerts` | Evalúa todos los estudiantes activos y genera alertas |
| `run_student_clustering` | Ejecuta clustering periódico |
| `refresh_materialized_views` | Refresca vistas materializadas (PostgreSQL) |

## Tests

```bash
python manage.py test apps.analytics --settings=config.settings.test
```

## Dependencias

- `academic.AcademicPeriod`, `academic.PeriodType`
- `students.Enrollment`, `students.Student`
- `iam.User`
- `attendance` (AttendanceRepository)
- `grading` (StudentNoteRepository, PeriodGradeSummaryRepository)
- `behavior` (ConductIncidentRepository)
- `institutions` (SchoolYear, Section, AcademicGrade)
- `integration` (SyncableModel, BaseSyncHandler)
