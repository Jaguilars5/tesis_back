from rest_framework import serializers
from ..models import Student, Representative, Student_Representative


class StudentSerializer(serializers.ModelSerializer):
    """Serializer para Student"""

    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    section_name = serializers.CharField(
        source="section.get_level_grade_display", read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "uuid",
            "dni",
            "names",
            "last_names",
            "full_name",
            "birth_date",
            "age",
            "section",
            "section_name",
            "enrollment_number",
            "enrollment_date",
            "active",
            "sync_status",
            "synced_at",
            "created_at",
            "updated_at",
            "deleted_at",
            "sync_version",
            "device_origin",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "created_at",
            "updated_at",
            "enrollment_date",
            "full_name",
            "age",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_age(self, obj):
        return obj.get_age()


class RepresentativeSerializer(serializers.ModelSerializer):
    """Serializer para Representative"""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Representative
        fields = [
            "id",
            "dni",
            "names",
            "last_names",
            "full_name",
            "phone",
            "email",
            "address",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_name"]

    def get_full_name(self, obj):
        return obj.get_full_name()


class StudentRepresentativeSerializer(serializers.ModelSerializer):
    """Serializer para Student_Representative"""

    student_names = serializers.CharField(
        source="student.get_full_name", read_only=True
    )
    representative_names = serializers.CharField(
        source="representative.get_full_name", read_only=True
    )
    class Meta:
        model = Student_Representative
        fields = [
            "id",
            "student",
            "student_names",
            "representative",
            "representative_names",
            "kinship",
            "is_primary",
            "can_pickup",
            "emergency_contact",
            "receives_notifications",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentDetailSerializer(StudentSerializer):
    """Serializer detallado para Student con representantes"""

    representatives = StudentRepresentativeSerializer(
        source="student_representative_set", many=True, read_only=True
    )

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ["representatives"]


class RepresentativeDetailSerializer(RepresentativeSerializer):
    """Serializer detallado para Representative con estudiantes"""

    students_count = serializers.SerializerMethodField()

    class Meta(RepresentativeSerializer.Meta):
        fields = RepresentativeSerializer.Meta.fields + ["students_count"]

    def get_students_count(self, obj):
        return obj.student_representative_set.filter(student__active=True).count()
