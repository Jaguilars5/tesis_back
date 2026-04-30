"""
SchedulingService - Lógica de negocio para la gestión de horarios escolares.
"""

from django.db import transaction
from ..repositories import (
    ScheduleSlotRepository,
    TimeSlotRepository,
    TeacherAvailabilityRepository,
    ScheduleTemplateConfigRepository,
)
from ..models import ScheduleSlot, TimeSlot


class SchedulingService:
    """
    Servicio para orquestar la creación de slots, validación de conflictos
    y gestión de disponibilidades.
    """

    @staticmethod
    @transaction.atomic
    def assign_slot(
        teacher_subject_section_id, school_year_id, time_slot_id, classroom_id=None
    ):
        """
        Asigna un docente/materia/sección a una franja horaria.
        Valida que no existan conflictos de aula o de docente.
        """
        from apps.academic.models import Teacher_Subject_Section

        tss = Teacher_Subject_Section.objects.get(id=teacher_subject_section_id)

        # Validar conflictos
        conflict = ScheduleSlotRepository.get_conflict(
            time_slot_id, classroom_id=classroom_id, user_id=tss.user_id
        )
        if conflict:
            raise ValueError(f"Conflicto detectado en el slot: {conflict}")

        # Validar disponibilidad del docente
        availability = TeacherAvailabilityRepository.list_by_teacher(
            tss.user_id, school_year_id
        ).filter(time_slot_id=time_slot_id, is_available=False)

        if availability.exists():
            raise ValueError("El docente no está disponible en este horario")

        slot = ScheduleSlot(
            teacher_subject_section_id=teacher_subject_section_id,
            school_year_id=school_year_id,
            time_slot_id=time_slot_id,
            classroom_id=classroom_id,
            is_manual=True,
        )
        slot.full_clean()
        slot.save()
        return slot

    @staticmethod
    def get_section_schedule(section_id, school_year_id):
        """Retorna el horario completo de una sección."""
        return ScheduleSlotRepository.list_by_section(section_id, school_year_id)

    @staticmethod
    def deactivate_slot(slot_id):
        """Realiza borrado lógico de un slot de horario."""
        slot = ScheduleSlotRepository.get_by_id(slot_id)
        if slot:
            slot.active = False
            slot.save()
            return True
        return False
