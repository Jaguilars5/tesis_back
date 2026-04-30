from django.urls import path, include

urlpatterns = [
    path("api/", include("apps.analytics.api.urls")),
]
