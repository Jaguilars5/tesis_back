from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.models import Notification
from apps.core.repositories.notification_repo import NotificationRepository
from apps.core.utils.responses import ok_response

from .serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(summary="Listar mis notificaciones", tags=["notifications"]),
)
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Centro de notificaciones del usuario autenticado.

    Cada usuario solo puede ver y modificar sus propias notificaciones, por lo
    que se omite el ``RoleBasedFilterBackend`` (filtrado por ``recipient`` en
    ``get_queryset``) y basta con ``IsAuthenticated``.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = []
    queryset = Notification.objects.none()

    def get_queryset(self):
        return NotificationRepository.list_for_user(self.request.user)

    @extend_schema(summary="Conteo de no leídas", tags=["notifications"])
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        return ok_response({"unread": NotificationRepository.unread_count(request.user)})

    @extend_schema(summary="Marcar notificación como leída", tags=["notifications"])
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = NotificationRepository.mark_read(pk, request.user)
        if not notification:
            return ok_response(
                None,
                msg="Notificación no encontrada",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return ok_response(
            NotificationSerializer(notification).data,
            msg="Notificación marcada como leída",
        )

    @extend_schema(summary="Marcar todas como leídas", tags=["notifications"])
    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = NotificationRepository.mark_all_read(request.user)
        return ok_response({"updated": updated}, msg="Notificaciones marcadas como leídas")
