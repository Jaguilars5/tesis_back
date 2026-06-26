"""
Servicios de dominio para dashboard y reportes analíticos.

Agrupa métricas y datos para visualizaciones.
"""

import csv
import io
from typing import List, Optional, Dict, Any

from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth

from apps.students.repositories.enrollment_repo import EnrollmentRepository
from apps.analytics.student_risk.infrastructure.repositories import (
    StudentRiskScoreRepository,
    StudentFeatureSnapshotRepository,
)
from apps.analytics.student_risk.infrastructure.models import (
    StudentRiskScore,
    StudentFeatureSnapshot,
)
from apps.analytics.early_alert.infrastructure.repositories import (
    EarlyAlertRepository,
)
from apps.analytics.early_alert.infrastructure.models import EarlyAlert


class DashboardService:
    """
    Servicio para métricas y KPIs del dashboard analítico.

    Proporciona agregaciones sobre datos de riesgo, asistencia y conducta.
    """

    @classmethod
    def get_overview(cls, academic_period_id: int) -> Dict[str, Any]:
        """KPIs globales para un período académico."""
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
                snapshots.aggregate(Avg("attendance_rate"))["attendance_rate__avg"]
                or 0
            ),
            "formative_avg": (
                snapshots.aggregate(Avg("formative_avg_normalized"))[
                    "formative_avg_normalized__avg"
                ]
                or 0
            ),
            "summative_avg": (
                snapshots.aggregate(Avg("summative_avg_normalized"))[
                    "summative_avg_normalized__avg"
                ]
                or 0
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
                snapshots.aggregate(Avg("severe_incidents_count"))[
                    "severe_incidents_count__avg"
                ]
                or 0
            ),
        }

    @classmethod
    def get_risk_distribution_by_grade(cls, academic_period_id: int) -> Dict[str, Dict]:
        """Distribución de riesgo por grado académico."""
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__section__academic_grade")

        distribution = {}
        for score in scores:
            grade = score.enrollment.section.academic_grade.name
            if grade not in distribution:
                distribution[grade] = {
                    "rojo": 0,
                    "amarillo": 0,
                    "verde": 0,
                    "total": 0,
                }
            distribution[grade][score.risk_label] += 1
            distribution[grade]["total"] += 1

        return distribution

    @classmethod
    def _risk_distribution_by_dimension(
        cls, scores, key_fn
    ) -> Dict[str, Dict[str, int]]:
        """Helper para distribución por dimensión arbitraria."""
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
    def get_risk_distribution_by_city(cls, academic_period_id: int) -> Dict[str, Dict]:
        """Distribución de riesgo por ciudad de origen (Fase 4)."""
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__user__person__city")

        def city_name(score):
            person = getattr(score.enrollment.student.user, "person", None)
            city = getattr(person, "city", None) if person else None
            return city.name if city else None

        return cls._risk_distribution_by_dimension(scores, city_name)

    @classmethod
    def get_risk_distribution_by_special_needs_type(
        cls, academic_period_id: int
    ) -> Dict[str, Dict]:
        """Distribución de riesgo por tipo de NEE (Fase 4)."""
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__special_needs_type")

        def needs_type(score):
            snt = score.enrollment.student.special_needs_type
            return snt.name if snt else "Sin NEE"

        return cls._risk_distribution_by_dimension(scores, needs_type)

    @classmethod
    def get_dropout_by_city(
        cls, school_year_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Índice de deserción por ciudad.

        Retorna lista de dicts con ciudad, total, retirados y tasa.
        """
        from apps.students.models import Enrollment

        qs = Enrollment.objects.select_related("student__user__person__city")
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
                "dropout_rate": (
                    round(data["withdrawn"] / data["total"], 4) if data["total"] else 0.0
                ),
            }
            for name, data in sorted(
                rows.items(), key=lambda kv: kv[1]["withdrawn"], reverse=True
            )
        ]

    @classmethod
    def get_withdrawal_reasons(
        cls, school_year_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Conteo de motivos de retiro."""
        from apps.students.models import Enrollment

        qs = Enrollment.objects.filter(enrollment_status="RET").select_related(
            "withdrawal_reason"
        )
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
    def get_students_at_risk(
        cls, academic_period_id: int, risk_label: str = "rojo"
    ) -> List[Dict[str, Any]]:
        """Lista de estudiantes con nivel de riesgo específico."""
        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id, risk_label=risk_label
        ).select_related("enrollment__student__user__person")

        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "risk_score": float(s.risk_score),
                "risk_label": s.risk_label,
            }
            for s in scores
        ]

    @classmethod
    def get_section_summary(cls, section_id: int) -> Dict[str, Any]:
        """Resumen de métricas para una sección específica."""
        snapshots = StudentFeatureSnapshot.objects.filter(
            enrollment__section_id=section_id
        )
        scores = StudentRiskScore.objects.filter(enrollment__section_id=section_id)

        return {
            "section_id": section_id,
            "total_students": snapshots.count(),
            "attendance_rate_avg": (
                snapshots.aggregate(Avg("attendance_rate"))["attendance_rate__avg"]
                or 0
            ),
            "formative_avg": (
                snapshots.aggregate(Avg("formative_avg_normalized"))[
                    "formative_avg_normalized__avg"
                ]
                or 0
            ),
            "risk_distribution": {
                "rojo": scores.filter(risk_label="rojo").count(),
                "amarillo": scores.filter(risk_label="amarillo").count(),
                "verde": scores.filter(risk_label="verde").count(),
            },
        }

    @classmethod
    def get_enrollment_trend(
        cls, school_year_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Tendencia de matrículas por mes."""
        from apps.students.models import Enrollment

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


class CSVExportService:
    """
    Servicio para exportación de datos a CSV.
    """

    EXPORT_TYPES = {
        "risk": {
            "model_path": "apps.analytics.student_risk.infrastructure.models.StudentRiskScore",
            "fields": [
                "enrollment__student__student_code",
                "risk_score",
                "risk_label",
            ],
            "headers": ["Código Estudiante", "Score Riesgo", "Nivel"],
        },
        "attendance": {
            "model_path": "apps.analytics.student_risk.infrastructure.models.StudentFeatureSnapshot",
            "fields": [
                "enrollment__student__student_code",
                "attendance_rate",
                "tardiness_count",
            ],
            "headers": ["Código Estudiante", "% Asistencia", "Tardanzas"],
        },
    }

    @classmethod
    def generate_csv(cls, export_type: str, academic_period_id: int) -> str:
        """
        Genera CSV para el tipo de exportación especificado.

        Args:
            export_type: "risk" o "attendance"
            academic_period_id: ID del período académico

        Returns:
            String con contenido CSV
        """
        config = cls.EXPORT_TYPES.get(export_type)
        if not config:
            raise ValueError(f"Tipo de exportación no válido: {export_type}")

        # Import dinámico del modelo
        module_path, model_name = config["model_path"].rsplit(".", 1)
        module = __import__(module_path, fromlist=[model_name])
        Model = getattr(module, model_name)

        queryset = Model.objects.filter(
            academic_period_id=academic_period_id
        ).values_list(*config["fields"])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(config["headers"])

        for row in queryset:
            writer.writerow(row)

        return output.getvalue()


class RecalculationService:
    """
    Servicio para recalcular riesgo de estudiantes.
    """

    @classmethod
    def get_student_ids_for_period(cls, academic_period_id: int) -> List[int]:
        """Obtiene IDs de estudiantes activos para un período."""
        from apps.students.models import Enrollment

        return list(
            Enrollment.objects.filter(
                enrollment_status="ACT",
                section__school_year__academic_periods__id=academic_period_id,
            ).values_list("student_id", flat=True)
        )

    @classmethod
    def recalculate_period(cls, academic_period_id: int, user_id: Optional[int] = None):
        """
        Inicia recálculo de riesgo para todos los estudiantes de un período.

        Retorna el task de Celery iniciado.
        """
        from apps.analytics.student_risk.domain.services import (
            StudentRiskCalculationService,
        )

        student_ids = cls.get_student_ids_for_period(academic_period_id)

        if not student_ids:
            return None

        return StudentRiskCalculationService.batch_calculate(
            academic_period_id, student_ids, user_id=user_id
        )
