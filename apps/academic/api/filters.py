"""Filtros para el módulo académico.

Define django-filter FilterSets para permitir filtros server-side via query params
en los endpoints de la app academic.
"""
from django_filters import rest_framework as filters

from ..models import TeacherSubjectSection


class TeacherSubjectSectionFilter(filters.FilterSet):
    """Filtros para el endpoint de asignaciones docente-materia.

    Query params soportados (combinables con AND):
        - academic_grade: id del grado académico
        - school_year: id del año lectivo
        - section: id de la sección
        - subject: id de la materia
        - user: id del docente
        - is_active: true|false
    """

    academic_grade = filters.NumberFilter(
        field_name="subject_offering__section__academic_grade_id"
    )
    school_year = filters.NumberFilter(
        field_name="subject_offering__section__school_year_id"
    )
    section = filters.NumberFilter(
        field_name="subject_offering__section_id"
    )
    subject = filters.NumberFilter(
        field_name="subject_offering__subject_academic_config__subject_id"
    )
    user = filters.NumberFilter(field_name="user_id")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = TeacherSubjectSection
        fields = [
            "academic_grade",
            "school_year",
            "section",
            "subject",
            "user",
            "is_active",
        ]
