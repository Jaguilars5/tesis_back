"""
Serializers de DRF para el módulo accounts.

Validan el formato de entrada HTTP y controlan qué campos se exponen en la respuesta.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from apps.accounts.models import (
    Person,
    User,
    Role,
    Permission,
    RolePermission,
)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Serializer personalizado para refresh que incluye datos del usuario."""

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
                data["user"] = {
                    "id": user.id,
                    "dni": person.document_number if person else "",
                    "names": person.names if person else "",
                    "last_names": person.last_names if person else "",
                    "email": user.email,
                    "role": first_role.role.name if first_role else None,
                    "role_id": first_role.role.id if first_role else None,
                    "active": user.active,
                    "permissions": list(user.get_all_permissions()),
                }
            except User.DoesNotExist:
                pass
        return data


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para login que incluye datos del usuario."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        person = user.person
        print("User", user, "Person", person)
        first_role = user.user_roles.select_related("role").first()
        data["user"] = {
            "id": user.id,
            "dni": person.document_number if person else "",
            "names": person.names if person else "",
            "last_names": person.last_names if person else "",
            "email": user.email,
            "role": first_role.role.name if first_role else None,
            "role_id": first_role.role.id if first_role else None,
            "active": user.active,
            "permissions": list(user.get_all_permissions()),
        }
        return data


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer para Permission."""

    class Meta:
        model = Permission
        fields = ["id", "code", "description", "module", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer para RolePermission (relación Role ↔ Permission)."""

    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = ["id", "role", "permission", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoleListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para Role en listados."""

    class Meta:
        model = Role
        fields = ["id", "name", "description", "active", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoleDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para Role con sus permisos."""

    role_permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "description",
            "active",
            "role_permissions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para User en listados."""

    dni = serializers.CharField(source="person.document_number", read_only=True)
    names = serializers.CharField(source="person.names", read_only=True)
    last_names = serializers.CharField(source="person.last_names", read_only=True)
    role_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "dni",
            "names",
            "last_names",
            "email",
            "role_name",
            "active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_role_name(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        return first_role.role.name if first_role else None


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para User con sus permisos."""

    dni = serializers.CharField(source="person.document_number", read_only=True)
    names = serializers.CharField(source="person.names", read_only=True)
    last_names = serializers.CharField(source="person.last_names", read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "dni",
            "names",
            "last_names",
            "email",
            "role",
            "role_id",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_role(self, obj):
        first_role = obj.user_roles.select_related("role").first()
        if first_role:
            return RoleDetailSerializer(first_role.role, context=self.context).data
        return None

    def validate_email(self, value):
        instance = self.instance
        if (
            User.objects.filter(email=value)
            .exclude(id=instance.id if instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Este email ya está registrado.")
        return value


class UserCreateSerializer(serializers.Serializer):
    """Serializer para crear usuarios (incluye password)."""

    document_number = serializers.CharField(max_length=20)
    names = serializers.CharField(max_length=100)
    last_names = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.IntegerField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_document_number(self, value):
        from apps.accounts.models import Person

        if Person.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("Este documento ya está registrado.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        role_id = validated_data.pop("role_id")
        document_number = validated_data.pop("document_number")
        names = validated_data.pop("names")
        last_names = validated_data.pop("last_names")

        from apps.accounts.models import Person, Role
        from apps.institutions.models import DocumentType

        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula de Ciudadanía"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number=document_number,
            names=names,
            last_names=last_names,
            email=validated_data.get("email", ""),
        )

        user = User.objects.create_user(
            person=person,
            email=validated_data["email"],
            password=password,
        )
        if role_id:
            from apps.accounts.models import UserRole

            role = Role.objects.get(id=role_id)
            UserRole.objects.create(user=user, role=role)
        return user
