import logging

from rest_framework import serializers

from ..infrastructure.models import Enrollment, Kinship, SpecialNeedsType, Student, StudentRepresentative

logger = logging.getLogger(__name__)


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    primary_representative = serializers.SerializerMethodField()
    parish = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    document_number = serializers.CharField(write_only=True, required=False)
    names = serializers.CharField(write_only=True, required=False)
    last_names = serializers.CharField(write_only=True, required=False)
    birth_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    document_type = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "student_code",
            "special_needs_type",
            "has_special_needs",
            "full_name",
            "age",
            "is_active",
            "created_at",
            "primary_representative",
            "parish",
            "document_number",
            "names",
            "last_names",
            "birth_date",
            "email",
            "phone",
            "document_type",
        ]
        read_only_fields = ["id", "created_at", "full_name", "age"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        person = instance.user.person if hasattr(instance.user, "person") else None
        if person:
            ret["document_number"] = person.document_number
            ret["names"] = person.names
            ret["last_names"] = person.last_names
            ret["birth_date"] = str(person.birth_date) if person.birth_date else None
            ret["email"] = person.email
            ret["phone"] = person.phone
            ret["parish_id"] = person.parish_id
            ret["parish_name"] = person.parish.name if person.parish else None
            ret["city_id"] = person.parish.city_id if person.parish else None
            ret["city_name"] = person.parish.city.name if person.parish and person.parish.city_id else None
            ret["document_type_id"] = person.document_type_id
            ret["document_type_name"] = person.document_type.name if person.document_type else None
        else:
            ret["document_number"] = None
            ret["names"] = None
            ret["last_names"] = None
            ret["birth_date"] = None
            ret["email"] = None
            ret["phone"] = None
            ret["parish_id"] = None
            ret["parish_name"] = None
            ret["city_id"] = None
            ret["city_name"] = None
            ret["document_type_id"] = None
            ret["document_type_name"] = None
        return ret

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_age(self, obj):
        return obj.get_age()

    def get_primary_representative(self, obj):
        cache = getattr(obj, "_primary_rep_cache", None)
        if cache:
            rep = cache[0]
        else:
            rep = (
                obj.representatives_set.order_by("-is_primary", "-created_at")
                .select_related("kinship", "user__person")
                .first()
            )
        if rep is None:
            return None
        result = {
            "id": rep.id,
            "user_names": rep.user.get_full_name(),
            "kinship": rep.kinship_id,
            "kinship_name": rep.kinship.name,
        }
        return result


class StudentRepresentativeSerializer(serializers.ModelSerializer):
    student_names = serializers.CharField(
        source="student.get_full_name", read_only=True
    )
    user_names = serializers.CharField(source="user.get_full_name", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    names = serializers.CharField(source="user.person.names", read_only=True)
    last_names = serializers.CharField(source="user.person.last_names", read_only=True)
    dni = serializers.CharField(source="user.person.document_number", read_only=True)
    email = serializers.EmailField(source="user.person.email", read_only=True)
    phone = serializers.CharField(source="user.person.phone", read_only=True)

    class Meta:
        model = StudentRepresentative
        fields = [
            "id",
            "student",
            "student_names",
            "user",
            "user_names",
            "user_name",
            "names",
            "last_names",
            "dni",
            "email",
            "phone",
            "kinship",
            "is_primary",
            "emergency_contact",
            "receives_notifications",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def to_internal_value(self, data):
        if "kinship" in data and isinstance(data["kinship"], str):
            try:
                data = dict(data)
                kinship_code = data["kinship"].upper()[:30]
                kinship_obj, _ = Kinship.objects.get_or_create(
                    code=kinship_code,
                    defaults={"name": data["kinship"]}
                )
                data["kinship"] = kinship_obj.id
            except Exception:
                pass
        return super().to_internal_value(data)


class StudentDetailSerializer(StudentSerializer):
    representatives = StudentRepresentativeSerializer(
        source="representatives_set", many=True, read_only=True
    )

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + [
            "representatives",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    section_name = serializers.CharField(source="section.__str__", read_only=True)
    status_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def get_status_name(self, obj):
        return obj.get_enrollment_status_display()


class KinshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kinship
        fields = ["id", "code", "name", "description", "is_active"]


class StudentCreateSerializer(serializers.Serializer):
    document_number = serializers.CharField(max_length=20)
    names = serializers.CharField(max_length=100)
    last_names = serializers.CharField(max_length=100)
    birth_date = serializers.DateField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    parish = serializers.IntegerField(required=False, allow_null=True)
    document_type = serializers.IntegerField(required=False, allow_null=True)
    has_special_needs = serializers.BooleanField(required=False, default=False)
    special_needs_type = serializers.IntegerField(required=False, allow_null=True)

    def validate_document_number(self, value):
        from apps.people.models import Person
        if Person.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("Este documento ya está registrado.")
        return value


class SpecialNeedsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialNeedsType
        fields = "__all__"


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "student", "section", "enrollment_status", "enrollment_date"]
        read_only_fields = ["enrollment_status"]
