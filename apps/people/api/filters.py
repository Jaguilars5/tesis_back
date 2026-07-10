from django_filters import rest_framework as filters

from ..infrastructure.models import City, DocumentType, Parish, Person


class ParishFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    code = filters.CharFilter(lookup_expr="icontains")
    parish_type = filters.CharFilter(lookup_expr="exact")
    city = filters.NumberFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = Parish
        fields = ["name", "code", "parish_type", "city", "is_active"]


class CityFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    code = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = City
        fields = ["name", "code", "is_active"]


class DocumentTypeFilter(filters.FilterSet):
    code = filters.CharFilter(lookup_expr="icontains")
    name = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()

    class Meta:
        model = DocumentType
        fields = ["code", "name", "is_active"]


class PersonFilter(filters.FilterSet):
    names = filters.CharFilter(lookup_expr="icontains")
    last_names = filters.CharFilter(lookup_expr="icontains")
    document_number = filters.CharFilter(lookup_expr="icontains")
    email = filters.CharFilter(lookup_expr="icontains")
    is_active = filters.BooleanFilter()
    document_type = filters.NumberFilter()
    parish = filters.NumberFilter()
    city = filters.NumberFilter(field_name="parish__city")

    class Meta:
        model = Person
        fields = ["names", "last_names", "document_number", "email", "is_active", "document_type", "parish", "city"]
