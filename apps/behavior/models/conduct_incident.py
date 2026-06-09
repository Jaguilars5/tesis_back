import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class ConductIncident(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
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
    severity = models.IntegerField(verbose_name="Gravedad")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    actions_taken = models.TextField(null=True, blank=True, verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado el")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "behavior"
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"

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
