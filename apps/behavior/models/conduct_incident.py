from django.db import models
from apps.core.models import TimeStampedModel
from apps.integration.models.syncable_mixin import SyncableModel


class ConductIncident(TimeStampedModel, SyncableModel):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Matrícula",
        null=True,
    )
    reported_by_user = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        related_name="reported_conduct_incidents",
        null=True,
        verbose_name="Reportado por",
    )
    academic_period = models.ForeignKey(
        "academic.AcademicPeriod",
        on_delete=models.CASCADE,
        related_name="conduct_incidents",
        verbose_name="Período Académico",
    )
    incident_type = models.ForeignKey(
        "behavior.IncidentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de incidente",
        null=True,
    )
    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    severity = models.ForeignKey(
        "behavior.Severity",
        on_delete=models.PROTECT,
        verbose_name="Severidad",
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    actions_taken = models.TextField(null=True, blank=True, verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    created_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="incidents_created", verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="incidents_modified", verbose_name="Modificado por",
    )
    approved_by = models.ForeignKey(
        "iam.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="incidents_approved", verbose_name="Aprobado por",
    )

    class Meta:
        app_label = "behavior"
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"
        ordering = ["-incident_date"]
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["academic_period", "severity"]),
            models.Index(fields=["incident_date"]),
        ]

    def __init__(self, *args, **kwargs):
        category = kwargs.pop("category", None)
        super().__init__(*args, **kwargs)
        if category:
            from apps.behavior.models import IncidentType
            incident_type, _ = IncidentType.objects.get_or_create(
                code=category,
                defaults={"name": category.capitalize(), "description": f"Tipo de incidente: {category}"}
            )
            self.incident_type = incident_type

    @property
    def category(self):
        return self.incident_type.code if self.incident_type else ""

    @category.setter
    def category(self, value):
        if value:
            from apps.behavior.models import IncidentType
            incident_type, _ = IncidentType.objects.get_or_create(
                code=value,
                defaults={"name": value.capitalize(), "description": f"Tipo de incidente: {value}"}
            )
            self.incident_type = incident_type
        else:
            self.incident_type = None

    def __str__(self):
        category_str = self.category if self.category else (str(self.incident_type) if self.incident_type else "")
        return f"{self.enrollment} - {category_str} ({self.incident_date})"
