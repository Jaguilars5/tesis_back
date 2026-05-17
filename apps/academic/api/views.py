from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import HasPermission
from apps.core.constants.permissions import academic
from apps.core.utils import ok_response, error_response
from ..models import (
    Section,
    Subject,
    Config_Academic,
    Academic_Period,
    Academic_Activity,
    Timing_Regime,
    Teacher_Subject_Section,
    SubjectAcademicConfig,
    SubjectOffering,
)
from .serializers import (
    SectionSerializer,
    SubjectSerializer,
    Config_AcademicSerializer,
    Academic_PeriodSerializer,
    Academic_ActivitySerializer,
    Timing_RegimeSerializer,
    Teacher_Subject_SectionSerializer,
    SubjectAcademicConfigSerializer,
    SubjectOfferingSerializer,
)


class BaseAcademicViewSet(viewsets.ModelViewSet):
    """ViewSet base para modelos académicos con soporte de StandardResponse"""

    permission_classes = [IsAuthenticated, HasPermission]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return ok_response(response.data)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return ok_response(response.data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return ok_response(response.data, status=201)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return ok_response(response.data)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "active"):
            instance.active = False
            instance.save()
            return ok_response({"id": instance.id, "active": False})
        return error_response("Este modelo no soporta borrado lógico", status=400)


class SectionViewSet(BaseAcademicViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    action_permissions = {
        "list": academic.VIEW_SECTION,
        "retrieve": academic.VIEW_SECTION,
        "create": academic.CREATE_SECTION,
        "update": academic.UPDATE_SECTION,
        "partial_update": academic.UPDATE_SECTION,
        "destroy": academic.DELETE_SECTION,
        "soft_delete": academic.DELETE_SECTION,
    }


class SubjectViewSet(BaseAcademicViewSet):
    queryset = Subject.objects.all()
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


class ConfigAcademicViewSet(BaseAcademicViewSet):
    queryset = Config_Academic.objects.all()
    serializer_class = Config_AcademicSerializer
    action_permissions = {
        "list": academic.VIEW_CONFIG,
        "retrieve": academic.VIEW_CONFIG,
        "create": academic.CREATE_CONFIG,
        "update": academic.UPDATE_CONFIG,
        "partial_update": academic.UPDATE_CONFIG,
        "destroy": academic.DELETE_CONFIG,
        "soft_delete": academic.DELETE_CONFIG,
    }


class AcademicPeriodViewSet(BaseAcademicViewSet):
    queryset = Academic_Period.objects.all()
    serializer_class = Academic_PeriodSerializer
    action_permissions = {
        "list": academic.VIEW_PERIOD,
        "retrieve": academic.VIEW_PERIOD,
        "create": academic.CREATE_PERIOD,
        "update": academic.UPDATE_PERIOD,
        "partial_update": academic.UPDATE_PERIOD,
        "destroy": academic.DELETE_PERIOD,
        "soft_delete": academic.DELETE_PERIOD,
    }


class AcademicActivityViewSet(BaseAcademicViewSet):
    queryset = Academic_Activity.objects.all()
    serializer_class = Academic_ActivitySerializer
    action_permissions = {
        "list": academic.VIEW_ACTIVITY,
        "retrieve": academic.VIEW_ACTIVITY,
        "create": academic.CREATE_ACTIVITY,
        "update": academic.UPDATE_ACTIVITY,
        "partial_update": academic.UPDATE_ACTIVITY,
        "destroy": academic.DELETE_ACTIVITY,
        "soft_delete": academic.DELETE_ACTIVITY,
    }


class TimingRegimeViewSet(BaseAcademicViewSet):
    queryset = Timing_Regime.objects.all()
    serializer_class = Timing_RegimeSerializer
    action_permissions = {
        "list": academic.VIEW_REGIME,
        "retrieve": academic.VIEW_REGIME,
        "create": academic.CREATE_REGIME,
        "update": academic.UPDATE_REGIME,
        "partial_update": academic.UPDATE_REGIME,
        "destroy": academic.DELETE_REGIME,
        "soft_delete": academic.DELETE_REGIME,
    }


class TeacherSubjectSectionViewSet(BaseAcademicViewSet):
    queryset = Teacher_Subject_Section.objects.all()
    serializer_class = Teacher_Subject_SectionSerializer
    action_permissions = {
        "list": academic.VIEW_TEACHER_SUBJECT,
        "retrieve": academic.VIEW_TEACHER_SUBJECT,
        "create": academic.CREATE_TEACHER_SUBJECT,
        "update": academic.UPDATE_TEACHER_SUBJECT,
        "partial_update": academic.UPDATE_TEACHER_SUBJECT,
        "destroy": academic.DELETE_TEACHER_SUBJECT,
        "soft_delete": academic.DELETE_TEACHER_SUBJECT,
    }


class SubjectAcademicConfigViewSet(BaseAcademicViewSet):
    queryset = SubjectAcademicConfig.objects.all()
    serializer_class = SubjectAcademicConfigSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT,
        "retrieve": academic.VIEW_SUBJECT,
        "create": academic.CREATE_SUBJECT,
        "update": academic.UPDATE_SUBJECT,
        "partial_update": academic.UPDATE_SUBJECT,
        "destroy": academic.DELETE_SUBJECT,
        "soft_delete": academic.DELETE_SUBJECT,
    }


class SubjectOfferingViewSet(BaseAcademicViewSet):
    queryset = SubjectOffering.objects.all()
    serializer_class = SubjectOfferingSerializer
    action_permissions = {
        "list": academic.VIEW_SUBJECT,
        "retrieve": academic.VIEW_SUBJECT,
        "create": academic.CREATE_SUBJECT,
        "update": academic.UPDATE_SUBJECT,
        "partial_update": academic.UPDATE_SUBJECT,
        "destroy": academic.DELETE_SUBJECT,
        "soft_delete": academic.DELETE_SUBJECT,
    }
