from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CityViewSet, DocumentTypeViewSet, PersonViewSet

router = DefaultRouter()
router.register(r"cities", CityViewSet, basename="city")
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")
router.register(r"persons", PersonViewSet, basename="person")

urlpatterns = [
    path("", include(router.urls)),
]
