from django.urls import path, include

urlpatterns = [
    path('api/', include('apps.scheduling.api.urls')),
]
