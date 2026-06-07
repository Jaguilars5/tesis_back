from decimal import Decimal
from datetime import date
from django.db import transaction
from apps.grading.repositories.recovery_process_repository import (
    RecoveryProcessRepository,
)


class RecoveryProcessService:
    """
    Servicio para gestionar procesos de recuperación académica.
    """

    @staticmethod
    @transaction.atomic
    def start_recovery(period_grade_summary, managed_by_user, process_type="reinforcement"):
        """Inicia un proceso de recuperación para un resumen de calificaciones."""
        recovery = RecoveryProcessRepository.create(
            period_grade_summary=period_grade_summary,
            managed_by_user=managed_by_user,
            process_type=process_type,
            initial_grade=period_grade_summary.final_avg_truncated,
            start_date=date.today(),
        )
        period_grade_summary.requires_recovery = True
        period_grade_summary.promotion_status = "recovery"
        period_grade_summary.save()
        return recovery

    @staticmethod
    @transaction.atomic
    def complete_recovery(recovery_id, final_grade, observations=""):
        """Completa un proceso de recuperación con la nota final."""
        recovery = RecoveryProcessRepository.get_by_id(recovery_id)
        if not recovery:
            return None

        RecoveryProcessRepository.update(
            recovery.id,
            final_calculated_grade=final_grade,
            end_date=date.today(),
            observations=observations,
        )

        # Volver a cargar el registro actualizado
        recovery = RecoveryProcessRepository.get_by_id(recovery_id)

        if final_grade >= Decimal("7.00"):
            summary = recovery.period_grade_summary
            summary.promotion_status = "approved"
            summary.save()

        return recovery
