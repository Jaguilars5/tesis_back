from django.urls import include, path

urlpatterns = [
    path("", include("apps.people.api.urls")),
]
