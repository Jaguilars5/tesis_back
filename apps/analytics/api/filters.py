import django_filters
from ..models import StudentFeatureSnapshot, StudentRiskScore


class StudentRiskScoreFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name="enrollment__student__user__person__names",
        lookup_expr="icontains",
    )
    risk_label = django_filters.ChoiceFilter(
        choices=[("rojo", "Rojo"), ("amarillo", "Amarillo"), ("verde", "Verde")],
    )
    academic_period = django_filters.NumberFilter()

    class Meta:
        model = StudentRiskScore
        fields = ["risk_label", "academic_period"]


class StudentFeatureSnapshotFilter(django_filters.FilterSet):
    enrollment = django_filters.NumberFilter()
    academic_period = django_filters.NumberFilter()

    class Meta:
        model = StudentFeatureSnapshot
        fields = ["enrollment", "academic_period"]
