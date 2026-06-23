from apps.core.repositories.base import BaseRepository
from apps.grading.models import PeriodGradeSummary


class PeriodGradeSummaryRepository(BaseRepository):
    model = PeriodGradeSummary

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
        ).select_related("subject_offering", "academic_period", "qualitative_scale")

    @classmethod
    def get_by_enrollment_offering_period(cls, enrollment, subject_offering, academic_period):
        return cls.model.objects.filter(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        ).first()

    @classmethod
    def get_failing(cls, academic_period_id):
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            is_failing=True,
        ).select_related("enrollment__student", "subject_offering")

    @classmethod
    def count_failing(cls, enrollment_id, academic_period_id):
        """
        Fuente ÚNICA del número de materias reprobadas para un (matrícula, periodo).
        Consumida tanto por `feature_builder` (riesgo) como por `early_alert_service`
        (alertas) para garantizar el mismo conteo (Fase 2, §6.4).
        """
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            is_failing=True,
        ).count()
