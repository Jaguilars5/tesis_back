from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import academic
from apps.core.utils import ok_response, error_response

from ..repositories import (
    SubjectRepository,
    AcademicPeriodRepository,
    PeriodTypeRepository,
    TeacherSubjectSectionRepository,
    SubjectAcademicConfigRepository,
    SubjectOfferingRepository,
    ClassScheduleRepository,
)
from ..services.academic_service import AcademicService
from .filters import TeacherSubjectSectionFilter
from .serializers import (
    AcademicPeriodSerializer,
    ClassScheduleSerializer,
    PeriodTypeSerializer,
    SubjectAcademicConfigSerializer,
    SubjectOfferingSerializer,
    SubjectSerializer,
    TeacherSubjectSectionSerializer,
)


class BaseAcademicViewSet(viewsets.ModelViewSet):
    """ViewSet base para modelos académicos con soporte de StandardResponse"""

    permission_classes = [IsAuthenticated, HasPermission]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save()
            return ok_response({"id": instance.id, "is_active": False})
        return error_response("Este modelo no soporta borrado lógico")


@extend_schema_view(
    list=extend_schema(summary="Listar asignaturas", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener asignatura", tags=["academic"]),
    create=extend_schema(summary="Crear asignatura", tags=["academic"]),
    update=extend_schema(summary="Actualizar asignatura", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar asignatura parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar asignatura", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar asignatura", tags=["academic"]),
)
class SubjectViewSet(BaseAcademicViewSet):
    serializer_class = SubjectSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT,
        "retrieve": academic.VIEW_SUBJECT,
        "create": academic.CREATE_SUBJECT,
        "update": academic.UPDATE_SUBJECT,
        "partial_update": academic.UPDATE_SUBJECT,
        "destroy": academic.DELETE_SUBJECT,
        "soft_delete": academic.DELETE_SUBJECT,
    }
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar periodos académicos", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener periodo académico", tags=["academic"]),
    create=extend_schema(summary="Crear periodo académico", tags=["academic"]),
    update=extend_schema(summary="Actualizar periodo académico", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar periodo académico parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar periodo académico", tags=["academic"]),
    soft_delete=extend_schema(
        summary="Desactivar periodo académico", tags=["academic"]
    ),
)
class AcademicPeriodViewSet(BaseAcademicViewSet):
    serializer_class = AcademicPeriodSerializer
    action_permissions = {
        "list": academic.VIEW_PERIOD,
        "retrieve": academic.VIEW_PERIOD,
        "create": academic.CREATE_PERIOD,
        "update": academic.UPDATE_PERIOD,
        "partial_update": academic.UPDATE_PERIOD,
        "destroy": academic.DELETE_PERIOD,
        "soft_delete": academic.DELETE_PERIOD,
    }
    ordering_fields = ["name", "start_date", "end_date"]
    ordering = ["-start_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicPeriodRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            period = AcademicService.create_academic_period(
                name=data["name"],
                school_year_id=data["school_year"].id
                if hasattr(data["school_year"], "id")
                else data["school_year"],
                period_type=data.get("period_type"),
                start_date=data["start_date"],
                end_date=data["end_date"],
                is_regular_period=data.get("is_regular_period", True),
                year_weight=data.get("year_weight"),
            )
        except ValueError as e:
            errors = e.args[0] if e.args and isinstance(e.args[0], dict) else {"non_field_errors": str(e)}
            if isinstance(errors, dict):
                first_error = next(iter(errors.values()))
                msg = str(first_error) if first_error else "No se pudo crear"
            else:
                msg = "No se pudo crear"
            return error_response(
                msg=msg,
                data=errors,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        out = self.get_serializer(period)
        return ok_response(out.data, msg="Período académico creado", status_code=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        update_kwargs = {k: v for k, v in data.items() if k != "period_type"}
        try:
            period = AcademicService.update_academic_period(instance.id, **update_kwargs)
        except ValueError as e:
            errors = e.args[0] if e.args and isinstance(e.args[0], dict) else {"non_field_errors": str(e)}
            if isinstance(errors, dict):
                first_error = next(iter(errors.values()))
                msg = str(first_error) if first_error else "No se pudo actualizar"
            else:
                msg = "No se pudo actualizar"
            return error_response(
                msg=msg,
                data=errors,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        out = self.get_serializer(period)
        return ok_response(out.data, msg="Período académico actualizado")

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="Listar asignaciones docente-materia", tags=["academic"]
    ),
    retrieve=extend_schema(
        summary="Obtener asignación docente-materia", tags=["academic"]
    ),
    create=extend_schema(summary="Crear asignación docente-materia", tags=["academic"]),
    update=extend_schema(
        summary="Actualizar asignación docente-materia", tags=["academic"]
    ),
    partial_update=extend_schema(
        summary="Actualizar asignación docente-materia parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(
        summary="Eliminar asignación docente-materia", tags=["academic"]
    ),
    soft_delete=extend_schema(
        summary="Desactivar asignación docente-materia", tags=["academic"]
    ),
)
class TeacherSubjectSectionViewSet(BaseAcademicViewSet):
    serializer_class = TeacherSubjectSectionSerializer
    action_permissions = {
        "list": academic.VIEW_TEACHER_SUBJECT,
        "retrieve": academic.VIEW_TEACHER_SUBJECT,
        "create": academic.CREATE_TEACHER_SUBJECT,
        "update": academic.UPDATE_TEACHER_SUBJECT,
        "partial_update": academic.UPDATE_TEACHER_SUBJECT,
        "destroy": academic.DELETE_TEACHER_SUBJECT,
        "soft_delete": academic.DELETE_TEACHER_SUBJECT,
    }
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        drf_filters.OrderingFilter,
    ]
    filterset_class = TeacherSubjectSectionFilter
    search_fields = [
        "user__person__names",
        "user__person__last_names",
        "user__username",
        "user__email",
        "subject_offering__section__school_year__name",
        "subject_offering__section__academic_grade__name",
        "subject_offering__section__parallel",
        "subject_offering__subject_academic_config__subject__name",
    ]
    ordering_fields = ["id", "created_at", "is_active"]
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = TeacherSubjectSectionRepository()

    def get_queryset(self):
        return self.repository.get_all().select_related(
            "user__person",
            "subject_offering__section__school_year",
            "subject_offering__section__academic_grade",
            "subject_offering__subject_academic_config__subject",
            "subject_offering__subject_academic_config__academic_grade",
        )


