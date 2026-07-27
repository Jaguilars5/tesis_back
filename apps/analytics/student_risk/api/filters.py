"""
Filtros de django-filter para riesgo estudiantil.
"""

import django_filters

from ..infrastructure.models import (
    RiskFactor,
    StudentRiskScore,
    StudentRiskFactor,
    StudentFeatureSnapshot,
)


class RiskFactorFilter(django_filters.FilterSet):
    """Filtros para catálogo de factores de riesgo."""

    code = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = RiskFactor
        fields = ["code", "name"]


class StudentRiskScoreFilter(django_filters.FilterSet):
    """Filtros para puntajes de riesgo."""

    RISK_TYPE_CHOICES = [
        ("general", "General"),
        ("annual", "Anual"),
        ("dropout", "Desercion"),
    ]

    enrollment = django_filters.NumberFilter()
    academic_period = django_filters.NumberFilter()
    risk_type = django_filters.ChoiceFilter(
        method="filter_risk_type",
        choices=RISK_TYPE_CHOICES,
    )
    risk_label = django_filters.ChoiceFilter(
        choices=[("verde", "Verde"), ("amarillo", "Amarillo"), ("rojo", "Rojo")]
    )
    risk_score__gte = django_filters.NumberFilter(
        field_name="risk_score", lookup_expr="gte"
    )
    risk_score__lte = django_filters.NumberFilter(
        field_name="risk_score", lookup_expr="lte"
    )
    calculated_at__gte = django_filters.DateTimeFilter(
        field_name="calculated_at", lookup_expr="gte"
    )
    calculated_at__lte = django_filters.DateTimeFilter(
        field_name="calculated_at", lookup_expr="lte"
    )

    class Meta:
        model = StudentRiskScore
        fields = ["enrollment", "academic_period", "risk_label", "risk_type"]

    def filter_risk_type(self, queryset, name, value):
        if value == "annual":
            return queryset.filter(model_version__startswith="annual-risk")
        if value == "dropout":
            return queryset.filter(model_version__startswith="dropout-risk")
        return queryset.exclude(model_version__startswith="annual-risk").exclude(
            model_version__startswith="dropout-risk"
        )


class StudentRiskFactorFilter(django_filters.FilterSet):
    """Filtros para factores de riesgo por estudiante."""

    student_risk_score = django_filters.NumberFilter()
    risk_factor = django_filters.NumberFilter()

    class Meta:
        model = StudentRiskFactor
        fields = ["student_risk_score", "risk_factor"]


class StudentFeatureSnapshotFilter(django_filters.FilterSet):
    """Filtros para snapshots de features."""

    enrollment = django_filters.NumberFilter()
    academic_period = django_filters.NumberFilter()
    is_current = django_filters.BooleanFilter()
    snapshot_trigger = django_filters.ChoiceFilter(
        choices=[("MANUAL", "Manual"), ("AUTO", "Automático"), ("BATCH", "Por Lote")]
    )
    failing_subjects_count__gte = django_filters.NumberFilter(
        field_name="failing_subjects_count", lookup_expr="gte"
    )
    attendance_rate__lte = django_filters.NumberFilter(
        field_name="attendance_rate", lookup_expr="lte"
    )

    class Meta:
        model = StudentFeatureSnapshot
        fields = [
            "enrollment",
            "academic_period",
            "is_current",
            "snapshot_trigger",
        ]
