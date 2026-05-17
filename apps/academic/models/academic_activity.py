from django.db import models


class Academic_Activity(models.Model):
    """Legacy stub — reemplazado por jerarquía EvaluationMacro → ClassAssignment."""
    config_academic = models.ForeignKey("academic.Config_Academic", on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey("academic.Subject", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=80, blank=True, default="")
    value_max = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    applies_to = models.CharField(max_length=20, blank=True, default="")
    is_recoverable = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "academic"
        managed = False
        db_table = "academic_academic_activity"

    def __str__(self):
        return self.name
