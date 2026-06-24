"""
Servicios de dominio para alertas tempranas.

Lógica de negocio pura que orquesta validaciones y persistencia.
"""

from django.db import transaction
from django.utils import timezone
from typing import List, Optional

from ..infrastructure.repositories import EarlyAlertRepository
from ..infrastructure.models import AlertTypeChoices, UrgencyLevelChoices


class EarlyAlertService:
    """
    Servicio para generación y gestión de alertas tempranas.

    Evalúa reglas de negocio y crea alertas cuando se cumplen condiciones.
    """

    @staticmethod
    @transaction.atomic
    def evaluate_student(enrollment, academic_period) -> List:
        """
        Evalúa todas las reglas de alerta para un estudiante en un período.

        Retorna lista de alertas generadas.
        """
        alerts = []

        # Regla 1: Baja asistencia
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
                alert = EarlyAlertRepository.create(
                    enrollment=enrollment,
                    academic_period=academic_period,
                    alert_type=alert_type,
                    description="Tasa de asistencia por debajo del 70%",
                    urgency_level=urgency_level,
                )
                alerts.append(alert)

        # Regla 2: Calificaciones bajas
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
            alert = EarlyAlertRepository.create(
                enrollment=enrollment,
                academic_period=academic_period,
                alert_type=alert_type,
                description=f"{failing_count} materias reprobadas",
                urgency_level=urgency_level,
            )
            alerts.append(alert)

        # Regla 3: Incidentes de conducta graves
        from apps.behavior.conduct_incident import ConductIncidentRepository

        severe = ConductIncidentRepository.get_severe_by_enrollment(enrollment.id)
        if severe.count() >= 2:
            alert_type = AlertTypeChoices.BEHAVIORAL
            urgency_level = UrgencyLevelChoices.CRITICAL
            alert = EarlyAlertRepository.create(
                enrollment=enrollment,
                academic_period=academic_period,
                alert_type=alert_type,
                description=f"{severe.count()} incidentes graves reportados",
                urgency_level=urgency_level,
            )
            alerts.append(alert)

        return alerts

    @staticmethod
    @transaction.atomic
    def mark_as_attended(
        alert_id: int, user_id: int, response_actions: Optional[str] = None
    ) -> Optional:
        """Marca una alerta como atendida."""
        alert = EarlyAlertRepository.get_by_id(alert_id)
        if alert and not alert.attended:
            alert = EarlyAlertRepository.update(
                alert.id,
                attended=True,
                attended_by_user_id=user_id,
                attended_at=timezone.now(),
                response_actions=response_actions or "",
            )
        return alert
