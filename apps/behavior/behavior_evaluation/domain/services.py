from datetime import date

from django.db import transaction

from apps.grading.qualitative_scale import QualitativeScale
from apps.grading.qualitative_scale import QualitativeScaleRepository
from apps.behavior.conduct_incident.infrastructure.repositories import (
    ConductIncidentRepository,
)

from ..constants import MODERATE_CODES, SEVERE_CODES
from ..infrastructure.repositories import BehaviorEvaluationRepository


class BehaviorEvaluationService:
    """Lógica de negocio para evaluaciones de conducta."""

    repository = BehaviorEvaluationRepository

    @staticmethod
    @transaction.atomic
    def calculate_behavior_evaluation(enrollment, academic_period):
        incidents = list(
            ConductIncidentRepository.get_by_enrollment_and_period(
                enrollment_id=enrollment.id,
                academic_period_id=academic_period.id,
            )
        )
        if not incidents:
            scale = QualitativeScaleRepository.get_by_code("SE")
            if not scale:
                scale, _ = QualitativeScale.objects.get_or_create(
                    code="NA",
                    defaults={
                        "description": "Sin incidentes",
                        "numeric_equivalence": 10.0,
                    },
                )
            eval_obj, _ = BehaviorEvaluationRepository.get_or_create(
                enrollment=enrollment,
                academic_period=academic_period,
                defaults={"calculated_scale": scale, "evaluation_date": date.today()},
            )
            return eval_obj

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

        scale = QualitativeScaleRepository.get_by_code(scale_code)
        if not scale:
            scale, _ = QualitativeScale.objects.get_or_create(
                code=scale_code,
                defaults={
                    "description": "Escala autom\u00e1tica",
                    "numeric_equivalence": 5.0,
                },
            )

        eval_obj, _ = BehaviorEvaluationRepository.get_or_create(
            enrollment=enrollment,
            academic_period=academic_period,
            defaults={"calculated_scale": scale, "evaluation_date": date.today()},
        )
        if not eval_obj.final_scale:
            eval_obj.calculated_scale = scale
            eval_obj.save()
        return eval_obj

    @staticmethod
    @transaction.atomic
    def override_evaluation(evaluation, new_scale, reason=""):
        evaluation.final_scale = new_scale
        evaluation.override_reason = reason
        evaluation.save()
        return evaluation
