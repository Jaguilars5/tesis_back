"""
URLs para el módulo de alertas tempranas.

Registra EarlyAlertViewSet con AnalyticsRouter.
"""

from apps.analytics.api.routers import AnalyticsRouter

from .api.views import EarlyAlertViewSet

router = AnalyticsRouter()
router.register(r"early-alerts", EarlyAlertViewSet, basename="early-alert")

urlpatterns = router.urls
