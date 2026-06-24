import re
import unicodedata

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, person, password=None, username=None, **extra_fields):
        if not person:
            raise ValueError("Person es obligatorio")
        extra_fields.pop("user_type", None)
        extra_fields.pop("email", None)
        must_change_password = extra_fields.pop("must_change_password", True)
        if not username:
            username = User.generate_username(person.names, person.last_names)
        user = self.model(person=person, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.must_change_password = must_change_password
        user.save(using=self._db)
        return user

    def create_superuser(self, **fields):
        from apps.people.models import Person

        email = fields.get("email")
        if not email:
            raise ValueError("Email es obligatorio")
        username = fields.get("username") or email.split("@")[0]
        extra_fields = {k: v for k, v in fields.items() if k not in ["email", "username"]}
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        email = self.normalize_email(email)
        person_data = {
            "email": email,
            "names": username,
            "last_names": "Superuser",
            "document_number": f"SUPER-{username}",
        }
        person, _ = Person.objects.get_or_create(
            document_number=person_data["document_number"], defaults=person_data,
        )
        user = self.model(person=person, username=username, **extra_fields)
        if fields.get("password"):
            user.set_password(fields["password"])
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, TimeStampedModel):
    person = models.OneToOneField(
        "people.Person",
        on_delete=models.CASCADE,
        null=False,
        verbose_name="Persona",
    )
    username = models.CharField(max_length=50, unique=True, verbose_name="Nombre de Usuario")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Personal del Admin")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")
    must_change_password = models.BooleanField(default=True, verbose_name="Debe cambiar contrase\u00f1a")

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        app_label = "iam"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["id"]
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        if self.person:
            return f"{self.person.names} {self.person.last_names} ({self.username})"
        return f"User #{self.pk}"

    @property
    def birth_date(self):
        return self.person.birth_date if self.person else None

    def get_full_name(self):
        if self.person:
            return f"{self.person.names} {self.person.last_names}"
        return self.username

    @staticmethod
    def _normalize(text):
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-z0-9]", "", text)
        return text

    @staticmethod
    def generate_username(names, last_names):
        if not names or not last_names:
            return None
        first_name = User._normalize(names.split()[0])
        first_last_name = User._normalize(last_names.split()[0])
        base_username = first_name[0] + first_last_name
        if not User.objects.filter(username=base_username).exists():
            return base_username
        existing = User.objects.filter(username__startswith=base_username).values_list("username", flat=True)
        max_num = 1
        for uname in existing:
            match = re.match(r"^" + re.escape(base_username) + r"(\d+)$", uname)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"{base_username}{max_num + 1:02d}"

    def has_perm(self, permission_code):
        if self.is_superuser:
            return True
        return self.user_roles.filter(
            role__role_permissions__permission__code=permission_code
        ).exists()

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_all_permissions(self):
        return set(
            self.user_roles.values_list(
                "role__role_permissions__permission__code", flat=True
            ).distinct()
        )

    @property
    def user_category(self):
        role = self.user_roles.select_related("role").first()
        if not role:
            return "SIN_ROL"
        code = role.role.code
        if code == "ESTUDIANTE":
            return "ESTUDIANTE"
        if code == "REPRESENTANTE":
            return "REPRESENTANTE"
        if code in ("DOCENTE", "DIRECTOR", "CONSEJERO", "RECTOR"):
            return "DOCENTE"
        if code == "ADMIN":
            return "ADMIN"
        return "OTRO"


class Role(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, null=True, verbose_name="C\u00f3digo del Rol")
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Rol")
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripci\u00f3n")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "iam"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["is_active"])]

    def __str__(self):
        return self.name

    def get_all_permissions(self):
        return Permission.objects.filter(permission_roles__role=self).distinct()


class Permission(TimeStampedModel):
    code = models.CharField(max_length=100, unique=True, verbose_name="C\u00f3digo del Permiso")
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripci\u00f3n")
    module = models.CharField(max_length=50, blank=True, verbose_name="M\u00f3dulo")

    class Meta:
        app_label = "iam"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["code"]
        indexes = [models.Index(fields=["code"]), models.Index(fields=["module"])]

    def __str__(self):
        return self.code


class UserRole(TimeStampedModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_roles", verbose_name="Usuario")
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="user_roles", verbose_name="Rol")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Asignado en")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira en")

    class Meta:
        app_label = "iam"
        verbose_name = "Rol del Usuario"
        verbose_name_plural = "Roles del Usuario"
        constraints = [models.UniqueConstraint(fields=["user", "role"], name="unique_user_role")]

    def __str__(self):
        return f"{self.user} \u2192 {self.role.name}"


class RolePermission(TimeStampedModel):
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="role_permissions", verbose_name="Rol")
    permission = models.ForeignKey("Permission", on_delete=models.CASCADE, related_name="permission_roles", verbose_name="Permiso")

    class Meta:
        app_label = "iam"
        verbose_name = "Permiso del Rol"
        verbose_name_plural = "Permisos del Rol"
        constraints = [models.UniqueConstraint(fields=["role", "permission"], name="unique_role_permission")]
        indexes = [models.Index(fields=["role"]), models.Index(fields=["permission"])]

    def __str__(self):
        return f"{self.role.name} \u2192 {self.permission.code}"
