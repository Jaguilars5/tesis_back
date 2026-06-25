from django.apps import AppConfig


class SubjectOfferingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic.subject_offering"
    label = "academic_subject_offering"
    verbose_name = "Ofertas de Materia"
