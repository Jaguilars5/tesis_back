from rest_framework import serializers

from ..infrastructure.models import AcademicPeriod


class AcademicPeriodSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
    period_type_name = serializers.CharField(
        source="period_type.name", read_only=True, allow_null=True
    )

    class Meta:
        model = AcademicPeriod
        fields = [
            "id",
            "code",
            "school_year",
            "name",
            "period_type",
            "start_date",
            "end_date",
            "year_weight",
            "is_regular_period",
            "is_active",
            "school_year_name",
            "period_type_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
