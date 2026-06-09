from django.db import models
from apps.core.models import TimeStampedModel


class DocumentType(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "people"
        db_table = "people_document_type"
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        ordering = ["name"]

    def __str__(self):
        return self.name
