from .routers import PeopleRouter
from .views import CityViewSet, DocumentTypeViewSet, ParishViewSet, PersonViewSet

router = PeopleRouter()
router.register(r"cities", CityViewSet, basename="city")
router.register(r"parishes", ParishViewSet, basename="parish")
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")
router.register(r"persons", PersonViewSet, basename="person")

urlpatterns = router.urls
