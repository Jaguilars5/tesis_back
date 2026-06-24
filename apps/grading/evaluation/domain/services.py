from decimal import Decimal

from ..infrastructure.models import EvaluationBlock


class EvaluationService:
    """L\u00f3gica de negocio para bloques, componentes y actividades evaluativas."""

    @staticmethod
    def calculate_block_grade(enrollment, evaluation_block):
        from apps.grading.student_note.infrastructure.models import StudentNote

        notes = StudentNote.objects.filter(
            enrollment=enrollment,
            evaluative_activity__block_component__evaluation_block=evaluation_block,
        )
        if not notes.exists():
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for note in notes:
            activity = note.evaluative_activity
            component = activity.block_component

            act_weight = activity.internal_weight
            comp_weight = component.internal_weight

            if activity.max_score > 0:
                normalized = (note.numeric_score / activity.max_score) * Decimal("10")
            else:
                normalized = Decimal("0.00")

            combined_weight = (act_weight / Decimal("100")) * (comp_weight / Decimal("100"))
            total_score += normalized * combined_weight
            total_weight += combined_weight

        if total_weight == 0:
            return None

        weighted_avg = total_score / total_weight
        return weighted_avg.quantize(Decimal("0.01"))

    @staticmethod
    def calculate_period_average(enrollment, academic_period):
        blocks = academic_period.evaluation_blocks.filter(is_active=True)
        if not blocks.exists():
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for block in blocks:
            block_grade = EvaluationService.calculate_block_grade(enrollment, block)
            if block_grade is not None:
                total_score += block_grade * (block.weight_percentage / Decimal("100"))
                total_weight += block.weight_percentage / Decimal("100")

        if total_weight == 0:
            return None

        return (total_score / total_weight).quantize(Decimal("0.01"))

    @staticmethod
    def get_grade_hierarchy(evaluative_activity):
        component = evaluative_activity.block_component
        block = component.evaluation_block
        period = block.academic_period

        return {
            "evaluative_activity": evaluative_activity,
            "component": component,
            "block": block,
            "academic_period": period,
        }
