from django.db import models

from apps.core.models import TimeStampedModel


class ScoringEngineChoices(models.TextChoices):
    """Motor activo para el cálculo del riesgo académico."""

    RULES = "reglas", "Motor de reglas (ponderado + umbrales)"
    ML = "ML", "Modelo de Machine Learning"


class ScoringPresetChoices(models.TextChoices):
    """Presets cerrados como punto de partida seguro (Auditoría §9.4)."""

    CONSERVADOR = "conservador", "Conservador"
    EQUILIBRADO = "equilibrado", "Equilibrado"
    ESTRICTO = "estricto", "Estricto"
    PERSONALIZADO = "personalizado", "Personalizado"


class RiskScoringConfig(TimeStampedModel):
    """
    Configuración GLOBAL (singleton) del motor de riesgo académico.

    Externaliza lo que históricamente vivía hardcodeado en
    `apps/analytics/tasks.py` (`WEIGHTS` y los umbrales del semáforo). Permite a
    la institución ajustar **pesos + umbrales** con parámetros seguros
    (Auditoría §9). Es un *singleton*: existe a lo sumo una fila (pk fijo = 1).

    Los **pesos** se guardan como **porcentajes** (deben sumar 100) para que la
    suma y la UI de sliders sean naturales; el servicio los normaliza a
    fracciones (0–1) al construir la configuración efectiva que consume `tasks`.

    Con `engine = ML` los pesos/umbrales del motor de reglas se ignoran (el ML
    aprende sus propios pesos de los datos); se documenta y se conserva el
    fallback por reglas cuando no hay artefacto entrenado.
    """

    SINGLETON_PK = 1

    engine = models.CharField(
        max_length=10,
        choices=ScoringEngineChoices.choices,
        default=ScoringEngineChoices.RULES,
        verbose_name="Motor de cálculo",
    )
    preset = models.CharField(
        max_length=15,
        choices=ScoringPresetChoices.choices,
        default=ScoringPresetChoices.EQUILIBRADO,
        verbose_name="Preset aplicado",
    )

    # ─── Pesos de dimensión (porcentajes, deben sumar 100) ───
    weight_conducta = models.DecimalField(
        max_digits=5, decimal_places=2, default=30.00,
        verbose_name="Peso Conducta (%)",
    )
    weight_asistencia = models.DecimalField(
        max_digits=5, decimal_places=2, default=35.00,
        verbose_name="Peso Asistencia (%)",
    )
    weight_calificaciones = models.DecimalField(
        max_digits=5, decimal_places=2, default=35.00,
        verbose_name="Peso Calificaciones (%)",
    )

    # ─── Umbrales del semáforo de asistencia (0–100) ───
    # asistencia < attendance_red_max => rojo; <= attendance_yellow_max => amarillo
    attendance_red_max = models.DecimalField(
        max_digits=5, decimal_places=2, default=70.00,
        verbose_name="Asistencia máxima para Rojo (%)",
    )
    attendance_yellow_max = models.DecimalField(
        max_digits=5, decimal_places=2, default=85.00,
        verbose_name="Asistencia máxima para Amarillo (%)",
    )

    # ─── Umbrales del semáforo de promedio (0–10) ───
    # promedio < average_red_max => rojo; <= average_yellow_max => amarillo
    average_red_max = models.DecimalField(
        max_digits=4, decimal_places=2, default=6.00,
        verbose_name="Promedio máximo para Rojo",
    )
    average_yellow_max = models.DecimalField(
        max_digits=4, decimal_places=2, default=7.00,
        verbose_name="Promedio máximo para Amarillo",
    )

    # ─── Umbrales de conducta (conteos) ───
    # faltas_graves > severe_red_min => rojo; faltas_leves > mild_yellow_min => amarillo
    severe_red_min = models.IntegerField(
        default=3, verbose_name="Faltas graves para Rojo (>)",
    )
    mild_yellow_min = models.IntegerField(
        default=5, verbose_name="Faltas leves para Amarillo (>)",
    )

    class Meta:
        app_label = "analytics"
        verbose_name = "Configuración de Cálculo de Riesgo"
        verbose_name_plural = "Configuración de Cálculo de Riesgo"

    def __str__(self):
        return f"RiskScoringConfig(engine={self.engine}, preset={self.preset})"
