from typing import List, Optional

from django.db import transaction
from django.utils import timezone

from ..application import validators
from ..infrastructure.repositories import EarlyAlertRepository
from ..infrastructure.models import AlertTypeChoices, UrgencyLevelChoices


class EarlyAlertService:
    repository = EarlyAlertRepository

    @classmethod
    def get_alert(cls, alert_id):
        obj = cls.repository.get_by_id(alert_id)
        if not obj:
            raise ValueError({"id": f"Alerta {alert_id} no encontrada"})
        return obj

    @classmethod
    @transaction.atomic
    def create_alert(cls, enrollment, academic_period, alert_type=None, description="", urgency_level=None):
        cls._validate_or_raise(
            enrollment_id=enrollment.id if hasattr(enrollment, "id") else enrollment,
            academic_period_id=academic_period.id if hasattr(academic_period, "id") else academic_period,
            alert_type=alert_type,
            urgency_level=urgency_level,
        )
        return cls.repository.create(
            enrollment=enrollment,
            academic_period=academic_period,
            alert_type=alert_type,
            description=description,
            urgency_level=urgency_level,
        )

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def evaluate_student(cls, enrollment, academic_period) -> List:
        alerts = []

        from apps.attendance.attendance_core import AttendanceRepository

        attendance_summary = AttendanceRepository.get_absences_summary(
            enrollment.id, academic_period.id
        )
        if attendance_summary and attendance_summary.get("total", 0) > 0:
            attendance_rate = 1 - (
                (attendance_summary["unjustified"] + attendance_summary["late"])
                / attendance_summary["total"]
            )
            if attendance_rate < 0.7:
                alert_type = AlertTypeChoices.LOW_ATTENDANCE
                urgency_level = (
                    UrgencyLevelChoices.HIGH
                    if attendance_rate < 0.5
                    else UrgencyLevelChoices.MEDIUM
                )
                alert = cls.repository.create(
                    enrollment=enrollment,
                    academic_period=academic_period,
                    alert_type=alert_type,
                    description="Tasa de asistencia por debajo del 70%",
                    urgency_level=urgency_level,
                )
                alerts.append(alert)

        from apps.grading.student_note import PeriodGradeSummaryRepository

        failing_count = PeriodGradeSummaryRepository.count_failing(
            enrollment.id, academic_period.id
        )
        if failing_count >= 2:
            alert_type = AlertTypeChoices.FAILING_GRADES
            urgency_level = (
                UrgencyLevelChoices.HIGH
                if failing_count >= 4
                else UrgencyLevelChoices.MEDIUM
            )
            alert = cls.repository.create(
                enrollment=enrollment,
                academic_period=academic_period,
                alert_type=alert_type,
                description=f"{failing_count} materias reprobadas",
                urgency_level=urgency_level,
            )
            alerts.append(alert)

        from apps.behavior.conduct_incident import ConductIncidentRepository

        severe = ConductIncidentRepository.get_severe_by_enrollment(enrollment.id)
        if severe.count() >= 2:
            alert_type = AlertTypeChoices.BEHAVIORAL
            urgency_level = UrgencyLevelChoices.CRITICAL
            alert = cls.repository.create(
                enrollment=enrollment,
                academic_period=academic_period,
                alert_type=alert_type,
                description=f"{severe.count()} incidentes graves reportados",
                urgency_level=urgency_level,
            )
            alerts.append(alert)

        return alerts

    @classmethod
    @transaction.atomic
    def mark_as_attended(
        cls, alert_id: int, user_id: int, response_actions: Optional[str] = None
    ):
        alert = cls.get_alert(alert_id)
        if not alert.attended:
            alert = cls.repository.update(
                alert.id,
                attended=True,
                attended_by_user_id=user_id,
                attended_at=timezone.now(),
                response_actions=response_actions or "",
            )
        return alert
