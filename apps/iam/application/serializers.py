import logging

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from ..infrastructure.models import User, Role, Permission, RolePermission, UserRole

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


class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=150)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)


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
            user.id,
            student,
            student_id,
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
        fields = ["id", "code", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoleDetailSerializer(serializers.ModelSerializer):
    role_permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "role_permissions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserListSerializer(serializers.ModelSerializer):
    dni = serializers.CharField(source="person.document_number", read_only=True)
    names = serializers.CharField(source="person.names", read_only=True)
    last_names = serializers.CharField(source="person.last_names", read_only=True)
    email = serializers.CharField(source="person.email", read_only=True)
    birth_date = serializers.DateField(source="person.birth_date", read_only=True, allow_null=True)
    phone = serializers.CharField(source="person.phone", read_only=True)
    parish_id = serializers.IntegerField(source="person.parish_id", read_only=True, allow_null=True)
    parish_name = serializers.CharField(source="person.parish.name", read_only=True, allow_null=True)
    city_id = serializers.IntegerField(source="person.parish.city_id", read_only=True, allow_null=True)
    city_name = serializers.CharField(source="person.parish.city.name", read_only=True, allow_null=True)
    document_type_id = serializers.IntegerField(source="person.document_type_id", read_only=True, allow_null=True)
    document_type_name = serializers.CharField(source="person.document_type.name", read_only=True, allow_null=True)
    role = serializers.SerializerMethodField(read_only=True)
    role_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "dni",
            "names",
            "last_names",
            "email",
            "birth_date",
            "phone",
            "parish_id",
            "parish_name",
            "city_id",
            "city_name",
            "document_type_id",
            "document_type_name",
            "role",
            "role_id",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_role(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        return first_role.role.code if first_role else None

    def get_role_id(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        return first_role.role.id if first_role else None


class UserDetailSerializer(serializers.ModelSerializer):
    dni = serializers.CharField(source="person.document_number", read_only=True)
    names = serializers.CharField(source="person.names", read_only=True)
    last_names = serializers.CharField(source="person.last_names", read_only=True)
    email = serializers.CharField(source="person.email", read_only=True)
    birth_date = serializers.DateField(source="person.birth_date", read_only=True, allow_null=True)
    phone = serializers.CharField(source="person.phone", read_only=True)
    parish_id = serializers.IntegerField(source="person.parish_id", read_only=True, allow_null=True)
    parish_name = serializers.CharField(source="person.parish.name", read_only=True, allow_null=True)
    city_id = serializers.IntegerField(source="person.parish.city_id", read_only=True, allow_null=True)
    city_name = serializers.CharField(source="person.parish.city.name", read_only=True, allow_null=True)
    document_type_id = serializers.IntegerField(source="person.document_type_id", read_only=True, allow_null=True)
    document_type_name = serializers.CharField(source="person.document_type.name", read_only=True, allow_null=True)
    role = serializers.SerializerMethodField(read_only=True)
    role_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "dni",
            "names",
            "last_names",
            "email",
            "birth_date",
            "phone",
            "parish_id",
            "parish_name",
            "city_id",
            "city_name",
            "document_type_id",
            "document_type_name",
            "role",
            "role_id",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "username", "created_at", "updated_at"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_role(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        return first_role.role.code if first_role else None

    def get_role_id(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        return first_role.role.id if first_role else None

    def to_internal_value(self, data):
        from apps.people.models import DocumentType, Parish

        values = super().to_internal_value(data)
        person_fields = {
            "document_number": serializers.CharField(max_length=20),
            "names": serializers.CharField(max_length=100),
            "last_names": serializers.CharField(max_length=100),
            "email": serializers.EmailField(),
            "birth_date": serializers.DateField(allow_null=True),
            "phone": serializers.CharField(max_length=15, allow_blank=True),
            "document_type": serializers.IntegerField(allow_null=True),
            "parish": serializers.IntegerField(allow_null=True),
        }
        for field_name, field in person_fields.items():
            if field_name in data:
                values[field_name] = field.run_validation(data.get(field_name))
        if "email" in values:
            values["email"] = self.validate_email(values["email"])
        if "document_number" in values:
            values["document_number"] = self.validate_document_number(
                values["document_number"]
            )
        if (
            "document_type" in values
            and values["document_type"] is not None
            and not DocumentType.objects.filter(pk=values["document_type"]).exists()
        ):
            raise serializers.ValidationError(
                {"document_type": "El tipo de documento seleccionado no existe"}
            )
        if (
            "parish" in values
            and values["parish"] is not None
            and not Parish.objects.filter(pk=values["parish"]).exists()
        ):
            raise serializers.ValidationError(
                {"parish": "La parroquia seleccionada no existe"}
            )
        if "role_id" in data:
            role_id = serializers.IntegerField().run_validation(
                data.get("role_id")
            )
            if not Role.objects.filter(pk=role_id).exists():
                raise serializers.ValidationError(
                    {"role_id": f"El rol con ID {role_id} no existe"}
                )
            values["role_id"] = role_id
        return values

    def update(self, instance, validated_data):
        from apps.people.models import DocumentType, Parish

        role_id = validated_data.pop("role_id", None)
        person_data = {
            key: validated_data.pop(key)
            for key in [
                "document_number",
                "names",
                "last_names",
                "email",
                "birth_date",
                "phone",
                "document_type",
                "parish",
            ]
            if key in validated_data
        }
        instance = super().update(instance, validated_data)

        if role_id is not None:
            role = Role.objects.get(pk=role_id)
            UserRole.objects.filter(user=instance).delete()
            UserRole.objects.create(user=instance, role=role)

        if person_data and instance.person:
            if "document_type" in person_data:
                document_type = person_data.pop("document_type")
                instance.person.document_type = (
                    DocumentType.objects.get(pk=document_type)
                    if document_type is not None
                    else None
                )
            if "parish" in person_data:
                parish = person_data.pop("parish")
                instance.person.parish = (
                    Parish.objects.get(pk=parish) if parish is not None else None
                )
            for key, value in person_data.items():
                setattr(instance.person, key, value)
            instance.person.save()

        return instance

    def validate_email(self, value):
        from apps.people.models import Person

        instance = self.instance
        qs = Person.objects.filter(email=value)
        if instance and instance.person_id:
            qs = qs.exclude(id=instance.person_id)
        if qs.exists():
            raise serializers.ValidationError("Este email ya esta registrado.")
        return value

    def validate_document_number(self, value):
        from apps.people.models import Person

        instance = self.instance
        qs = Person.objects.filter(document_number=value)
        if instance and instance.person_id:
            qs = qs.exclude(id=instance.person_id)
        if qs.exists():
            raise serializers.ValidationError("Este documento ya esta registrado.")
        return value


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    document_number = serializers.CharField(max_length=20)
    names = serializers.CharField(max_length=100)
    last_names = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.IntegerField()
    birth_date = serializers.DateField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    document_type = serializers.IntegerField(required=False, allow_null=True)
    parish = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        from apps.people.models import Person

        if Person.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya esta registrado.")
        return value

    def validate_document_number(self, value):
        from apps.people.models import Person

        if Person.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("Este documento ya esta registrado.")
        return value