@extend_schema_view(
    list=extend_schema(summary="Listar configuraciones académicas", tags=["academic"]),
    retrieve=extend_schema(
        summary="Obtener configuración académica", tags=["academic"]
    ),
    create=extend_schema(summary="Crear configuración académica", tags=["academic"]),
    update=extend_schema(
        summary="Actualizar configuración académica", tags=["academic"]
    ),
    partial_update=extend_schema(
        summary="Actualizar configuración académica parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(
        summary="Eliminar configuración académica", tags=["academic"]
    ),
    soft_delete=extend_schema(
        summary="Desactivar configuración académica", tags=["academic"]
    ),
)
class SubjectAcademicConfigViewSet(BaseAcademicViewSet):
    serializer_class = SubjectAcademicConfigSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT_CONFIG,
        "retrieve": academic.VIEW_SUBJECT_CONFIG,
        "create": academic.CREATE_SUBJECT_CONFIG,
        "update": academic.UPDATE_SUBJECT_CONFIG,
        "partial_update": academic.UPDATE_SUBJECT_CONFIG,
        "destroy": academic.DELETE_SUBJECT_CONFIG,
        "soft_delete": academic.DELETE_SUBJECT_CONFIG,
    }
    ordering_fields = ["weekly_hours"]
    ordering = ["subject"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectAcademicConfigRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar ofertas de materia", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener oferta de materia", tags=["academic"]),
    create=extend_schema(summary="Crear oferta de materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar oferta de materia", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar oferta de materia parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar oferta de materia", tags=["academic"]),
    soft_delete=extend_schema(
        summary="Desactivar oferta de materia", tags=["academic"]
    ),
)
class SubjectOfferingViewSet(BaseAcademicViewSet):
    serializer_class = SubjectOfferingSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT_OFFERING,
        "retrieve": academic.VIEW_SUBJECT_OFFERING,
        "create": academic.CREATE_SUBJECT_OFFERING,
        "update": academic.UPDATE_SUBJECT_OFFERING,
        "partial_update": academic.UPDATE_SUBJECT_OFFERING,
        "destroy": academic.DELETE_SUBJECT_OFFERING,
        "soft_delete": academic.DELETE_SUBJECT_OFFERING,
    }
    ordering_fields = ["id"]
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectOfferingRepository()

    def get_queryset(self):
        return self.repository.get_all()






