"""
Filtros de django-filter para alertas tempranas.
"""

import django_filters

from ..infrastructure.models import EarlyAlert


class EarlyAlertFilter(django_filters.FilterSet):
    """Filtros para el endpoint de alertas tempranas."""

    attended = django_filters.BooleanFilter()
    urgency_level = django_filters.ChoiceFilter(
        choices=EarlyAlert._meta.get_field("urgency_level").choices
    )
    alert_type = django_filters.ChoiceFilter(
        choices=EarlyAlert._meta.get_field("alert_type").choices
    )
    enrollment = django_filters.NumberFilter()
    academic_period = django_filters.NumberFilter()
    detected_at__gte = django_filters.DateTimeFilter(
        field_name="detected_at", lookup_expr="gte"
    )
    detected_at__lte = django_filters.DateTimeFilter(
        field_name="detected_at", lookup_expr="lte"
    )

    class Meta:
        model = EarlyAlert
        fields = [
            "attended",
            "urgency_level",
            "alert_type",
            "enrollment",
            "academic_period",
        ]
