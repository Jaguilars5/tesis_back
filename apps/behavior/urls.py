from django.urls import include, path

urlpatterns = [
    path("", include("apps.behavior.api.urls")),
]
