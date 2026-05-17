from django.db import models


class Config_Academic(models.Model):
    """Legacy stub — migrado a estructura School_Year → AcademicPeriod."""
    school_year = models.ForeignKey("institutions.School_Year", on_delete=models.CASCADE, null=True)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=80, blank=True, default="")
    academic_period_type = models.CharField(max_length=20, blank=True, default="")
    number_of_periods = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "academic"
        managed = False
        db_table = "academic_config_academic"

    def __str__(self):
        return self.name
