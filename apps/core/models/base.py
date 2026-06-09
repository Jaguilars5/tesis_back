from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Actualización")

    class Meta:
        abstract = True
