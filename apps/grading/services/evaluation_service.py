from decimal import Decimal
from django.db import models
from ..models import StudentNote, GradeChangeHistory


class EvaluationService:
    @staticmethod
    def calculate_macro_grade(enrollment, evaluation_macro):
        notes = StudentNote.objects.filter(
            enrollment=enrollment,
            class_assignment__evaluation_subcriteria__evaluation_criteria__evaluation_macro=evaluation_macro,
        )
        if not notes.exists():
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for note in notes:
            assignment = note.class_assignment
            subcriteria = assignment.evaluation_subcriteria
            criteria = subcriteria.evaluation_criteria

            sub_weight = subcriteria.internal_weight
            crit_weight = criteria.internal_weight

            if assignment.max_score > 0:
                normalized = (note.numeric_score / assignment.max_score) * Decimal("10")
            else:
                normalized = Decimal("0.00")

            combined_weight = (sub_weight / Decimal("100")) * (crit_weight / Decimal("100"))
            total_score += normalized * combined_weight
            total_weight += combined_weight

        if total_weight == 0:
            return None

        weighted_avg = total_score / total_weight
        return weighted_avg.quantize(Decimal("0.01"))

    @staticmethod
    def calculate_period_average(enrollment, academic_period):
        macros = academic_period.evaluation_macros.filter(active=True)
        if not macros.exists():
            return None

        total_score = Decimal("0.00")
        total_weight = Decimal("0.00")

        for macro in macros:
            macro_grade = EvaluationService.calculate_macro_grade(enrollment, macro)
            if macro_grade is not None:
                total_score += macro_grade * (macro.weight_percentage / Decimal("100"))
                total_weight += macro.weight_percentage / Decimal("100")

        if total_weight == 0:
            return None

        return (total_score / total_weight).quantize(Decimal("0.01"))

    @staticmethod
    def get_grade_hierarchy(class_assignment):
        subcriteria = class_assignment.evaluation_subcriteria
        criteria = subcriteria.evaluation_criteria
        macro = criteria.evaluation_macro
        period = macro.academic_period

        return {
            "class_assignment": class_assignment,
            "subcriteria": subcriteria,
            "criteria": criteria,
            "macro": macro,
            "academic_period": period,
        }

    @staticmethod
    def create_grade_change_history(student_note, new_score, user=None, reason=""):
        previous = student_note.numeric_score
        history = GradeChangeHistory.objects.create(
            student_note=student_note,
            modified_by_user=user,
            previous_score=previous,
            new_score=new_score,
            reason=reason,
        )
        student_note.numeric_score = new_score
        student_note.manually_overridden = True
        student_note.save()
        return history
