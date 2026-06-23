# Estandarización de Rutas — Mapeo Completo

## Cambios rompedores

### Eje A: Prefijos pluralizados

#### academic

| Vieja ruta | Nueva ruta |
|------------|------------|
| `/api/academic/subject/` | `/api/academic/subjects/` |
| `/api/academic/academic-period/` | `/api/academic/academic-periods/` |
| `/api/academic/teacher-subject-section/` | `/api/academic/teacher-subject-sections/` |
| `/api/academic/class-schedule/` | `/api/academic/class-schedules/` |

Sin cambio: `period-types`, `subject-academic-configs`, `subject-offerings`

#### institutions

| Vieja ruta | Nueva ruta |
|------------|------------|
| `/api/institutions/school-year/` | `/api/institutions/school-years/` |
| `/api/institutions/academic-sublevel/` | `/api/institutions/academic-sublevels/` |
| `/api/institutions/section/` | `/api/institutions/sections/` |

Sin cambio: `academic-levels`, `academic-grades`

#### students

| Vieja ruta | Nueva ruta |
|------------|------------|
| `/api/students/student/` | `/api/students/students/` |
| `/api/students/student-representative/` | `/api/students/student-representatives/` |
| `/api/students/kinship/` | `/api/students/kinships/` |

Sin cambio: `enrollments`, `special-needs-types`

### Eje B: Acciones a kebab-case

Todas las `@action` sin `url_path` explícito ahora tienen uno en kebab-case.

#### academic

| ViewSet | Acción | URL anterior (snake_case) | URL nueva (kebab-case) |
|---------|--------|---------------------------|------------------------|
| ClassScheduleViewSet | `by_section` | `/class-schedule/by_section/` | `/class-schedules/by-section/` |
| ClassScheduleViewSet | `my_schedule` | `/class-schedule/my_schedule/` | `/class-schedules/my-schedule/` |
| ClassScheduleViewSet | `my_today` | `/class-schedule/my_today/` | `/class-schedules/my-today/` |

#### students

| ViewSet | Acción | URL anterior (snake_case) | URL nueva (kebab-case) |
|---------|--------|---------------------------|------------------------|
| StudentViewSet | `by_section` | `/student/by_section/` | `/students/by-section/` |
| StudentRepresentativeViewSet | `set_primary` | `/student-representative/set_primary/` | `/student-representatives/set-primary/` |

#### behavior

| ViewSet | Acción | URL anterior (snake_case) | URL nueva (kebab-case) |
|---------|--------|---------------------------|------------------------|
| IncidentTypeViewSet | `soft_delete` | `/incident-types/soft_delete/` | `/incident-types/soft-delete/` |
| SeverityViewSet | `soft_delete` | `/severities/soft_delete/` | `/severities/soft-delete/` |
| BehaviorEvaluationViewSet | `related_incidents` | `/behavior-evaluations/{pk}/related_incidents/` | `/behavior-evaluations/{pk}/related-incidents/` |

#### attendance

| ViewSet | Acción | URL anterior (snake_case) | URL nueva (kebab-case) |
|---------|--------|---------------------------|------------------------|
| AttendanceViewSet | `take_by_schedule` | `/attendances/take_by_schedule/` | `/attendances/take-by-schedule/` |

#### iam

| ViewSet | Acción | URL anterior (snake_case) | URL nueva (kebab-case) |
|---------|--------|---------------------------|------------------------|
| PermissionViewSet | `by_module` | `/permissions/by_module/` | `/permissions/by-module/` |
| RoleViewSet | `assign_permissions` | `/roles/{pk}/assign_permissions/` | `/roles/{pk}/assign-permissions/` |

#### analytics

