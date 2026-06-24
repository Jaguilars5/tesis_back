import django_filters

from ..infrastructure.models import QualitativeScale


class QualitativeScaleFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = QualitativeScale
        fields = ["is_active"]
