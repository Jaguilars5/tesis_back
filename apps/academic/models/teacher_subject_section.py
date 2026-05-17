from django.db import models


class Teacher_Subject_Section(models.Model):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, verbose_name="Docente"
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        verbose_name="Oferta de Materia",
    )
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        app_label = "academic"
        verbose_name = "Docente-Materia-Sección"
        verbose_name_plural = "Docentes-Materias-Secciones"

    def __str__(self):
        return f"{self.user} - {self.subject_offering}"
