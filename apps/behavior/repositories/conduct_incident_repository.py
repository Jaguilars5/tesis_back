from apps.core.repositories.base import BaseRepository
from apps.behavior.models import ConductIncident


class ConductIncidentRepository(BaseRepository):
    model = ConductIncident

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).select_related("incident_type")

    @classmethod
    def get_severe_by_enrollment(cls, enrollment_id, severity_threshold=3):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            severity__numeric_level__gte=severity_threshold,
        ).order_by("-incident_date")

    @classmethod
    def list_by_filters(
        cls,
        student_id=None,
        academic_period_id=None,
        category=None,
        severity=None,
        family_notified=None,
    ):
        queryset = cls.model.objects.all()
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if category:
            queryset = queryset.filter(incident_type__code=category)
        if severity:
            severity_val = getattr(severity, 'numeric_level', severity)
            queryset = queryset.filter(severity__numeric_level=severity_val)
        if family_notified is not None:
            queryset = queryset.filter(family_notified=family_notified)
        return queryset.order_by(
            "-incident_date", "enrollment__student__last_names", "enrollment__student__names"
        )

    @classmethod
    def list_for_risk_snapshot(cls, student_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment__student_id=student_id,
            academic_period_id=academic_period_id,
        ).order_by("-incident_date", "-id")
