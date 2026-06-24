from django.apps import AppConfig


class EvaluationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.grading.evaluation"
    label = "grading_evaluation"
    verbose_name = "Evaluaciones"

    def ready(self):
        import apps.grading.evaluation.signals  # noqa: F401
