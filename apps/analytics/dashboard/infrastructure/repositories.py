"""
Repositorio del dashboard analítico.

Centraliza TODA la consulta ORM de las métricas/reportes del dashboard
(checklist §4: "Toda consulta ORM debe vivir aquí"). Importa modelos de otras
apps únicamente en esta capa de infraestructura.
"""

from typing import Optional

from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth

from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from apps.analytics.student_risk.infrastructure.models import (
    StudentFeatureSnapshot,
    StudentRiskScore,
)
from apps.students.models import Enrollment


class DashboardRepository:
    """Acceso a datos para KPIs, distribuciones y reportes del dashboard."""

    # ── Helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _label_counts(scores_qs) -> dict:
        """Cuenta puntajes por etiqueta de riesgo (rojo/amarillo/verde)."""
        counts = {"rojo": 0, "amarillo": 0, "verde": 0}
        for row in scores_qs.values("risk_label").annotate(n=Count("id")):
            if row["risk_label"] in counts:
                counts[row["risk_label"]] = row["n"]
        return counts

    # ── Período: snapshots y scores ──────────────────────────────────────────
    @classmethod
    def get_snapshot_aggregates(cls, academic_period_id: int) -> dict:
        """Agregados de métricas (snapshots) para un período."""
        qs = StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        )
        agg = qs.aggregate(
            attendance_rate_avg=Avg("attendance_rate"),
            formative_avg=Avg("formative_avg_normalized"),
            summative_avg=Avg("summative_avg_normalized"),
            avg_severe_incidents=Avg("severe_incidents_count"),
        )
        return {
            "total_students": qs.count(),
            "failing_count": qs.filter(failing_subjects_count__gte=1).count(),
            "attendance_rate_avg": agg["attendance_rate_avg"] or 0,
            "formative_avg": agg["formative_avg"] or 0,
            "summative_avg": agg["summative_avg"] or 0,
            "avg_severe_incidents": agg["avg_severe_incidents"] or 0,
        }

    @classmethod
    def get_risk_label_counts(cls, academic_period_id: int) -> dict:
        """Distribución global de etiquetas de riesgo para un período."""
        return cls._label_counts(
            StudentRiskScore.objects.filter(academic_period_id=academic_period_id)
        )

    @classmethod
    def get_active_alerts_count(cls, academic_period_id: int) -> int:
        """Conteo de alertas tempranas no atendidas del período."""
        return EarlyAlert.objects.filter(
            academic_period_id=academic_period_id, attended=False
        ).count()

    @classmethod
    def scores_with_grade(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__section__academic_grade")

    @classmethod
    def scores_with_city(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__user__person__city")

    @classmethod
    def scores_with_special_needs(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__special_needs_type")

    @classmethod
    def scores_with_person_by_label(cls, academic_period_id: int, risk_label: str):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id, risk_label=risk_label
        ).select_related("enrollment__student__user__person")

    # ── Sección ──────────────────────────────────────────────────────────────
    @classmethod
    def get_section_snapshot_aggregates(cls, section_id: int) -> dict:
        qs = StudentFeatureSnapshot.objects.filter(enrollment__section_id=section_id)
        agg = qs.aggregate(
            attendance_rate_avg=Avg("attendance_rate"),
            formative_avg=Avg("formative_avg_normalized"),
        )
        return {
            "total_students": qs.count(),
            "attendance_rate_avg": agg["attendance_rate_avg"] or 0,
            "formative_avg": agg["formative_avg"] or 0,
        }

    @classmethod
    def get_section_risk_label_counts(cls, section_id: int) -> dict:
        return cls._label_counts(
            StudentRiskScore.objects.filter(enrollment__section_id=section_id)
        )

    # ── Matrículas: deserción / retiro / tendencia ───────────────────────────
    @classmethod
    def enrollments_with_city(cls, school_year_id: Optional[int] = None):
        qs = Enrollment.objects.select_related("student__user__person__city")
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return qs

    @classmethod
    def withdrawn_enrollments_with_reason(cls, school_year_id: Optional[int] = None):
        qs = Enrollment.objects.filter(enrollment_status="RET").select_related(
            "withdrawal_reason"
        )
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return qs

    @classmethod
    def get_enrollment_trend_rows(cls, school_year_id: Optional[int] = None):
        qs = Enrollment.objects.all()
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return (
            qs.annotate(month=TruncMonth("enrollment_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

    @classmethod
    def get_active_student_ids_for_period(cls, academic_period_id: int) -> list:
        return list(
            Enrollment.objects.filter(
                enrollment_status="ACT",
                section__school_year__academic_periods__id=academic_period_id,
            ).values_list("student_id", flat=True)
        )

    # ── Exportación CSV ──────────────────────────────────────────────────────
    @classmethod
    def get_risk_export_rows(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).values_list(
            "enrollment__student__student_code", "risk_score", "risk_label"
        )

    @classmethod
    def get_attendance_export_rows(cls, academic_period_id: int):
        return StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        ).values_list(
            "enrollment__student__student_code", "attendance_rate", "tardiness_count"
        )
