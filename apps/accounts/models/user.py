from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager personalizado para el modelo User.
    """

    def create_user(self, email, dni, names, last_names, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(
            email=email, dni=dni, names=names, last_names=last_names, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, dni, names, last_names, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(email, dni, names, last_names, password, **extra_fields)
        return user


class User(AbstractBaseUser):
    """
    Usuario del sistema (Compatible con Django Auth).

    dni: Documento de identidad único
    names: Nombres
    last_names: Apellidos
    email: Correo electrónico único (USERNAME_FIELD)
    password: Heredado de AbstractBaseUser (Hash bcrypt)
    role: Rol asignado (Docente, Admin, Director, etc)
    institution: Institución a la que pertenece
    active: Indica si el usuario puede acceder al sistema
    """

    dni = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Documento de Identidad",
        help_text="Cédula, pasaporte u otro documento único",
    )
    names = models.CharField(
        max_length=100,
        verbose_name="Nombres",
        help_text="Nombres completos del usuario",
    )
    last_names = models.CharField(
        max_length=100, verbose_name="Apellidos", help_text="Apellidos del usuario"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Correo Electrónico",
        help_text="Dirección de correo única",
    )

    role = models.ForeignKey(
        "Role",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="Rol",
        help_text="Rol asignado al usuario (Docente, Administrador, Director, etc)",
    )
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="Institución",
        help_text="Institución a la que pertenece el usuario",
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el usuario puede acceder al sistema",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Es Personal del Admin",
        help_text="Permite acceso al panel de administración",
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Es Superusuario",
        help_text="Acceso total al sistema",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["dni", "names", "last_names"]

    class Meta:
        app_label = "accounts"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["email"]
        indexes = [
            models.Index(fields=["dni"]),
            models.Index(fields=["email"]),
            models.Index(fields=["active"]),
            models.Index(fields=["institution"]),
        ]
        unique_together = [("dni", "institution")]

    def __str__(self):
        return f"{self.names} {self.last_names} ({self.email})"

    # El método is_active es requerido por algunos componentes de Django
    @property
    def is_active(self):
        return self.active

    def has_perm(self, permission_codename):
        """
        Verifica si el usuario tiene un permiso específico.
        """
        if self.is_superuser:
            return True

        from .permission import Permission
        from .user_permission import UserPermission

        try:
            permission = Permission.objects.get(codename=permission_codename)
        except Permission.DoesNotExist:
            return False

        # Verificar override en UserPermission
        try:
            up = UserPermission.objects.get(user=self, permission=permission)
            return up.granted
        except UserPermission.DoesNotExist:
            # Hereda del role
            if self.role:
                return self.role.get_all_permissions().filter(id=permission.id).exists()
            return False

    def has_module_perms(self, app_label):
        """
        Retorna True si el usuario tiene algún permiso en el módulo.
        """
        if self.is_superuser:
            return True
        return False

    def get_all_permissions(self):
        """
        Retorna un set con todos los codenames de permisos del usuario (Rol + Overrides - Revocados).
        """
        from .user_permission import UserPermission

        # 1. Obtener permisos base del rol
        if self.role:
            role_perms = set(
                self.role.get_all_permissions().values_list("codename", flat=True)
            )
        else:
            role_perms = set()

        # 2. Obtener overrides del usuario
        user_overrides = UserPermission.objects.filter(user=self).values_list(
            "permission__codename", "granted"
        )

        user_granted = {codename for codename, granted in user_overrides if granted}
        user_revoked = {codename for codename, granted in user_overrides if not granted}

        # 3. Calcular resultado final: (Rol + Otorgados) - Revocados
        return (role_perms | user_granted) - user_revoked
