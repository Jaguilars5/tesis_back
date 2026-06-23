"""
Analytics repositories - Acceso a datos de riesgo y métricas.
"""

from apps.core.repositories.base import BaseRepository
from ..models import StudentRiskScore, StudentFeatureSnapshot


class StudentRiskScoreRepository(BaseRepository):
    model = StudentRiskScore

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_latest_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(enrollment_id=enrollment_id).first()

    @classmethod
    def get_latest_by_student(cls, student_id):
        """Obtiene el puntaje de riesgo más reciente de un estudiante."""
        return cls.model.objects.filter(enrollment__student_id=student_id).first()

    @classmethod
    def list_high_risk(cls, academic_period_id, threshold=70):
        """Lista estudiantes con riesgo alto según un umbral."""
        return cls.model.objects.filter(
            academic_period_id=academic_period_id, risk_score__gte=threshold
        ).select_related("enrollment")

    @classmethod
    def create_score(
        cls,
        student_id=None,
        enrollment_id=None,
        academic_period_id=None,
        risk_score=None,
        risk_label=None,
        model_version=None,
    ):
        if not enrollment_id and student_id:
            from apps.students.models import Enrollment
            from apps.academic.models import AcademicPeriod
            period = AcademicPeriod.objects.get(pk=academic_period_id)
            enrollment = Enrollment.objects.filter(
                student_id=student_id,
                section__school_year=period.school_year
            ).first()
            if enrollment:
                enrollment_id = enrollment.id

        obj, _ = cls.model.objects.update_or_create(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            model_version=model_version,
            defaults={
                "risk_score": risk_score,
                "risk_label": risk_label,
            },
        )
        return obj


class StudentFeatureSnapshotRepository(BaseRepository):
    model = StudentFeatureSnapshot

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_enrollment_period(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id, academic_period_id=academic_period_id
        ).first()

    @classmethod
    def get_by_student_period(cls, student_id, academic_period_id):
        """Obtiene la foto de métricas para un estudiante y periodo."""
        return cls.model.objects.filter(
            enrollment__student_id=student_id, academic_period_id=academic_period_id
        ).first()

    @classmethod
    def create_snapshot(cls, student_id=None, enrollment_id=None, academic_period_id=None, metrics=None):
        """Persiste una instantanea de features calculadas."""
        if not enrollment_id and student_id:
            from apps.students.models import Enrollment
            from apps.academic.models import AcademicPeriod
            period = AcademicPeriod.objects.get(pk=academic_period_id)
            enrollment = Enrollment.objects.filter(
                student_id=student_id,
                section__school_year=period.school_year
            ).first()
            if enrollment:
                enrollment_id = enrollment.id

        mapped_metrics = {}
        if metrics:
            mapped_metrics = metrics.copy()
            if "avg_grade_normalized" in mapped_metrics:
                val = mapped_metrics.pop("avg_grade_normalized")
                mapped_metrics["formative_avg_normalized"] = val
                mapped_metrics["summative_avg_normalized"] = val

        # Asegurar valores por defecto para nuevos campos no nulos del modelo
        mapped_metrics.setdefault("justified_absences", 0)
        mapped_metrics.setdefault("unjustified_absences", 0)
        mapped_metrics.setdefault("severe_incidents_count", 0)
        mapped_metrics.setdefault("is_repeat", False)
        mapped_metrics.setdefault("has_special_needs", False)

        obj, _ = cls.model.objects.update_or_create(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            defaults=mapped_metrics,
        )
        return obj
