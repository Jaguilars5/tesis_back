from django.apps import AppConfig


class QualitativeScaleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.grading.qualitative_scale"
    label = "grading_qualitative_scale"
    verbose_name = "Escalas Cualitativas"

    def ready(self):
        import apps.grading.qualitative_scale.signals  # noqa: F401
