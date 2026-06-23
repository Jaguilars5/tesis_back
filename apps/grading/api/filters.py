"""Filtros para el módulo de calificaciones (grading).

Define django-filter FilterSets para permitir filtros server-side via query params
con nombres planos que el frontend pueda usar, eliminando la necesidad de
nested ORM lookups desde el cliente.
"""

from django_filters import rest_framework as filters

from ..models import BlockComponent, EvaluativeActivity


class EvaluativeActivityFilter(filters.FilterSet):
    """Filtros para actividades evaluativas.

    Query params soportados (combinables con AND):
        - teacher_subject_section: id de la asignación docente-materia-sección
        - academic_period: id del período académico (resuelve a través de
          block_component → evaluation_block)
    """

    teacher_subject_section = filters.NumberFilter(
        field_name="teacher_subject_section_id"
    )
    academic_period = filters.NumberFilter(
        field_name="block_component__evaluation_block__academic_period_id"
    )

    class Meta:
        model = EvaluativeActivity
        fields = [
            "teacher_subject_section",
            "academic_period",
        ]


class BlockComponentFilter(filters.FilterSet):
    """Filtros para componentes de bloque.

    Query params soportados (combinables con AND):
        - evaluation_block: id del bloque de evaluación
        - subject_offering: id de la oferta de materia (a través de evaluation_block)
        - academic_period: id del período académico (a través de evaluation_block)
        - is_active: true|false
    """

    evaluation_block = filters.NumberFilter(field_name="evaluation_block_id")
    subject_offering = filters.NumberFilter(
        field_name="evaluation_block__subject_offering_id"
    )
    academic_period = filters.NumberFilter(
        field_name="evaluation_block__academic_period_id"
    )
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = BlockComponent
        fields = [
            "evaluation_block",
            "subject_offering",
            "academic_period",
            "is_active",
        ]
