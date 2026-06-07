from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, person, password=None, **extra_fields):
        if not person:
            raise ValueError("Person es obligatorio")
        email = self.normalize_email(person.email) if person.email else ""
        user = self.model(
            person=person, email=email, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **fields):
        email = fields.get("email")
        if not email:
            raise ValueError("Email es obligatorio")
        extra_fields = {k: v for k, v in fields.items() if k not in ["email"]}
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        if fields.get("password"):
            user.set_password(fields["password"])
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    person = models.OneToOneField(
        "Person",
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Persona",
    )
    email = models.EmailField(
        unique=True, verbose_name="Correo Electrónico",
        help_text="Sincronizado desde Person.email",
    )
    user_type = models.CharField(
        max_length=20,
        choices=[
            ("ESTUDIANTE", "Estudiante"),
            ("DOCENTE", "Docente"),
            ("ADMIN", "Administrador"),
            ("REPRESENTANTE", "Representante"),
        ],
        null=True,
        blank=True,
        verbose_name="Tipo de Usuario",
        help_text="Rol base del usuario en el sistema",
    )
    active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Personal del Admin")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "accounts"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["active"]),
        ]

    def __str__(self):
        if self.person:
            return f"{self.person.names} {self.person.last_names} ({self.email})"
        return f"User #{self.pk}"

    @property
    def is_active(self):
        return self.active and (self.person is None or self.person.active)

    def has_perm(self, permission_code):
        if self.is_superuser:
            return True
        return self.user_roles.filter(
            role__role_permissions__permission__code=permission_code
        ).exists()

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return False

    def get_all_permissions(self):
        return set(
            self.user_roles.values_list(
                "role__role_permissions__permission__code", flat=True
            ).distinct()
        )
