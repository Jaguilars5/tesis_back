"""
GradingService - Lógica de negocio para calificaciones, asistencia y conducta.

Este servicio actúa como intermediario entre los controladores (API) y los repositorios.
Garantiza que las reglas de negocio (como la normalización de notas) se apliquen de manera
consistente y maneja transacciones atómicas.
"""

from decimal import Decimal

from django.db import transaction
from django.db import models

from apps.academic.models import Academic_Activity

from ..models import Attendance, ConductIncident, StudentNote
from ..repositories import (
    AttendanceRepository,
    ConductIncidentRepository,
    StudentNoteRepository,
)


class GradingService:
    """
    Servicio principal para la gestión de datos académicos del estudiante.
    """

    @staticmethod
    def _normalize_note(note_value, value_max):
        """
        Normaliza una nota a base 10 de forma interna.
        """
        value_max = Decimal(value_max)
        if value_max == 0:
            return Decimal("0.00")
        return ((Decimal(note_value) / value_max) * Decimal("10")).quantize(
            Decimal("0.01")
        )

    @staticmethod
    @transaction.atomic
    def create_student_note(
        student_id,
        academic_activity_id,
        academic_period_id,
        teacher_subject_section_id,
        note_value,
        observation="",
        device_origin=None,
    ):
        """
        Crea o actualiza una nota de estudiante.
        Si ya existe una nota para la misma combinación de estudiante, actividad,
        período y sección, se actualiza el valor existente.
        """
        activity = Academic_Activity.objects.get(id=academic_activity_id)
        normalized_value = GradingService._normalize_note(
            note_value, activity.value_max
        )

        existing = StudentNoteRepository.get_by_composite_key(
            student_id,
            academic_activity_id,
            academic_period_id,
            teacher_subject_section_id,
        )
        if existing:
            existing.note_value = note_value
            existing.normalized_value = normalized_value
            existing.observation = observation
            existing.sync_status = "pending"
            existing.device_origin = device_origin
            existing.full_clean()
            existing.save()
            return existing

        note = StudentNote(
            student_id=student_id,
            academic_activity_id=academic_activity_id,
            academic_period_id=academic_period_id,
            teacher_subject_section_id=teacher_subject_section_id,
            note_value=note_value,
            normalized_value=normalized_value,
            observation=observation,
            sync_status="pending",
            device_origin=device_origin,
        )
        note.full_clean()
        note.save()
        return note

    @staticmethod
    def get_student_note(note_id):
        """
        Recupera una nota por su ID. Lanza ValueError si no existe.
        """
        note = StudentNoteRepository.get_by_id(note_id)
        if not note:
            raise ValueError(f"Calificación {note_id} no encontrada")
        return note

    @staticmethod
    def list_student_notes(
        student_id=None, academic_period_id=None, subject_id=None, section_id=None
    ):
        """
        Lista notas filtradas por diversos criterios.
        """
        return StudentNoteRepository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            section_id=section_id,
        )

    @staticmethod
    @transaction.atomic
    def update_student_note(note_id, **kwargs):
        """
        Actualiza campos específicos de una nota.
        Recalcula el valor normalizado si la nota numérica cambia.
        """
        note = GradingService.get_student_note(note_id)
        if "note_value" in kwargs:
            activity = kwargs.get("academic_activity", note.academic_activity)
            note.normalized_value = GradingService._normalize_note(
                kwargs["note_value"], activity.value_max
            )
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
        note.full_clean()
        note.save()
        return note

    @staticmethod
    def deactivate_student_note(note_id):
        """
        Realiza un borrado lógico de una nota.
        """
        note = GradingService.get_student_note(note_id)
        note.active = False
        note.save()
        return note

    @staticmethod
    def calculate_period_average(
        student_id, academic_period_id, subject_id=None, section_id=None
    ):
        """
        Calcula el promedio de notas normalizadas para un estudiante en un período dado.
        """
        queryset = StudentNoteRepository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            section_id=section_id,
        )
        if not queryset.exists():
            return None
        average = queryset.aggregate(models.Avg("normalized_value"))[
            "normalized_value__avg"
        ]
        if average is None:
            return None
        return Decimal(average).quantize(Decimal("0.01"))

    @staticmethod
    @transaction.atomic
    def create_attendance(
        student_id,
        teacher_subject_section_id,
        academic_period_id,
        date,
        status,
        observation="",
        device_origin=None,
    ):
        """
        Registra la asistencia de un estudiante.
        Si ya existe registro para la fecha/clase, lo actualiza.
        """
        existing = AttendanceRepository.get_by_unique_key(
            student_id, teacher_subject_section_id, date
        )
        if existing:
            existing.academic_period_id = academic_period_id
            existing.status = status
            existing.observation = observation
            existing.device_origin = device_origin
            existing.full_clean()
            existing.save()
            return existing

        attendance = Attendance(
            student_id=student_id,
            teacher_subject_section_id=teacher_subject_section_id,
            academic_period_id=academic_period_id,
            date=date,
            status=status,
            observation=observation,
            device_origin=device_origin,
        )
        attendance.full_clean()
        attendance.save()
        return attendance

    @staticmethod
    def get_attendance(attendance_id):
        """
        Recupera un registro de asistencia por ID.
        """
        attendance = AttendanceRepository.get_by_id(attendance_id)
        if not attendance:
            raise ValueError(f"Asistencia {attendance_id} no encontrada")
        return attendance

    @staticmethod
    def list_attendance(
        student_id=None,
        academic_period_id=None,
        section_id=None,
        date=None,
        status=None,
    ):
        """
        Lista registros de asistencia con filtros.
        """
        return AttendanceRepository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            section_id=section_id,
            date=date,
            status=status,
        )

    @staticmethod
    @transaction.atomic
    def update_attendance(attendance_id, **kwargs):
        """
        Actualiza campos de un registro de asistencia.
        """
        attendance = GradingService.get_attendance(attendance_id)
        for key, value in kwargs.items():
            if hasattr(attendance, key):
                setattr(attendance, key, value)
        attendance.full_clean()
        attendance.save()
        return attendance

    @staticmethod
    def delete_attendance(attendance_id):
        """
        Elimina físicamente un registro de asistencia.
        """
        attendance = GradingService.get_attendance(attendance_id)
        attendance.delete()
        return True

    @staticmethod
    @transaction.atomic
    def create_conduct_incident(
        student_id,
        reported_by_id,
        academic_period_id,
        incident_date,
        category,
        severity,
        description="",
        family_notified=False,
        device_origin=None,
    ):
        """
        Registra un nuevo incidente de conducta.
        """
        incident = ConductIncident(
            student_id=student_id,
            reported_by_id=reported_by_id,
            academic_period_id=academic_period_id,
            incident_date=incident_date,
            category=category,
            severity=severity,
            description=description,
            family_notified=family_notified,
            device_origin=device_origin,
        )
        incident.full_clean()
        incident.save()
        return incident

    @staticmethod
    def get_conduct_incident(incident_id):
        """
        Recupera un incidente de conducta por ID.
        """
        incident = ConductIncidentRepository.get_by_id(incident_id)
        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")
        return incident

    @staticmethod
    def list_conduct_incidents(
        student_id=None,
        academic_period_id=None,
        category=None,
        severity=None,
        family_notified=None,
    ):
        """
        Lista incidentes de conducta filtrados.
        """
        return ConductIncidentRepository.list_by_filters(
            student_id=student_id,
            academic_period_id=academic_period_id,
            category=category,
            severity=severity,
            family_notified=family_notified,
        )

    @staticmethod
    @transaction.atomic
    def update_conduct_incident(incident_id, **kwargs):
        """
        Actualiza campos de un incidente de conducta.
        """
        incident = GradingService.get_conduct_incident(incident_id)
        for key, value in kwargs.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
        incident.full_clean()
        incident.save()
        return incident

    @staticmethod
    def delete_conduct_incident(incident_id):
        """
        Elimina físicamente un incidente de conducta.
        """
        incident = GradingService.get_conduct_incident(incident_id)
        incident.delete()
        return True

