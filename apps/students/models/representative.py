from django.db import models


class Representative(models.Model):
    """Legacy stub — modelo será eliminado tras migración completa."""
    names = models.CharField(max_length=100, blank=True, default="")
    last_names = models.CharField(max_length=100, blank=True, default="")
    dni = models.CharField(max_length=13, unique=True, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, default="")
    address = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "students"
        managed = False
        db_table = "students_representative"

    def __str__(self):
        return f"{self.names} {self.last_names}"

    def get_full_name(self):
        return f"{self.names} {self.last_names}"
