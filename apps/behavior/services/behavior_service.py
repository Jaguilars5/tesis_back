from datetime import date
from django.db import transaction
from apps.grading.models import QualitativeScale
from apps.grading.repositories.grading_repo import QualitativeScaleRepository
from ..models import BehaviorEvaluation
from ..repositories import ConductIncidentRepository


class BehaviorEvaluationService:
    @staticmethod
    @transaction.atomic
    def calculate_behavior_evaluation(enrollment, academic_period):
        incidents = ConductIncidentRepository.get_by_enrollment_and_period(
            enrollment_id=enrollment.id,
            academic_period_id=academic_period.id,
        )
        if not incidents.exists():
            scale = QualitativeScaleRepository.get_by_code("SE")
            if not scale:
                scale, _ = QualitativeScale.objects.get_or_create(
                    code="NA", defaults={
                        "description": "Sin incidentes",
                        "numeric_equivalence": 10.0,
                    }
                )
            eval_obj, _ = BehaviorEvaluation.objects.get_or_create(
                enrollment=enrollment,
                academic_period=academic_period,
                defaults={"calculated_scale": scale, "evaluation_date": date.today()},
            )
            return eval_obj

        max_severity = max(i.severity.numeric_level for i in incidents)
        severe_count = sum(1 for i in incidents if i.severity.numeric_level >= 3)
        total_incidents = incidents.count()

        if severe_count >= 3 or max_severity >= 3 and total_incidents >= 2:
            scale_code = "NA"
        elif max_severity >= 2 or total_incidents >= 3:
            scale_code = "AC"
        elif total_incidents >= 1:
            scale_code = "SA"
        else:
            scale_code = "SE"

        scale = QualitativeScaleRepository.get_by_code(scale_code)
        if not scale:
            scale, _ = QualitativeScale.objects.get_or_create(
                code=scale_code, defaults={
                    "description": "Escala automática",
                    "numeric_equivalence": 5.0,
                }
            )

        eval_obj, _ = BehaviorEvaluation.objects.get_or_create(
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
