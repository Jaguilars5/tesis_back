import django_filters

from ..infrastructure.models import QualitativeScale, QualitativeScaleSublevel


class QualitativeScaleFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = QualitativeScale
        fields = ["is_active"]


class QualitativeScaleSublevelFilter(django_filters.FilterSet):
    scale = django_filters.NumberFilter(field_name="scale_id")
    sublevel = django_filters.NumberFilter(field_name="sublevel_id")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = QualitativeScaleSublevel
        fields = ["scale", "sublevel", "is_active"]
