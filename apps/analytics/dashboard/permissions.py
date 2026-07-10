"""
Permisos para el módulo de dashboard.
"""

from apps.core.constants.permissions import analytics

DASHBOARD_ACTION_PERMISSIONS = {
    "overview": analytics.VIEW_RISK_SCORE,
    "risk_distribution": analytics.VIEW_RISK_SCORE,
    "risk_by_city": analytics.VIEW_RISK_SCORE,
    "risk_by_special_needs": analytics.VIEW_RISK_SCORE,
    "dropout_by_city": analytics.VIEW_RISK_SCORE,
    "withdrawal_reasons": analytics.VIEW_RISK_SCORE,
    "students_at_risk": analytics.VIEW_RISK_SCORE,
    "export_csv": analytics.VIEW_RISK_SCORE,
    "section_summary": analytics.VIEW_RISK_SCORE,
    "enrollment_trend": analytics.VIEW_RISK_SCORE,
    "enrollment_comparison": analytics.VIEW_RISK_SCORE,
    "enrollment_cumulative": analytics.VIEW_RISK_SCORE,
    "director_dashboard": analytics.VIEW_RISK_SCORE,
    "teacher_dashboard": analytics.VIEW_RISK_SCORE,
    "recalculate_period": analytics.CREATE_STUDENT_RISK_FACTOR,
}
