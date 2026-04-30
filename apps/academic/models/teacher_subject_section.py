from django.db import models


class Teacher_Subject_Section(models.Model):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, verbose_name="Docente"
    )
    subject = models.ForeignKey(
        "academic.Subject", on_delete=models.CASCADE, verbose_name="Materia"
    )
    section = models.ForeignKey(
        "academic.Section", on_delete=models.CASCADE, verbose_name="Sección"
    )
    school_year = models.ForeignKey(
        "institutions.School_Year", on_delete=models.CASCADE, verbose_name="Año Escolar"
    )
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Docente-Materia-Sección"
        verbose_name_plural = "Docentes-Materias-Secciones"
        unique_together = ("user", "subject", "section", "school_year")

    def __str__(self):
        return f"{self.user.names} - {self.subject.name} - {self.section}"
