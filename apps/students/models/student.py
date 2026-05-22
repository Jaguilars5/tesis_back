from django.db import models


class Student(models.Model):
    person = models.OneToOneField(
        "accounts.Person",
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Persona",
    )
    student_code = models.CharField(
        max_length=50, unique=True, verbose_name="Código de Estudiante"
    )
    residential_zone = models.CharField(
        max_length=50, blank=True, verbose_name="Zona Residencial"
    )
    distance_to_school_km = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Distancia al Colegio (km)",
    )
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        app_label = "students"
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["student_code"]),
        ]

    def __str__(self):
        if self.person:
            return self.person.get_full_name()
        return f"Student #{self.pk}"

    def get_full_name(self):
        if self.person:
            return self.person.get_full_name()
        return ""

    def get_age(self):
        from datetime import date
        if self.person and self.person.birth_date:
            today = date.today()
            return today.year - self.person.birth_date.year - (
                (today.month, today.day) < (self.person.birth_date.month, self.person.birth_date.day)
            )
        return 0
