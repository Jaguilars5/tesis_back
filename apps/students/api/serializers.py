from rest_framework import serializers
from ..models import Enrollment, EnrollmentStatus, Student, Student_Representative


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "person",
            "student_code",
            "full_name",
            "age",
            "active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "full_name", "age"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_age(self, obj):
        return obj.get_age()


class StudentRepresentativeSerializer(serializers.ModelSerializer):
    student_names = serializers.CharField(
        source="student.get_full_name", read_only=True
    )
    person_names = serializers.CharField(
        source="person.get_full_name", read_only=True
    )

    class Meta:
        model = Student_Representative
        fields = [
            "id",
            "student",
            "student_names",
            "person",
            "person_names",
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
    representatives = StudentRepresentativeSerializer(
        source="representatives_set", many=True, read_only=True
    )

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ["representatives"]


class EnrollmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentStatus
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    section_name = serializers.CharField(source="section.__str__", read_only=True)
    status_name = serializers.CharField(source="enrollment_status.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["student", "section", "enrollment_status", "enrollment_date", "device_origin"]
