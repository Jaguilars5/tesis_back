from django.apps import AppConfig


class EarlyAlertConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics.early_alert"
    label = "early_alert"
    verbose_name = "Alertas Tempranas"
