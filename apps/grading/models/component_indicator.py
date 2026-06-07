from django.db import models


class ComponentIndicator(models.Model):
    """
    INDICADOR_COMPONENTE — Indicadores de logro dentro de cada componente.
    Alineados al currículo nacional; baja frecuencia de cambio.
    """

    block_component = models.ForeignKey(
        "grading.BlockComponent",
        on_delete=models.CASCADE,
        related_name="indicators",
        verbose_name="Componente de Bloque",
    )
    name = models.CharField(max_length=200, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Ponderación Interna (%)",
        help_text="Peso del indicador dentro de su componente",
    )

    class Meta:
        app_label = "grading"
        verbose_name = "Indicador de Componente"
        verbose_name_plural = "Indicadores de Componente"
        ordering = ["block_component", "name"]

    def __str__(self):
        return f"{self.block_component.name} — {self.name}"
