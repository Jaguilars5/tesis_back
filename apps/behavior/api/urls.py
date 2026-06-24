from django.urls import path, include

urlpatterns = [
    path("", include("apps.behavior.incident_type.urls")),
    path("", include("apps.behavior.severity.urls")),
    path("", include("apps.behavior.conduct_incident.urls")),
    path("", include("apps.behavior.behavior_evaluation.urls")),
]
