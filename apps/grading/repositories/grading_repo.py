"""
Grading repositories - Acceso a datos para el módulo de calificaciones, asistencia y conducta.

Centraliza todas las consultas a la base de datos para evitar lógica de persistencia
en los servicios o vistas.
"""

from django.db import models
from apps.core.repositories.base import BaseRepository
from ..models import (
    ActivityType,
    BlockComponent,
    EvaluationBlock,
    EvaluativeActivity,
    GradeChangeHistory,
    QualitativeScale,
    QualitativeScaleSublevel,
    StudentNote,
)


class StudentNoteRepository(BaseRepository):
    """
    Repositorio especializado para el modelo StudentNote.
    """

    model = StudentNote

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_composite_key(
        cls,
        enrollment_id,
        evaluative_activity_id,
    ):
        """
        Busca una nota específica basada en matrícula y actividad evaluativa.
        """
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity_id=evaluative_activity_id,
        ).first()

    @classmethod
    def list_by_filters(
        cls, student_id=None, academic_period_id=None, subject_id=None, section_id=None
    ):
        """
        Lista notas aplicando filtros opcionales de estudiante, período, materia o sección.
        """
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
    def list_for_risk_snapshot(cls, student_id, academic_period_id):
        """
        Lista notas activas con relaciones necesarias para construir features.
        """
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


class EvaluationBlockRepository(BaseRepository):
    model = EvaluationBlock

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("academic_period")


class BlockComponentRepository(BaseRepository):
    model = BlockComponent

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("evaluation_block")


class EvaluativeActivityRepository(BaseRepository):
    model = EvaluativeActivity

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related(
            "block_component", "teacher_subject_section", "activity_type"
        )


class GradeChangeHistoryRepository(BaseRepository):
    model = GradeChangeHistory

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("student_note", "modified_by_user")


class QualitativeScaleRepository(BaseRepository):
    model = QualitativeScale

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None


class ActivityTypeRepository(BaseRepository):
    model = ActivityType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")


class QualitativeScaleSublevelRepository(BaseRepository):
    model = QualitativeScaleSublevel

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("scale", "sublevel")
