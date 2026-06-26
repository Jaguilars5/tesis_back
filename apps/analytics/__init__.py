# Paquete Analytics para análisis de riesgo estudiantil.
#
# Cada bounded context es una sub-app instalable (mismo patrón que apps.academic),
# con sus propias capas domain/infrastructure/application/api.

ANALYTICS_APPS = [
    "apps.analytics.student_risk",
    "apps.analytics.early_alert",
    "apps.analytics.dashboard",
]
