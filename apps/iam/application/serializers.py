import logging

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from ..infrastructure.models import User, Role, Permission, RolePermission

logger = logging.getLogger(__name__)


class UserLoginDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    dni = serializers.CharField(read_only=True)
    names = serializers.CharField(read_only=True)
    last_names = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True, allow_null=True)
    role_id = serializers.IntegerField(read_only=True, allow_null=True)
    student_id = serializers.IntegerField(read_only=True, allow_null=True)
    is_active = serializers.BooleanField(read_only=True)
    must_change_password = serializers.BooleanField(read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), read_only=True)


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserLoginDataSerializer(read_only=True)


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    user = UserLoginDataSerializer(read_only=True)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.payload.get("user_id")
        if user_id:
            try:
                user = User.objects.get(id=int(user_id))
                person = user.person
                first_role = user.user_roles.select_related("role").first()
                from apps.students.models import Student

                student = Student.objects.filter(user=user).first()
                student_id = student.pk if student else None
                data["user"] = {
                    "id": user.id,
                    "username": user.username,
                    "dni": person.document_number if person else "",
                    "names": person.names if person else "",
                    "last_names": person.last_names if person else "",
                    "email": person.email if person else "",
                    "role": first_role.role.code if first_role else None,
                    "role_id": first_role.role.id if first_role else None,
                    "student_id": student_id,
                    "is_active": user.is_active,
                    "must_change_password": user.must_change_password,
                    "permissions": list(user.get_all_permissions()),
                }
            except User.DoesNotExist:
                pass
        return data


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        person = user.person
        first_role = user.user_roles.select_related("role").first()
        from apps.students.models import Student

        student = Student.objects.filter(user=user).first()
        student_id = student.pk if student else None
        logger.info(
            "[LoginSerializer] user=%s, student=%s, student_id=%s",
            user.id, student, student_id,
        )
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "dni": person.document_number if person else "",
            "names": person.names if person else "",
            "last_names": person.last_names if person else "",
            "email": person.email if person else "",
            "role": first_role.role.code if first_role else None,
            "role_id": first_role.role.id if first_role else None,
            "student_id": student_id,
            "is_active": user.is_active,
            "must_change_password": user.must_change_password,
            "permissions": list(user.get_all_permissions()),
        }
        return data


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "code", "description", "module", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RolePermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = ["id", "role", "permission", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoleDetailSerializer(serializers.ModelSerializer):
    role_permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "description", "is_active", "role_permissions", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserListSerializer(serializers.ModelSerializer):
    dni = serializers.CharField(source="person.document_number", read_only=True)
    names = serializers.CharField(source="person.names", read_only=True)
    last_names = serializers.CharField(source="person.last_names", read_only=True)
    email = serializers.CharField(source="person.email", read_only=True)
    role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "dni", "names", "last_names", "email", "role", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_role(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        return first_role.role.code if first_role else None


class UserDetailSerializer(serializers.ModelSerializer):
    dni = serializers.CharField(source="person.document_number", read_only=True)
    names = serializers.CharField(source="person.names", read_only=True)
    last_names = serializers.CharField(source="person.last_names", read_only=True)
    email = serializers.CharField(source="person.email", read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "dni", "names", "last_names", "email", "role", "role_id", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "username", "created_at", "updated_at"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_role(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        if first_role:
            return RoleDetailSerializer(first_role.role, context=self.context).data
        return None

    def validate_email(self, value):
        from apps.people.models import Person
        instance = self.instance
        qs = Person.objects.filter(email=value)
        if instance and instance.person_id:
            qs = qs.exclude(id=instance.person_id)
        if qs.exists():
            raise serializers.ValidationError("Este email ya est\u00e1 registrado.")
        return value


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    document_number = serializers.CharField(max_length=20)
    names = serializers.CharField(max_length=100)
    last_names = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.IntegerField()

    def validate_email(self, value):
        from apps.people.models import Person
        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya est\u00e1 registrado.")
        return value

    def validate_document_number(self, value):
        from apps.people.models import Person
        if Person.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("Este documento ya est\u00e1 registrado.")
        return value