@extend_schema_view(
    list=extend_schema(summary="Listar tipos de periodo", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener tipo de periodo", tags=["academic"]),
    create=extend_schema(summary="Crear tipo de periodo", tags=["academic"]),
    update=extend_schema(summary="Actualizar tipo de periodo", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar tipo de periodo parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar tipo de periodo", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar tipo de periodo", tags=["academic"]),
)
class PeriodTypeViewSet(BaseAcademicViewSet):
    serializer_class = PeriodTypeSerializer
    action_permissions = {
        "list": academic.VIEW_PERIOD_TYPE,
        "retrieve": academic.VIEW_PERIOD_TYPE,
        "create": academic.CREATE_PERIOD_TYPE,
        "update": academic.UPDATE_PERIOD_TYPE,
        "partial_update": academic.UPDATE_PERIOD_TYPE,
        "destroy": academic.DELETE_PERIOD_TYPE,
        "soft_delete": academic.DELETE_PERIOD_TYPE,
    }
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = PeriodTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar horarios académicos", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener horario académico", tags=["academic"]),
    create=extend_schema(summary="Crear horario académico", tags=["academic"]),
    update=extend_schema(summary="Actualizar horario académico", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar horario académico parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar horario académico", tags=["academic"]),
    soft_delete=extend_schema(
        summary="Desactivar horario académico", tags=["academic"]
    ),
)
class ClassScheduleViewSet(BaseAcademicViewSet):
    serializer_class = ClassScheduleSerializer
    action_permissions = {
        "list": academic.VIEW_CLASS_SCHEDULE,
        "retrieve": academic.VIEW_CLASS_SCHEDULE,
        "create": academic.CREATE_CLASS_SCHEDULE,
        "update": academic.UPDATE_CLASS_SCHEDULE,
        "partial_update": academic.UPDATE_CLASS_SCHEDULE,
        "destroy": academic.DELETE_CLASS_SCHEDULE,
        "soft_delete": academic.DELETE_CLASS_SCHEDULE,
        "by_section": academic.VIEW_CLASS_SCHEDULE,
        "my_schedule": None,
        "my_today": None,
    }
    ordering_fields = ["day_of_week", "start_time"]
    ordering = ["day_of_week", "start_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ClassScheduleRepository()

    def get_queryset(self):
        return self.repository.get_all()

    @extend_schema(
        summary="Horario de una sección",
        description="Retorna el horario completo de una sección.",
        tags=["academic"],
    )
    @action(detail=False, methods=["get"])
    def by_section(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return error_response("section_id es requerido", status_code=status.HTTP_400_BAD_REQUEST)
        qs = self.repository.get_by_section(section_id)
        serializer = self.get_serializer(qs, many=True)
        return ok_response(serializer.data)

    @extend_schema(
        summary="Mi horario",
        description="Retorna el horario del estudiante o docente autenticado.",
        tags=["academic"],
    )
    @action(detail=False, methods=["get"])
    def my_schedule(self, request):
        user = request.user
        if user.user_category == "ESTUDIANTE":
            student = getattr(user, "student", None)
            if not student:
                return error_response("Perfil de estudiante no encontrado", status_code=status.HTTP_404_NOT_FOUND)
            qs = self.repository.get_by_student(student.id)
        else:
            qs = self.repository.get_by_teacher(user.id)
        serializer = self.get_serializer(qs, many=True)
        return ok_response(serializer.data)

    @extend_schema(
        summary="Clases de hoy",
        description="Retorna las clases de HOY del docente autenticado.",
        tags=["academic"],
    )
    @action(detail=False, methods=["get"])
    def my_today(self, request):
        user = request.user
        qs = self.repository.get_today_for_teacher(user.id)
        serializer = self.get_serializer(qs, many=True)
        return ok_response(serializer.data)
