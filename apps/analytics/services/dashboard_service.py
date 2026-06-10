from django.db.models import Avg, Count, Q
from ..models import StudentFeatureSnapshot, StudentRiskScore, EarlyAlert


class DashboardService:

    @classmethod
    def get_overview(cls, academic_period_id):
        snapshots = StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        )
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        )

        return {
            "period_id": academic_period_id,
            "total_students": snapshots.count(),
            "attendance_rate_avg": (
                snapshots.aggregate(Avg("attendance_rate"))["attendance_rate__avg"] or 0
            ),
            "formative_avg": (
                snapshots.aggregate(Avg("formative_avg_normalized"))["formative_avg_normalized__avg"] or 0
            ),
            "summative_avg": (
                snapshots.aggregate(Avg("summative_avg_normalized"))["summative_avg_normalized__avg"] or 0
            ),
            "failing_count": snapshots.filter(failing_subjects_count__gte=1).count(),
            "risk_distribution": {
                "rojo": scores.filter(risk_label="rojo").count(),
                "amarillo": scores.filter(risk_label="amarillo").count(),
                "verde": scores.filter(risk_label="verde").count(),
            },
            "active_alerts": EarlyAlert.objects.filter(
                academic_period_id=academic_period_id, attended=False
            ).count(),
            "avg_severe_incidents": (
                snapshots.aggregate(Avg("severe_incidents_count"))["severe_incidents_count__avg"] or 0
            ),
        }

    @classmethod
    def get_risk_distribution_by_grade(cls, academic_period_id):
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__section__academic_grade")

        distribution = {}
        for score in scores:
            grade = score.enrollment.section.academic_grade.name
            if grade not in distribution:
                distribution[grade] = {"rojo": 0, "amarillo": 0, "verde": 0, "total": 0}
            distribution[grade][score.risk_label] += 1
            distribution[grade]["total"] += 1

        return distribution

    @classmethod
    def get_students_at_risk(cls, academic_period_id, risk_label="rojo"):
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id,
            risk_label=risk_label,
        ).select_related("enrollment__student__person")

        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.person),
                "risk_score": s.risk_score,
                "risk_label": s.risk_label,
            }
            for s in scores
        ]
