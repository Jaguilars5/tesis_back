"""
Grading repositories - Acceso a datos para el módulo de calificaciones, asistencia y conducta.

Centraliza todas las consultas a la base de datos para evitar lógica de persistencia
en los servicios o vistas.
"""

from django.db import models

from ..models import Attendance, ConductIncident, StudentNote


class BaseRepository:
    """
    Repositorio base con métodos genéricos de consulta.
    """

    model = None

    @classmethod
    def get_all(cls, active_only=True):
        """
        Retorna todos los registros del modelo.
        Si active_only=True y el modelo tiene el campo 'active', filtra solo los activos.
        """
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, "active"):
            queryset = queryset.filter(active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        """
        Obtiene un registro por su clave primaria.
        Retorna None si no existe.
        """
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None


class StudentNoteRepository(BaseRepository):
    """
    Repositorio especializado para el modelo StudentNote.
    """

    model = StudentNote

    @classmethod
    def get_by_composite_key(
        cls,
        student_id,
        academic_activity_id,
        academic_period_id,
        teacher_subject_section_id,
    ):
        """
        Busca una nota específica basada en su clave compuesta única.
        """
        return cls.model.objects.filter(
            student_id=student_id,
            academic_activity_id=academic_activity_id,
            academic_period_id=academic_period_id,
            teacher_subject_section_id=teacher_subject_section_id,
        ).first()

    @classmethod
    def list_by_filters(
        cls, student_id=None, academic_period_id=None, subject_id=None, section_id=None
    ):
        """
        Lista notas aplicando filtros opcionales de estudiante, período, materia o sección.
        """
        queryset = cls.model.objects.all()
        if hasattr(cls.model, "active"):
            queryset = queryset.filter(active=True)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if subject_id:
            queryset = queryset.filter(teacher_subject_section__subject_id=subject_id)
        if section_id:
            queryset = queryset.filter(teacher_subject_section__section_id=section_id)
        return queryset.order_by("-created_at")


class AttendanceRepository(BaseRepository):
    """
    Repositorio especializado para el modelo Attendance.
    """

    model = Attendance

    @classmethod
    def get_by_unique_key(cls, student_id, teacher_subject_section_id, date):
        """
        Busca un registro de asistencia único para un estudiante, clase y fecha.
        """
        return cls.model.objects.filter(
            student_id=student_id,
            teacher_subject_section_id=teacher_subject_section_id,
            date=date,
        ).first()

    @classmethod
    def list_by_filters(
        cls,
        student_id=None,
        academic_period_id=None,
        section_id=None,
        date=None,
        status=None,
    ):
        """
        Lista registros de asistencia con filtros opcionales.
        """
        queryset = cls.model.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if section_id:
            queryset = queryset.filter(teacher_subject_section__section_id=section_id)
        if date:
            queryset = queryset.filter(date=date)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by("-date", "student__last_names", "student__names")


class ConductIncidentRepository(BaseRepository):
    """
    Repositorio especializado para el modelo ConductIncident.
    """

    model = ConductIncident

    @classmethod
    def list_by_filters(
        cls,
        student_id=None,
        academic_period_id=None,
        category=None,
        severity=None,
        family_notified=None,
    ):
        """
        Lista incidentes de conducta con filtros opcionales.
        """
        queryset = cls.model.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if category:
            queryset = queryset.filter(category=category)
        if severity:
            queryset = queryset.filter(severity=severity)
        if family_notified is not None:
            queryset = queryset.filter(family_notified=family_notified)
        return queryset.order_by(
            "-incident_date", "student__last_names", "student__names"
        )

