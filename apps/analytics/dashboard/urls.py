"""
URLs para el módulo de dashboard.

Registra DashboardViewSet.
"""

from apps.analytics.api.routers import AnalyticsRouter

from .api.views import DashboardViewSet

router = AnalyticsRouter()
router.register(r"dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls
