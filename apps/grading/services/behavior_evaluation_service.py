from django.db import transaction
from ..models import QualitativeScale
from apps.attendance.models import BehaviorEvaluation, ConductIncident


class BehaviorEvaluationService:
    @staticmethod
    @transaction.atomic
    def calculate_behavior_evaluation(enrollment, academic_period):
        incidents = ConductIncident.objects.filter(
            enrollment=enrollment,
            academic_period=academic_period,
        )
        if not incidents.exists():
            scale = QualitativeScale.objects.filter(code="SE").first()
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
                defaults={"calculated_scale": scale},
            )
            return eval_obj

        max_severity = max(i.severity for i in incidents)
        severe_count = sum(1 for i in incidents if i.severity >= 3)
        total_incidents = incidents.count()

        if severe_count >= 3 or max_severity >= 3 and total_incidents >= 2:
            scale_code = "NA"
        elif max_severity >= 2 or total_incidents >= 3:
            scale_code = "AC"
        elif total_incidents >= 1:
            scale_code = "SA"
        else:
            scale_code = "SE"

        scale = QualitativeScale.objects.filter(code=scale_code).first()
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
            defaults={"calculated_scale": scale},
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
