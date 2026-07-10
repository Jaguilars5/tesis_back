from decimal import Decimal

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import (
    StudentNoteRepositoryInterface,
    PeriodGradeSummaryRepositoryInterface,
    AnnualGradeSummaryRepositoryInterface,
)
from .models import StudentNote, PeriodGradeSummary, AnnualGradeSummary


class StudentNoteRepository(BaseRepository, StudentNoteRepositoryInterface):
    model = StudentNote

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_composite_key(cls, enrollment_id, evaluative_activity_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
        ).first()

    @classmethod
    def list_by_filters(
        cls, student_id=None, academic_period_id=None, subject_id=None, section_id=None
    ):
        queryset = cls.model.objects.all()
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(
                evaluative_activity__block_component__evaluation_block__academic_period_id=academic_period_id
            )
        if subject_id:
            queryset = queryset.filter(
                evaluative_activity__teacher_subject_section__subject_offering__subject_academic_config__subject_id=subject_id
            )
        if section_id:
            queryset = queryset.filter(enrollment__section_id=section_id)
        return queryset.order_by("-created_at")

    @classmethod
    def get_students_for_activity(
        cls, evaluative_activity_id, teacher_subject_section_id
    ):
        from apps.grading.evaluation.infrastructure.models import EvaluativeActivity
        from apps.students.models import Enrollment

        try:
            activity = EvaluativeActivity.objects.select_related(
                "block_component__evaluation_block__academic_period",
                "teacher_subject_section__subject_offering",
            ).get(id=evaluative_activity_id)
        except EvaluativeActivity.DoesNotExist:
            return None, []

        section_id = activity.teacher_subject_section.subject_offering.section_id

        enrollments = (
            Enrollment.objects.filter(
                section_id=section_id,
                enrollment_status="ACT",
            )
            .select_related(
                "student__user__person",
            )
            .order_by(
                "student__user__person__last_names", "student__user__person__names"
            )
        )

        existing_notes = cls.model.objects.filter(
            evaluative_activity_id=evaluative_activity_id,
            enrollment_id__in=enrollments.values_list("id", flat=True),
        ).select_related("enrollment")

        note_map = {n.enrollment_id: n for n in existing_notes}

        students_data = []
        for enr in enrollments:
            note = note_map.get(enr.id)
            students_data.append(
                {
                    "enrollment_id": enr.id,
                    "student_id": enr.student_id,
                    "student_name": enr.student.get_full_name(),
                    "note_obj": note,
                }
            )

        return activity, students_data

    @classmethod
    def list_for_risk_snapshot(cls, student_id, academic_period_id):
        return (
            cls.model.objects.filter(
                enrollment__student_id=student_id,
                evaluative_activity__block_component__evaluation_block__academic_period_id=academic_period_id,
            )
            .select_related(
                "evaluative_activity__teacher_subject_section__subject_offering__subject_academic_config__subject",
                "enrollment__student",
            )
            .order_by("created_at")
        )


class PeriodGradeSummaryRepository(
    BaseRepository, PeriodGradeSummaryRepositoryInterface
):
    model = PeriodGradeSummary

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
        ).select_related("subject_offering", "academic_period", "qualitative_scale")

    @classmethod
    def get_by_enrollment_offering_period(
        cls, enrollment, subject_offering, academic_period
    ):
        return cls.model.objects.filter(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
        ).first()

    @classmethod
    def get_failing(cls, academic_period_id):
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            is_failing=True,
        ).select_related("enrollment__student", "subject_offering")

    @classmethod
    def count_failing(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            is_failing=True,
        ).count()


class AnnualGradeSummaryRepository(
    BaseRepository, AnnualGradeSummaryRepositoryInterface
):
    model = AnnualGradeSummary

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
        ).select_related(
            "subject_offering__subject_academic_config__subject",
            "school_year",
        )

    @classmethod
    def get_by_enrollment_offering_year(cls, enrollment, subject_offering, school_year):
        return cls.model.objects.filter(
            enrollment=enrollment,
            subject_offering=subject_offering,
            school_year=school_year,
        ).first()

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id,
        ).select_related("enrollment", "subject_offering")

    @classmethod
    def get_failing_for_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            school_year_id=school_year_id,
            is_failing=True,
        ).select_related("enrollment__student", "subject_offering")

    @classmethod
    def count_failing(cls, enrollment_id, school_year_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            school_year_id=school_year_id,
            is_failing=True,
        ).count()


