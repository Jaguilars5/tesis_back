from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from apps.core.models import TimeStampedModel


class BlockComponent(TimeStampedModel):
    """
    COMPONENTE_BLOQUE — Componentes dentro de un bloque de evaluación.
    Configuración pedagógica del docente; baja frecuencia de cambio.
    """

    code = models.CharField(max_length=50, blank=True, db_index=True, verbose_name="Código")
    evaluation_block = models.ForeignKey(
        "grading.EvaluationBlock",
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Bloque de Evaluación",
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    internal_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Ponderación Interna (%)",
        help_text="Peso del componente dentro del bloque de evaluación",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "grading"
        verbose_name = "Componente de Bloque"
        verbose_name_plural = "Componentes de Bloque"
        ordering = ["evaluation_block", "name"]

    def clean(self):
        super().clean()
        if self.internal_weight and self.evaluation_block_id:
            total = BlockComponent.objects.filter(
                evaluation_block=self.evaluation_block,
                is_active=True,
            ).exclude(pk=self.pk).aggregate(total=Sum("internal_weight"))["total"] or 0
            if total + self.internal_weight > 100:
                raise ValidationError(
                    {"internal_weight": f"La suma de pesos internos excede 100%. Actualmente: {total}%, intentando agregar: {self.internal_weight}%"}
                )

    def __str__(self):
        return f"{self.evaluation_block.name} — {self.name}"