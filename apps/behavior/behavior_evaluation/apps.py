from django.apps import AppConfig


class BehaviorEvaluationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.behavior.behavior_evaluation"
    label = "behavior_evaluation"
    verbose_name = "Evaluaciones de Conducta"

    def ready(self):
        import apps.behavior.behavior_evaluation.signals  # noqa: F401
