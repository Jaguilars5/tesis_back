from django.db import models


class Academic_Activity(models.Model):
    config_academic = models.ForeignKey(
        "academic.Config_Academic",
        on_delete=models.CASCADE,
        verbose_name="Configuración Académica",
    )
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Materia",
    )
    name = models.CharField(max_length=80, verbose_name="Nombre de la Actividad")
    value_max = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Valor Máximo"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Peso/Porcentaje"
    )
    applies_to = models.CharField(max_length=20, verbose_name="Aplica a")
    is_recoverable = models.BooleanField(default=False, verbose_name="Es Recuperable")
    order = models.IntegerField(verbose_name="Orden")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Actividad Académica"
        verbose_name_plural = "Actividades Académicas"

    def __str__(self):
        return f"{self.config_academic.institution.name} - {self.name}"
