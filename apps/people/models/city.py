from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class City(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Ciudad")
    code = models.CharField(
        max_length=10, unique=True, verbose_name="Código de la Ciudad"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_city"
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ["name"]

    def __str__(self):
        return self.name
