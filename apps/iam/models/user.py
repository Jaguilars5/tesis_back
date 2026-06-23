import re
import unicodedata

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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
        extra_fields = {
            k: v for k, v in fields.items() if k not in ["email", "username"]
        }
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
            document_number=person_data["document_number"],
            defaults=person_data,
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
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre de Usuario",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Personal del Admin")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")
    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Debe cambiar contraseña",
        help_text="Indica si el usuario debe cambiar su contraseña en el próximo inicio de sesión",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        app_label = "iam"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

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
        text = (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
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
        existing = User.objects.filter(username__startswith=base_username).values_list(
            "username", flat=True
        )
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
        if self.is_superuser:
            return True
        return False

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
        if code in ("ESTUDIANTE",):
            return "ESTUDIANTE"
        if code in ("REPRESENTANTE",):
            return "REPRESENTANTE"
        if code in ("DOCENTE", "DIRECTOR", "CONSEJERO", "RECTOR"):
            return "DOCENTE"
        if code in ("ADMIN",):
            return "ADMIN"
        return "OTRO"
