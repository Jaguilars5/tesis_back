from django.urls import path, include

urlpatterns = [
    path("", include("apps.analytics.api.urls")),
]
