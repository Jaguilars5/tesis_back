import django_filters

from ..models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section


class SchoolYearFilter(django_filters.FilterSet):
    class Meta:
        model = SchoolYear
        fields = {
            "start_date": ["exact", "gte", "lte"],
            "end_date": ["exact", "gte", "lte"],
            "is_active": ["exact"],
        }


class AcademicLevelFilter(django_filters.FilterSet):
    class Meta:
        model = AcademicLevel
        fields = {
            "name": ["exact", "icontains"],
            "is_active": ["exact"],
        }


class AcademicSublevelFilter(django_filters.FilterSet):
    class Meta:
        model = AcademicSublevel
        fields = {
            "name": ["exact", "icontains"],
            "code": ["exact", "icontains"],
            "academic_level": ["exact"],
            "is_active": ["exact"],
        }


class AcademicGradeFilter(django_filters.FilterSet):
    class Meta:
        model = AcademicGrade
        fields = {
            "name": ["exact", "icontains"],
            "academic_sublevel": ["exact"],
            "is_active": ["exact"],
        }


class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = {
            "parallel": ["exact", "icontains"],
            "academic_grade": ["exact"],
            "school_year": ["exact"],
            "is_active": ["exact"],
        }
