from django.urls import include, path

urlpatterns = [
    path("", include("apps.iam.api.urls")),
]
