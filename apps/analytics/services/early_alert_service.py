from django.db import transaction
from apps.analytics.repositories.early_alert_repository import EarlyAlertRepository
from apps.analytics.repositories.alert_type_repository import AlertTypeRepository
from apps.analytics.repositories.urgency_level_repository import UrgencyLevelRepository


class EarlyAlertService:
    """
    Servicio para generación y gestión de alertas tempranas.
    Evalúa reglas de negocio y crea alertas cuando se cumplen condiciones.
    """

    @staticmethod
    @transaction.atomic
    def evaluate_student(enrollment, academic_period):
        """
        Evalúa todas las reglas de alerta para un estudiante en un período.
        Retorna lista de alertas generadas.
        """
        alerts = []

        # Regla 1: Baja asistencia
        from apps.attendance.repositories.attendance_repository import (
            AttendanceRepository,
        )
        attendance_summary = AttendanceRepository.get_absences_summary(
            enrollment.id, academic_period.id
        )
        if attendance_summary and attendance_summary.get("total", 0) > 0:
            attendance_rate = 1 - (
                (attendance_summary["unjustified"] + attendance_summary["late"]) /
                attendance_summary["total"]
            )
            if attendance_rate < 0.7:
                alert_type = AlertTypeRepository.get_by_code("low_attendance")
                urgency_code = "high" if attendance_rate < 0.5 else "medium"
                urgency_level = UrgencyLevelRepository.get_by_code(urgency_code)
                alert = EarlyAlertRepository.create(
                    enrollment=enrollment,
                    academic_period=academic_period,
                    alert_type=alert_type,
                    description="Tasa de asistencia por debajo del 70%",
                    urgency_level=urgency_level,
                )
                alerts.append(alert)

        # Regla 2: Calificaciones bajas
        from apps.grading.repositories.period_grade_summary_repository import (
            PeriodGradeSummaryRepository,
        )
        summaries = PeriodGradeSummaryRepository.get_by_enrollment(enrollment.id)
        failing = [s for s in summaries if s.requires_recovery]
        if len(failing) >= 2:
            alert_type = AlertTypeRepository.get_by_code("failing_grades")
            urgency_code = "high" if len(failing) >= 4 else "medium"
            urgency_level = UrgencyLevelRepository.get_by_code(urgency_code)
            alert = EarlyAlertRepository.create(
                enrollment=enrollment,
                academic_period=academic_period,
                alert_type=alert_type,
                description=f"{len(failing)} materias requieren recuperación",
                urgency_level=urgency_level,
            )
            alerts.append(alert)

        # Regla 3: Incidentes de conducta graves
        from apps.behavior.repositories.conduct_incident_repository import (
            ConductIncidentRepository,
        )
        severe = ConductIncidentRepository.get_severe_by_enrollment(
            enrollment.id, severity_threshold=4
        )
        if severe.count() >= 2:
            alert_type = AlertTypeRepository.get_by_code("behavioral")
            urgency_level = UrgencyLevelRepository.get_by_code("critical")
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
    def mark_as_attended(alert_id, user_id, response_actions=None):
        """Marca una alerta como atendida."""
        from django.utils import timezone
        alert = EarlyAlertRepository.get_by_id(alert_id)
        if alert and not alert.attended:
            alert = EarlyAlertRepository.update(
                alert.id,
                attended=True,
                attended_by_user_id=user_id,
                attended_at=timezone.now(),
                response_actions=response_actions,
            )
        return alert
