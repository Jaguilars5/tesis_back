from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..infrastructure.models import City, DocumentType, Parish, Person


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DocumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ParishSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parish
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PersonSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    age = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return obj.get_full_name()

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_age(self, obj):
        return obj.get_age()
