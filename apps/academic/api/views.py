from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import academic

from ..repositories import (
    SubjectRepository,
    AcademicPeriodRepository,
    PeriodTypeRepository,
    TeacherSubjectSectionRepository,
    SubjectAcademicConfigRepository,
    SubjectOfferingRepository,
    InterdisciplinaryProjectRepository,
    SubjectProjectRepository,
    DayOfWeekRepository,
    ClassScheduleRepository,
)
from .serializers import (
    AcademicPeriodSerializer,
    ClassScheduleSerializer,
    DayOfWeekSerializer,
    InterdisciplinaryProjectSerializer,
    PeriodTypeSerializer,
    SubjectAcademicConfigSerializer,
    SubjectOfferingSerializer,
    SubjectProjectSerializer,
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
            return Response({"id": instance.id, "is_active": False})
        return Response("Este modelo no soporta borrado lógico", status=400)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicPeriodRepository()

    def get_queryset(self):
        return self.repository.get_all()


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = TeacherSubjectSectionRepository()

    def get_queryset(self):
        return self.repository.get_all()


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectOfferingRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(
        summary="Listar proyectos interdisciplinarios", tags=["academic"]
    ),
    retrieve=extend_schema(
        summary="Obtener proyecto interdisciplinario", tags=["academic"]
    ),
    create=extend_schema(
        summary="Crear proyecto interdisciplinario", tags=["academic"]
    ),
    update=extend_schema(
        summary="Actualizar proyecto interdisciplinario", tags=["academic"]
    ),
    partial_update=extend_schema(
        summary="Actualizar proyecto interdisciplinario parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(
        summary="Eliminar proyecto interdisciplinario", tags=["academic"]
    ),
    soft_delete=extend_schema(
        summary="Desactivar proyecto interdisciplinario", tags=["academic"]
    ),
)
class InterdisciplinaryProjectViewSet(BaseAcademicViewSet):
    serializer_class = InterdisciplinaryProjectSerializer
    action_permissions = {
        "list": academic.VIEW_INTERDISCIPLINARY_PROJECT,
        "retrieve": academic.VIEW_INTERDISCIPLINARY_PROJECT,
        "create": academic.CREATE_INTERDISCIPLINARY_PROJECT,
        "update": academic.UPDATE_INTERDISCIPLINARY_PROJECT,
        "partial_update": academic.UPDATE_INTERDISCIPLINARY_PROJECT,
        "destroy": academic.DELETE_INTERDISCIPLINARY_PROJECT,
        "soft_delete": academic.DELETE_INTERDISCIPLINARY_PROJECT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = InterdisciplinaryProjectRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar proyectos de materia", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener proyecto de materia", tags=["academic"]),
    create=extend_schema(summary="Crear proyecto de materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar proyecto de materia", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar proyecto de materia parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar proyecto de materia", tags=["academic"]),
    soft_delete=extend_schema(
        summary="Desactivar proyecto de materia", tags=["academic"]
    ),
)
class SubjectProjectViewSet(BaseAcademicViewSet):
    serializer_class = SubjectProjectSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT_PROJECT,
        "retrieve": academic.VIEW_SUBJECT_PROJECT,
        "create": academic.CREATE_SUBJECT_PROJECT,
        "update": academic.UPDATE_SUBJECT_PROJECT,
        "partial_update": academic.UPDATE_SUBJECT_PROJECT,
        "destroy": academic.DELETE_SUBJECT_PROJECT,
        "soft_delete": academic.DELETE_SUBJECT_PROJECT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectProjectRepository()

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = PeriodTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar días de la semana", tags=["academic"]),
    retrieve=extend_schema(summary="Obtener día de la semana", tags=["academic"]),
    create=extend_schema(summary="Crear día de la semana", tags=["academic"]),
    update=extend_schema(summary="Actualizar día de la semana", tags=["academic"]),
    partial_update=extend_schema(
        summary="Actualizar día de la semana parcialmente", tags=["academic"]
    ),
    destroy=extend_schema(summary="Eliminar día de la semana", tags=["academic"]),
)
class DayOfWeekViewSet(BaseAcademicViewSet):
    serializer_class = DayOfWeekSerializer
    action_permissions = {
        "list": academic.VIEW_DAY_OF_WEEK,
        "retrieve": academic.VIEW_DAY_OF_WEEK,
        "create": academic.CREATE_DAY_OF_WEEK,
        "update": academic.UPDATE_DAY_OF_WEEK,
        "partial_update": academic.UPDATE_DAY_OF_WEEK,
        "destroy": academic.DELETE_DAY_OF_WEEK,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = DayOfWeekRepository()

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
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ClassScheduleRepository()

    def get_queryset(self):
        return self.repository.get_all()
