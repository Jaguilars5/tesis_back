"""
Mappers para convertir entre modelos Django y entities de dominio.

Placeholder para futura implementación de entities inmutables.
"""

from apps.analytics.student_risk.domain.risk_engine import score_to_risk_label
from .models import RiskFactor, StudentRiskScore, StudentFeatureSnapshot


def risk_factor_to_dict(factor: RiskFactor) -> dict:
    """Convierte RiskFactor a dict serializable."""
    return {
        "id": factor.id,
        "code": factor.code,
        "name": factor.name,
        "description": factor.description,
    }


def student_risk_score_to_dict(score: StudentRiskScore) -> dict:
    """Convierte StudentRiskScore a dict con sus factores."""
    return {
        "id": score.id,
        "enrollment_id": score.enrollment_id,
        "academic_period_id": score.academic_period_id,
        "risk_score": float(score.risk_score),
        "risk_label": score_to_risk_label(float(score.risk_score)),
        "model_version": score.model_version,
        "calculated_at": score.calculated_at,
        "risk_factors": [
            {
                "factor_id": rf.risk_factor_id,
                "factor_name": rf.risk_factor.name,
                "contribution_weight": float(rf.contribution_weight),
            }
            for rf in score.risk_factors.all()
        ],
    }


def student_feature_snapshot_to_dict(snapshot: StudentFeatureSnapshot) -> dict:
    """Convierte StudentFeatureSnapshot a dict."""
    return {
        "id": snapshot.id,
        "enrollment_id": snapshot.enrollment_id,
        "academic_period_id": snapshot.academic_period_id,
        "attendance_rate": float(snapshot.attendance_rate),
        "consecutive_absences_max": snapshot.consecutive_absences_max,
        "tardiness_count": snapshot.tardiness_count,
        "justified_absences": snapshot.justified_absences,
        "unjustified_absences": snapshot.unjustified_absences,
        "formative_avg_normalized": float(snapshot.formative_avg_normalized),
        "summative_avg_normalized": float(snapshot.summative_avg_normalized),
        "grade_trend_slope": float(snapshot.grade_trend_slope),
        "failing_subjects_count": snapshot.failing_subjects_count,
        "conduct_score": float(snapshot.conduct_score),
        "severe_incidents_count": snapshot.severe_incidents_count,
        "family_notified_ratio": float(snapshot.family_notified_ratio),
        "prev_period_avg_grade": float(snapshot.prev_period_avg_grade)
        if snapshot.prev_period_avg_grade
        else None,
        "age_grade_gap": snapshot.age_grade_gap,
        "is_repeat": snapshot.is_repeat,
        "has_special_needs": snapshot.has_special_needs,
        "is_current": snapshot.is_current,
        "snapshot_trigger": snapshot.snapshot_trigger,
        "calculated_at": snapshot.calculated_at,
    }
