"""
Serializers de DRF para el módulo accounts.

Validan el formato de entrada HTTP y controlan qué campos se exponen en la respuesta.
"""

from rest_framework import serializers
from apps.accounts.models import User, Role, Permission, RolePermission, UserPermission


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer para Permission."""

    class Meta:
        model = Permission
        fields = ["id", "codename", "description", "module", "created_at", "updated_at"]
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


class UserPermissionSerializer(serializers.ModelSerializer):
    """Serializer para UserPermission (excepciones de usuario)."""

    permission = PermissionSerializer(read_only=True)
    granted_by_email = serializers.SerializerMethodField()

    class Meta:
        model = UserPermission
        fields = [
            "id",
            "user",
            "permission",
            "granted",
            "reason",
            "expires_at",
            "granted_by",
            "granted_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_granted_by_email(self, obj):
        if obj.granted_by:
            return obj.granted_by.email
        return None


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para User en listados."""

    role_name = serializers.CharField(source="role.name", read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "dni",
            "names",
            "last_names",
            "email",
            "role",
            "role_name",
            "institution",
            "institution_name",
            "active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para User con sus permisos."""

    role = RoleDetailSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)
    institution = serializers.StringRelatedField(read_only=True)
    institution_id = serializers.IntegerField(write_only=True, required=False)
    user_permissions_set = UserPermissionSerializer(many=True, read_only=True)

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
            "institution",
            "institution_id",
            "active",
            "user_permissions_set",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "password": {"write_only": True}  # Nunca exponemos el hash
        }

    def validate_email(self, value):
        """Valida que el email sea único."""
        instance = self.instance
        if (
            User.objects.filter(email=value)
            .exclude(id=instance.id if instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Este email ya está registrado.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios (incluye password)."""

    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.IntegerField()
    institution_id = serializers.IntegerField()

    class Meta:
        model = User
        fields = [
            "dni",
            "names",
            "last_names",
            "email",
            "password",
            "role_id",
            "institution_id",
        ]

    def validate_email(self, value):
        """Valida que el email sea único."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_dni(self, value):
        """Valida que el DNI sea único."""
        if User.objects.filter(dni=value).exists():
            raise serializers.ValidationError("Este DNI ya está registrado.")
        return value

    def create(self, validated_data):
        """Crea el usuario y hashea la contraseña."""
        password = validated_data.pop("password")
        role_id = validated_data.pop("role_id")
        institution_id = validated_data.pop("institution_id")

        # Obtener relaciones
        from apps.accounts.models import Role
        from apps.institutions.models import Institution

        role = Role.objects.get(id=role_id)
        institution = Institution.objects.get(id=institution_id)

        user = User(**validated_data, role=role, institution=institution)
        user.set_password(password)
        user.save()
        return user
