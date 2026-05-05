"""
Vistas de API para el módulo Scheduling.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre horarios,
franjas horarias, disponibilidad y restricciones.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.constants.permissions import scheduling
from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import HasPermission
from apps.core.utils import ok_response, error_response

from ..repositories import (
    ScheduleSlotRepository,
    ScheduleTemplateConfigRepository,
    SubjectConstraintRepository,
    TeacherAvailabilityRepository,
    TimeSlotRepository,
)
from .serializers import (
    ScheduleSlotSerializer,
    ScheduleTemplateConfigSerializer,
    SubjectConstraintSerializer,
    TeacherAvailabilitySerializer,
    TimeSlotSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar registros", tags=["scheduling"]),
    retrieve=extend_schema(summary="Obtener registro", tags=["scheduling"]),
    create=extend_schema(summary="Crear registro", tags=["scheduling"]),
    update=extend_schema(summary="Actualizar registro", tags=["scheduling"]),
    partial_update=extend_schema(summary="Actualizar parcialmente", tags=["scheduling"]),
    destroy=extend_schema(summary="Eliminar registro", tags=["scheduling"]),
)
class BaseSchedulingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data, status=201)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            partial = kwargs.pop("partial", False)
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            if hasattr(instance, "active"):
                instance.active = False
                instance.save()
                return ok_response({"id": kwargs.get("pk"), "active": False})
            return error_response(
                f"{self.serializer_class.Meta.model.__name__} does not support soft delete."
            )
        except Exception as e:
            return error_response(e)


class ScheduleSlotViewSet(BaseSchedulingViewSet):
    serializer_class = ScheduleSlotSerializer
    action_permissions = {
        "list": scheduling.VIEW_SCHEDULE,
        "retrieve": scheduling.VIEW_SCHEDULE,
        "create": scheduling.CREATE_SCHEDULE,
        "update": scheduling.UPDATE_SCHEDULE,
        "partial_update": scheduling.UPDATE_SCHEDULE,
        "destroy": scheduling.DELETE_SCHEDULE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ScheduleSlotRepository()

    def get_queryset(self):
        return self.repository.get_all()


class TimeSlotViewSet(BaseSchedulingViewSet):
    serializer_class = TimeSlotSerializer
    action_permissions = {
        "list": scheduling.VIEW_TIMESLOT,
        "retrieve": scheduling.VIEW_TIMESLOT,
        "create": scheduling.CREATE_TIMESLOT,
        "update": scheduling.UPDATE_TIMESLOT,
        "partial_update": scheduling.UPDATE_TIMESLOT,
        "destroy": scheduling.DELETE_TIMESLOT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = TimeSlotRepository()

    def get_queryset(self):
        return self.repository.get_all()


class TeacherAvailabilityViewSet(BaseSchedulingViewSet):
    serializer_class = TeacherAvailabilitySerializer
    action_permissions = {
        "list": scheduling.VIEW_AVAILABILITY,
        "retrieve": scheduling.VIEW_AVAILABILITY,
        "create": scheduling.CREATE_AVAILABILITY,
        "update": scheduling.UPDATE_AVAILABILITY,
        "partial_update": scheduling.UPDATE_AVAILABILITY,
        "destroy": scheduling.DELETE_AVAILABILITY,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = TeacherAvailabilityRepository()

    def get_queryset(self):
        return self.repository.get_all()


class SubjectConstraintViewSet(BaseSchedulingViewSet):
    serializer_class = SubjectConstraintSerializer
    action_permissions = {
        "list": scheduling.VIEW_CONSTRAINT,
        "retrieve": scheduling.VIEW_CONSTRAINT,
        "create": scheduling.CREATE_CONSTRAINT,
        "update": scheduling.UPDATE_CONSTRAINT,
        "partial_update": scheduling.UPDATE_CONSTRAINT,
        "destroy": scheduling.DELETE_CONSTRAINT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectConstraintRepository()

    def get_queryset(self):
        return self.repository.get_all()


class ScheduleTemplateConfigViewSet(BaseSchedulingViewSet):
    serializer_class = ScheduleTemplateConfigSerializer
    action_permissions = {
        "list": scheduling.VIEW_TEMPLATE,
        "retrieve": scheduling.VIEW_TEMPLATE,
        "create": scheduling.CREATE_TEMPLATE,
        "update": scheduling.UPDATE_TEMPLATE,
        "partial_update": scheduling.UPDATE_TEMPLATE,
        "destroy": scheduling.DELETE_TEMPLATE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ScheduleTemplateConfigRepository()

    def get_queryset(self):
        return self.repository.get_all()
