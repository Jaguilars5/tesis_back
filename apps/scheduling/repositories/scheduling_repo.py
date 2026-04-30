"""
Scheduling repositories - Acceso a datos para el módulo de horarios.

Centraliza las consultas de configuración de plantillas, disponibilidad de docentes
y asignaciones de slots.
"""

from django.db import models
from ..models import (
    ScheduleTemplateConfig,
    TimeSlot,
    TeacherAvailability,
    SubjectConstraint,
    ScheduleSlot,
)


class BaseRepository:
    """Repositorio base con métodos genéricos."""

    model = None

    @classmethod
    def get_all(cls, active_only=True):
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, "active"):
            queryset = queryset.filter(active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None


class ScheduleTemplateConfigRepository(BaseRepository):
    model = ScheduleTemplateConfig

    @classmethod
    def get_by_timing_regime(cls, timing_regime_id):
        """Obtiene la configuración para un régimen horario específico."""
        return cls.model.objects.filter(timing_regime_id=timing_regime_id).first()


class TimeSlotRepository(BaseRepository):
    model = TimeSlot

    @classmethod
    def list_by_regime(cls, timing_regime_id):
        """Lista los slots de un régimen horario, ordenados por día y hora."""
        return cls.model.objects.filter(timing_regime_id=timing_regime_id).order_by(
            "day_of_week", "start_time"
        )


class TeacherAvailabilityRepository(BaseRepository):
    model = TeacherAvailability

    @classmethod
    def list_by_teacher(cls, user_id, school_year_id):
        """Lista disponibilidad de un docente."""
        return cls.model.objects.filter(
            user_id=user_id, school_year_id=school_year_id
        ).select_related("time_slot")


class ScheduleSlotRepository(BaseRepository):
    model = ScheduleSlot

    @classmethod
    def list_by_section(cls, section_id, school_year_id):
        """Lista el horario de una sección específica."""
        return cls.model.objects.filter(
            teacher_subject_section__section_id=section_id,
            school_year_id=school_year_id,
            active=True,
        ).select_related("time_slot", "teacher_subject_section__subject", "classroom")

    @classmethod
    def get_conflict(cls, time_slot_id, classroom_id=None, user_id=None):
        """Verifica si hay conflicto de aula o docente en un slot dado."""
        if classroom_id:
            conflict = cls.model.objects.filter(
                time_slot_id=time_slot_id, classroom_id=classroom_id, active=True
            ).first()
            if conflict:
                return conflict
        if user_id:
            conflict = cls.model.objects.filter(
                time_slot_id=time_slot_id,
                teacher_subject_section__user_id=user_id,
                active=True,
            ).first()
            if conflict:
                return conflict
        return None


class SubjectConstraintRepository(BaseRepository):
    model = SubjectConstraint

    @classmethod
    def get_by_subject(cls, subject_id):
        """Obtiene restricciones de una materia."""
        return cls.model.objects.filter(subject_id=subject_id).first()
