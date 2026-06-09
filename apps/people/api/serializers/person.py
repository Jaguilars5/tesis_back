from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from ...models import Person


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
