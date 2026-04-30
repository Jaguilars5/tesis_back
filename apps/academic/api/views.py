from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.utils import ok_response, error_response
from ..models import (
    Section,
    Subject,
    Config_Academic,
    Academic_Period,
    Academic_Activity,
    Timing_Regime,
    Teacher_Subject_Section,
)
from .serializers import (
    SectionSerializer,
    SubjectSerializer,
    Config_AcademicSerializer,
    Academic_PeriodSerializer,
    Academic_ActivitySerializer,
    Timing_RegimeSerializer,
    Teacher_Subject_SectionSerializer,
)


class BaseAcademicViewSet(viewsets.ModelViewSet):
    """ViewSet base para modelos académicos con soporte de StandardResponse"""

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


class SubjectViewSet(BaseAcademicViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class ConfigAcademicViewSet(BaseAcademicViewSet):
    queryset = Config_Academic.objects.all()
    serializer_class = Config_AcademicSerializer


class AcademicPeriodViewSet(BaseAcademicViewSet):
    queryset = Academic_Period.objects.all()
    serializer_class = Academic_PeriodSerializer


class AcademicActivityViewSet(BaseAcademicViewSet):
    queryset = Academic_Activity.objects.all()
    serializer_class = Academic_ActivitySerializer


class TimingRegimeViewSet(BaseAcademicViewSet):
    queryset = Timing_Regime.objects.all()
    serializer_class = Timing_RegimeSerializer


class TeacherSubjectSectionViewSet(BaseAcademicViewSet):
    queryset = Teacher_Subject_Section.objects.all()
    serializer_class = Teacher_Subject_SectionSerializer
