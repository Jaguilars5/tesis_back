from datetime import date

from django.db import transaction

from ..constants import MODERATE_CODES, SEVERE_CODES
from ..infrastructure.repositories import BehaviorEvaluationRepository
from ..application import validators


class BehaviorEvaluationService:
    """Lógica de negocio para evaluaciones de conducta."""

    repository = BehaviorEvaluationRepository

    @classmethod
    def get_behavior_evaluation(cls, pk):
        obj = cls.repository.get_by_id(pk)
        if not obj:
            raise ValueError(f"Evaluación de conducta {pk} no encontrada")
        return obj

    @classmethod
    @transaction.atomic
    def calculate_behavior_evaluation(cls, enrollment_id, academic_period_id):
        errors = validators.run_all_validators(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        )
        if errors:
            raise ValueError(errors)

        from apps.behavior.conduct_incident.infrastructure.repositories import (
            ConductIncidentRepository,
        )
        incidents = list(
            ConductIncidentRepository.get_by_enrollment_and_period(
                enrollment_id=enrollment_id,
                academic_period_id=academic_period_id,
            )
        )

        scale = cls._determine_scale(incidents)

        eval_obj, _ = cls.repository.get_or_create(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            defaults={"calculated_scale": scale, "evaluation_date": date.today()},
        )
        if incidents and not eval_obj.final_scale:
            cls.repository.update(eval_obj.id, calculated_scale=scale)
            eval_obj = cls.repository.get_by_id(eval_obj.id)
        return eval_obj

    @classmethod
    def _determine_scale(cls, incidents):
        if not incidents:
            return cls.repository.get_or_create_qualitative_scale(
                "SE", defaults={"description": "Sin incidentes", "numeric_equivalence": 10.0}
            )

        severe_count = sum(1 for i in incidents if i.severity.code in SEVERE_CODES)
        moderate_count = sum(1 for i in incidents if i.severity.code in MODERATE_CODES)
        total_incidents = len(incidents)

        if severe_count >= 3 or (severe_count >= 1 and total_incidents >= 2):
            scale_code = "NA"
        elif severe_count >= 1 or moderate_count >= 1 or total_incidents >= 3:
            scale_code = "AC"
        elif total_incidents >= 1:
            scale_code = "SA"
        else:
            scale_code = "SE"

        return cls.repository.get_or_create_qualitative_scale(
            scale_code,
            defaults={"description": "Escala automática", "numeric_equivalence": 5.0},
        )

    @classmethod
    @transaction.atomic
    def update_evaluation(cls, pk, **kwargs):
        cls.get_behavior_evaluation(pk)
        allowed = {
            "calculated_scale_id", "final_scale_id", "general_observation",
            "override_reason", "evaluation_date", "approval_date",
            "evaluated_by_id", "approved_by_id",
        }
        clean = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        return cls.repository.update(pk, **clean)