| ViewSet | Acción | URL anterior (snake_case) | URL nueva (kebab-case) |
|---------|--------|---------------------------|------------------------|
| StudentRiskScoreViewSet | `batch_calculate` | `/student-risk-factors/batch_calculate/` | `/student-risk-factors/batch-calculate/` |
| EarlyAlertViewSet | `mark_attended` | `/early-alerts/{pk}/mark_attended/` | `/early-alerts/{pk}/mark-attended/` |
| DashboardViewSet | `risk_distribution` | `/dashboard/risk_distribution/` | `/dashboard/risk-distribution/` |
| DashboardViewSet | `risk_by_city` | `/dashboard/risk_by_city/` | `/dashboard/risk-by-city/` |
| DashboardViewSet | `risk_by_special_needs` | `/dashboard/risk_by_special_needs/` | `/dashboard/risk-by-special-needs/` |
| DashboardViewSet | `dropout_by_city` | `/dashboard/dropout_by_city/` | `/dashboard/dropout-by-city/` |
| DashboardViewSet | `withdrawal_reasons` | `/dashboard/withdrawal_reasons/` | `/dashboard/withdrawal-reasons/` |
| DashboardViewSet | `students_at_risk` | `/dashboard/students_at_risk/` | `/dashboard/students-at-risk/` |
| DashboardViewSet | `export_csv` | `/dashboard/export_csv/` | `/dashboard/export-csv/` |
| DashboardViewSet | `section_summary` | `/dashboard/section_summary/` | `/dashboard/section-summary/` |
| DashboardViewSet | `enrollment_trend` | `/dashboard/enrollment_trend/` | `/dashboard/enrollment-trend/` |
| DashboardViewSet | `recalculate_period` | `/dashboard/recalculate_period/` | `/dashboard/recalculate-period/` |
| RiskScoringConfigViewSet | `update_config` | `/scoring-config/update_config/` | `/scoring-config/update-config/` |
| RiskScoringConfigViewSet | `apply_preset` | `/scoring-config/apply_preset/` | `/scoring-config/apply-preset/` |

### Rutas que NO cambiaron (singletons / mass nouns)

| Ruta | Razón |
|------|-------|
| `/api/analytics/dashboard/` | Singleton de diseño |
| `/api/analytics/scoring-config/` | Singleton de diseño |
| `/api/integration/sync-queue/` | Singleton de diseño |
| `/api/grading/grade-history/` | Sustantivo incontable |
| `/api/people/persons/` | Ya plural |
| `/api/attendance/attendances/` | Ya plural |
| `/api/attendance/attendance-statuses/` | Ya plural |
| `/api/attendance/absence-types/` | Ya plural |
| `/api/behavior/conduct-incidents/` | Ya plural |
| `/api/behavior/behavior-evaluations/` | Ya plural |
| `/api/behavior/incident-types/` | Ya plural |
| `/api/behavior/severities/` | Ya plural |
| `/api/iam/permissions/` | Ya plural |
| `/api/iam/roles/` | Ya plural |
| `/api/iam/users/` | Ya plural |
| `/api/people/cities/` | Ya plural |
| `/api/people/document-types/` | Ya plural |
| `/api/academic/period-types/` | Ya plural |
| `/api/academic/subject-academic-configs/` | Ya plural |
| `/api/academic/subject-offerings/` | Ya plural |
| `/api/institutions/academic-levels/` | Ya plural |
| `/api/institutions/academic-grades/` | Ya plural |
| `/api/students/enrollments/` | Ya plural |
| `/api/students/special-needs-types/` | Ya plural |
| `/api/grading/student-notes/` | Ya plural |
| `/api/grading/block-components/` | Ya plural |
| `/api/grading/evaluation-blocks/` | Ya plural |
| `/api/grading/evaluative-activities/` | Ya plural |
| `/api/grading/period-grade-summaries/` | Ya plural |
| `/api/grading/qualitative-scales/` | Ya plural |
| `/api/grading/activity-types/` | Ya plural |
| `/api/grading/qualitative-scale-sublevels/` | Ya plural |
| `/api/analytics/risk-factors/` | Ya plural |
| `/api/analytics/student-risk-factors/` | Ya plural |
| `/api/analytics/early-alerts/` | Ya plural |
| `/api/analytics/student-risk-scores/` | Ya plural |
| `/api/analytics/student-feature-snapshots/` | Ya plural |
