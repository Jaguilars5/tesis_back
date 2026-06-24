from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response, error_response

from ..application.serializers import ClassScheduleSerializer
from ..domain.services import ClassScheduleService
from ..infrastructure.repositories import ClassScheduleRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import ClassScheduleFilter


@extend_schema_view(
    list=extend_schema(summary="Listar horarios", tags=["academic"]),
    get=extend_schema(summary="Obtener horario", tags=["academic"]),
    create=extend_schema(summary="Crear horario", tags=["academic"]),
    update=extend_schema(summary="Actualizar horario", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente horario", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar horario", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar horario", tags=["academic"]),
    by_section=extend_schema(summary="Horarios por sección", tags=["academic"]),
    my_schedule=extend_schema(summary="Mi horario", tags=["academic"]),
    my_today=extend_schema(summary="Mis clases hoy", tags=["academic"]),
)
class ClassScheduleViewSet(BaseAcademicViewSet):
    serializer_class = ClassScheduleSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = ClassScheduleFilter
    search_fields = [
        "teacher_subject_section__subject_offering__section__parallel",
        "teacher_subject_section__subject_offering__subject_academic_config__subject__name",
        "teacher_subject_section__user__person__names",
        "teacher_subject_section__user__person__last_names",
    ]
    ordering_fields = ["day_of_week", "start_time"]
    ordering = ["day_of_week", "start_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ClassScheduleRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = ClassScheduleService.create_schedule(
            teacher_subject_section_id=data["teacher_subject_section"].id,
            day_of_week=data["day_of_week"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = ClassScheduleService.update_schedule(
            schedule_id=serializer.instance.id,
            **data,
        )
        serializer.instance = instance

    @action(detail=False, methods=["get"], url_path="by-section")
    def by_section(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return error_response(
                "section_id es requerido", status_code=status.HTTP_400_BAD_REQUEST
            )
        qs = ClassScheduleService.get_by_section(section_id)
        serializer = self.get_serializer(qs, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-schedule")
    def my_schedule(self, request):
        user = request.user
        if user.user_category == "ESTUDIANTE":
            student = getattr(user, "student", None)
            if not student:
                return error_response(
                    "Perfil de estudiante no encontrado",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            qs = ClassScheduleService.get_by_student(student.id)
        else:
            qs = ClassScheduleService.get_by_teacher(user.id)
        serializer = self.get_serializer(qs, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-today")
    def my_today(self, request):
        user = request.user
        qs = ClassScheduleService.get_today_for_teacher(user.id)
        serializer = self.get_serializer(qs, many=True)
        return ok_response(serializer.data)
