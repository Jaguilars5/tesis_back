from django.urls import include, path

urlpatterns = [
    path("", include("apps.integration.api.urls")),
]
