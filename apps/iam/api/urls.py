from django.urls import path, include
from .routers import IamRouter
from .views import PermissionViewSet, RoleViewSet, UserViewSet, CustomTokenObtainPairView, CustomTokenRefreshView

router = IamRouter()
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
