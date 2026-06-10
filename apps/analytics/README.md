# Módulo `analytics` — Análisis de Riesgo Académico y Alertas

> Procesamiento de datos académicos, de asistencia y conducta para generar snapshots de métricas, calcular perfiles de riesgo, alertas tempranas, dashboard institucional y clustering de estudiantes.

## Modelos (8)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `AlertType` | Catálogo de tipos de alerta | `code` (unique: low_attendance, failing_grades, behavioral, dropout_risk, socioemotional), `name`, `is_active` |
| `UrgencyLevel` | Catálogo de niveles de urgencia | `code` (unique: low, medium, high, critical), `name`, `is_active` |
| `RiskFactor` | Catálogo de factores de riesgo | `code` (unique: LOW_ATTENDANCE, FAILING_GRADES, BEHAVIOR_ISSUES, SOCIOEMOTIONAL), `name`, `description` |
| `StudentFeatureSnapshot` | Instantánea de métricas por estudiante y período | `enrollment` (FK), `academic_period` (FK), `attendance_rate`, `consecutive_absences_max`, `tardiness_count`, `justified_absences`, `unjustified_absences`, `formative_avg_normalized`, `summative_avg_normalized`, `grade_trend_slope`, `failing_subjects_count`, `conduct_score`, `severe_incidents_count`, `family_notified_ratio`, `prev_period_avg_grade`, `age_grade_gap`, `is_repeat`, `has_special_needs`, `active_alerts`, `calculated_at`. Unique: `(enrollment, academic_period)` |
| `StudentRiskScore` | Puntaje de riesgo calculado | `enrollment` (FK), `academic_period` (FK), `risk_score` (0-100), `risk_label` (rojo/amarillo/verde), `model_version`, `calculated_at`. Unique: `(enrollment, academic_period)` |
| `StudentRiskFactor` | Factor de riesgo vinculado a un score | `student_risk_score` (FK), `risk_factor` (FK), `contribution_weight`. Unique: `(student_risk_score, risk_factor)` |
| `EarlyAlert` | Alerta temprana generada automáticamente | `enrollment` (FK), `academic_period` (FK), `alert_type` (FK AlertType), `description`, `urgency_level` (FK UrgencyLevel), `attended`, `attended_by_user` (FK), `detected_at`, `attended_at`, `response_actions`. Hereda `SyncableModel`. |
| `DashboardMetric` | Métrica precalculada para dashboards | `academic_period` (FK), `section` (FK, nullable), `academic_grade` (FK, nullable), `metric_type`, `metric_value` (JSON), `calculated_at`. Unique: `(academic_period, section, metric_type)` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `AnalyticsService` | `get_student_risk_profile(student_id)` | Perfil completo de riesgo (score + snapshot) |
| `AnalyticsService` | `list_priority_students(academic_period_id)` | Estudiantes con mayor riesgo |
| `AcademicRiskFeatureBuilder` | `build()` | Construye snapshot JSON desde datos transaccionales |
| `AcademicRiskFeatureBuilder` | `build_persistence_metrics(snapshot)` | Extrae métricas planas para persistir |
| `EarlyAlertService` | `evaluate_student(enrollment, academic_period)` | Evalúa 3 reglas (asistencia <70%, ≥2 materias en recuperación, ≥2 incidentes graves) y genera alertas |
| `EarlyAlertService` | `mark_as_attended(alert_id, user_id, response_actions)` | Cierra alerta con acciones tomadas |
| `DashboardService` | `get_overview(period_id)` | KPIs globales del período |
| `DashboardService` | `get_risk_distribution_by_grade(period_id)` | Distribución semáforo por grado |
| `DashboardService` | `get_students_at_risk(period_id, risk_label)` | Lista estudiantes en nivel de riesgo |
| `CSVExportService` | `generate_csv(export_type, period_id)` | Exporta risk o attendance a CSV |
| `StudentClusteringService` | `cluster_students(period_id, n_clusters=4)` | KMeans clustering, persiste en DashboardMetric |

## API

| Método | Endpoint | ViewSet | Permiso requerido |
|--------|----------|---------|-------------------|
| GET | `/api/analytics/student-risk-scores/` | StudentRiskScoreViewSet | `analytics.view_risk_score` |
| GET | `/api/analytics/student-risk-scores/{id}/` | StudentRiskScoreViewSet | `analytics.view_risk_score` |
| POST | `/api/analytics/student-risk-scores/calculate/` | StudentRiskScoreViewSet | `analytics.create_student_risk_factor` |
| POST | `/api/analytics/student-risk-scores/batch_calculate/` | StudentRiskScoreViewSet | `analytics.create_student_risk_factor` |
| GET | `/api/analytics/feature-snapshots/` | StudentFeatureSnapshotViewSet | `analytics.view_feature_snapshot` |
| GET/POST | `/api/analytics/alert-types/` | AlertTypeViewSet | `analytics.view/create_alert_type` |
| GET/POST | `/api/analytics/urgency-levels/` | UrgencyLevelViewSet | `analytics.view/create_urgency_level` |
| GET | `/api/analytics/risk-factors/` | RiskFactorViewSet (read-only) | `analytics.view_risk_factor` |
| GET | `/api/analytics/student-risk-factors/` | StudentRiskFactorViewSet (read-only) | `analytics.view_student_risk_factor` |
| GET/POST/PATCH/DEL | `/api/analytics/early-alerts/` | EarlyAlertViewSet | `analytics.view/create/update/delete_early_alert` |
| POST | `/api/analytics/early-alerts/{id}/mark_attended/` | EarlyAlertViewSet | `analytics.update_early_alert` |
| GET | `/api/analytics/dashboard/overview/?period_id=` | DashboardViewSet | `analytics.view_risk_score` |
| GET | `/api/analytics/dashboard/risk-distribution/?period_id=` | DashboardViewSet | `analytics.view_risk_score` |
| GET | `/api/analytics/dashboard/students-at-risk/?period_id=&risk_label=` | DashboardViewSet | `analytics.view_risk_score` |
| GET | `/api/analytics/dashboard/export-csv/?type=&period_id=` | DashboardViewSet | `analytics.view_risk_score` |
| GET | `/api/analytics/dashboard/section-summary/?section_id=` | DashboardViewSet | `analytics.view_risk_score` |

## Pipeline de Riesgo: Reglas del Semáforo

| Nivel | Condiciones |
|-------|-------------|
| 🔴 Rojo | Asistencia < 70% **o** promedio < 6.0 **o** > 3 incidentes graves |
| 🟡 Amarillo | Asistencia 70-85% **o** promedio 6.0-7.0 **o** > 5 incidentes leves |
| 🟢 Verde | Asistencia > 85% **y** promedio > 7.0 **y** sin graves |

**Ponderación del puntaje fallback:** Conducta 30%, Asistencia 35%, Calificaciones 35%.

## ML y Clustering

| Componente | Descripción |
|------------|-------------|
| `ml/train_model.py` | `RiskModelTrainer` con GradientBoostingClassifier, 16 features |
| `management/commands/train_risk_model.py` | `python manage.py train_risk_model --period-id=X` |
| `services/clustering_service.py` | KMeans (4 clusters) sobre 6 variables, persiste en DashboardMetric |

## Tareas Celery

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
