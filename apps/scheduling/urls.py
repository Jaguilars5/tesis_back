from django.urls import path, include

urlpatterns = [
    path('', include('apps.scheduling.api.urls')),
]