class EvaluationRepository:
    """Metodos de acceso a datos para calculos de evaluacion."""

    FORMATIVE_TYPES = {"FORMATIVA"}
    SUMMATIVE_TYPES = {"SUMATIVA", "PROJECT"}

    @staticmethod
    def _normalized_value(note):
        """Normaliza la nota a base 10.

        - Cuantitativa: ``numeric_score / max_score * 10``.
        - Cualitativa (sin nota numérica): ``qualitative_scale.numeric_equivalence``.

        Devuelve ``None`` si la nota no aporta valor (anulada / sin score).
        """
        if note.manually_overridden:
            return None
        if note.numeric_score is not None:
            return note.calculate_normalized_value()
        if note.qualitative_scale_id and note.qualitative_scale:
            return Decimal(str(note.qualitative_scale.numeric_equivalence))
        return None

    @classmethod
    def calculate_period_average_for_subject(
        cls, enrollment_id, subject_offering_id, academic_period_id=None
    ):
        """Promedio ponderado jerárquico (actividad → componente → bloque) del
        periodo, renormalizando en cada nivel sobre los pesos efectivamente
        calificados (promedio "vivo").

        Returns:
            ``None`` si no hay notas calificables; de lo contrario un dict con
            ``final`` (ponderado de todos los bloques), ``formative`` (bloques
            FORMATIVA) y ``summative`` (bloques SUMATIVA/PROJECT), todos
            ``Decimal`` cuantizados a 0.01.
        """
        notes = StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__block_component__evaluation_block__subject_offering_id=subject_offering_id,
        ).select_related(
            "evaluative_activity__block_component__evaluation_block",
            "qualitative_scale",
        )
        if academic_period_id is not None:
            notes = notes.filter(
                evaluative_activity__block_component__evaluation_block__academic_period_id=academic_period_id
            )

        # block_id -> {"weight", "block_type", "components": {comp_id: {"weight", "num", "den"}}}
        blocks = {}
        for note in notes:
            normalized = cls._normalized_value(note)
            if normalized is None:
                continue

            activity = note.evaluative_activity
            component = activity.block_component
            block = component.evaluation_block

            block_entry = blocks.setdefault(
                block.id,
                {
                    "weight": Decimal(str(block.weight_percentage)),
                    "block_type": block.block_type,
                    "components": {},
                },
            )
            comp_entry = block_entry["components"].setdefault(
                component.id,
                {
                    "weight": Decimal(str(component.internal_weight)),
                    "num": Decimal("0"),
                    "den": Decimal("0"),
                },
            )
            act_weight = Decimal(str(activity.internal_weight))
            comp_entry["num"] += act_weight * normalized
            comp_entry["den"] += act_weight

        if not blocks:
            return None

        block_grades = {}  # block_id -> (block_grade, weight, block_type)
        for block_id, block_entry in blocks.items():
            num = Decimal("0")
            den = Decimal("0")
            for comp_entry in block_entry["components"].values():
                if comp_entry["den"] == 0:
                    continue
                comp_grade = comp_entry["num"] / comp_entry["den"]
                num += comp_entry["weight"] * comp_grade
                den += comp_entry["weight"]
            if den == 0:
                continue
            block_grade = num / den
            block_grades[block_id] = (
                block_grade,
                block_entry["weight"],
                block_entry["block_type"],
            )

        if not block_grades:
            return None

        def _weighted(filter_types=None):
            num = Decimal("0")
            den = Decimal("0")
            for block_grade, weight, block_type in block_grades.values():
                if filter_types is not None and block_type not in filter_types:
                    continue
                num += weight * block_grade
                den += weight
            if den == 0:
                return None
            return num / den

        final = _weighted()
        formative = _weighted(cls.FORMATIVE_TYPES)
        summative = _weighted(cls.SUMMATIVE_TYPES)

        quant = lambda v: (
            v.quantize(Decimal("0.01")) if v is not None else Decimal("0.00")
        )
        return {
            "final": final.quantize(Decimal("0.01")),
            "formative": quant(formative),
            "summative": quant(summative),
        }
