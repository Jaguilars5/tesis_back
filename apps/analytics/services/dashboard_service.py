from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from apps.students.models import Enrollment
from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from ..models import StudentFeatureSnapshot, StudentRiskScore


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
    def _risk_distribution_by_dimension(cls, scores, key_fn):
        distribution = {}
        for score in scores:
            key = key_fn(score) or "Sin asignar"
            bucket = distribution.setdefault(
                key, {"rojo": 0, "amarillo": 0, "verde": 0, "total": 0}
            )
            if score.risk_label in bucket:
                bucket[score.risk_label] += 1
            bucket["total"] += 1
        return distribution

    @classmethod
    def get_risk_distribution_by_city(cls, academic_period_id):
        """Distribución de riesgo por ciudad de origen (Fase 4 §5 F)."""
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__user__person__city")

        def city_name(score):
            person = getattr(score.enrollment.student.user, "person", None)
            city = getattr(person, "city", None) if person else None
            return city.name if city else None

        return cls._risk_distribution_by_dimension(scores, city_name)

    @classmethod
    def get_risk_distribution_by_special_needs_type(cls, academic_period_id):
        """Distribución de riesgo por tipo de NEE (Fase 4 §5 F)."""
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__special_needs_type")

        def needs_type(score):
            snt = score.enrollment.student.special_needs_type
            return snt.name if snt else "Sin NEE"

        return cls._risk_distribution_by_dimension(scores, needs_type)

    @classmethod
    def get_dropout_by_city(cls, school_year_id=None):
        """
        Índice de deserción por ciudad: total de matrículas vs. retiradas (estado
        RET) por ciudad de origen. Identifica ciudades con mayor deserción (§5 F).
        """
        qs = Enrollment.objects.select_related(
            "student__user__person__city"
        )
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)

        rows = {}
        for enrollment in qs:
            person = getattr(enrollment.student.user, "person", None)
            city = getattr(person, "city", None) if person else None
            name = city.name if city else "Sin asignar"
            bucket = rows.setdefault(name, {"total": 0, "withdrawn": 0})
            bucket["total"] += 1
            if enrollment.enrollment_status == "RET":
                bucket["withdrawn"] += 1

        return [
            {
                "city": name,
                "total": data["total"],
                "withdrawn": data["withdrawn"],
                "dropout_rate": round(data["withdrawn"] / data["total"], 4)
                if data["total"]
                else 0.0,
            }
            for name, data in sorted(
                rows.items(), key=lambda kv: kv[1]["withdrawn"], reverse=True
            )
        ]

    @classmethod
    def get_withdrawal_reasons(cls, school_year_id=None):
        """Conteo de motivos de retiro (reporte analítico, §5 F)."""
        qs = Enrollment.objects.filter(
            enrollment_status="RET"
        ).select_related("withdrawal_reason")
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)

        counts = {}
        for enrollment in qs:
            reason = enrollment.withdrawal_reason
            name = reason.name if reason else "Sin especificar"
            counts[name] = counts.get(name, 0) + 1

        return [
            {"reason": name, "count": count}
            for name, count in sorted(
                counts.items(), key=lambda kv: kv[1], reverse=True
            )
        ]

    @classmethod
    def get_students_at_risk(cls, academic_period_id, risk_label="rojo"):
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id,
            risk_label=risk_label,
        ).select_related("enrollment__student__user__person")

        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "risk_score": s.risk_score,
                "risk_label": s.risk_label,
            }
            for s in scores
        ]

    @classmethod
    def get_enrollment_trend(cls, school_year_id=None):
        qs = Enrollment.objects.all()
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)

        rows = (
            qs.annotate(month=TruncMonth("enrollment_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        return [
            {"month": r["month"].strftime("%Y-%m"), "count": r["count"]}
            for r in rows
            if r["month"] is not None
        ]
