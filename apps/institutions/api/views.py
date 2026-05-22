from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasPermission
from apps.core.constants.permissions import institutions

from ..services.institution_service import InstitutionService
from ..models import AcademicGrade, AcademicLevel, Classroom, DocumentType, RoomType, School_Year
from .serializers import (
    AcademicGradeSerializer,
    AcademicLevelSerializer,
    ClassroomSerializer,
    DocumentTypeSerializer,
    RoomTypeSerializer,
    School_YearSerializer,
)
from apps.core.utils import ok_response, error_response


class SchoolYearViewSet(viewsets.ModelViewSet):
    serializer_class = School_YearSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": institutions.VIEW_SCHOOL_YEAR,
        "retrieve": institutions.VIEW_SCHOOL_YEAR,
        "create": institutions.CREATE_SCHOOL_YEAR,
        "update": institutions.UPDATE_SCHOOL_YEAR,
        "partial_update": institutions.UPDATE_SCHOOL_YEAR,
        "destroy": institutions.DELETE_SCHOOL_YEAR,
        "list_by_institution": institutions.VIEW_SCHOOL_YEAR,
        "get_by_id": institutions.VIEW_SCHOOL_YEAR,
        "add_school_year": institutions.CREATE_SCHOOL_YEAR,
        "update_school_year": institutions.UPDATE_SCHOOL_YEAR,
        "soft_delete_school_year": institutions.DELETE_SCHOOL_YEAR,
    }

    def get_queryset(self):
        return School_Year.objects.filter(active=True).order_by("-start_date")

    @action(detail=False, methods=["post"], url_path="list")
    def list_by_institution(self, request):
        return ok_response(self.get_serializer(self.get_queryset(), many=True).data)

    @action(detail=False, methods=["post"], url_path="get")
    def get_by_id(self, request):
        school_year_id = request.data.get("id")
        if not school_year_id:
            return error_response('Se requiere "id"')
        try:
            school_year = School_Year.objects.get(id=school_year_id)
            return ok_response(self.get_serializer(school_year).data)
        except School_Year.DoesNotExist:
            return error_response("Año escolar no encontrado")

    @action(detail=False, methods=["post"], url_path="add")
    def add_school_year(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            school_year = InstitutionService.create_school_year(
                name=serializer.validated_data["name"],
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
            )
            return ok_response(self.get_serializer(school_year).data, status=201)
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["post"], url_path="update")
    def update_school_year(self, request):
        school_year_id = request.data.get("id")
        if not school_year_id:
            return error_response('Se requiere "id"')
        try:
            school_year = School_Year.objects.get(id=school_year_id)
        except School_Year.DoesNotExist:
            return error_response("Año escolar no encontrado")
        data = {k: v for k, v in request.data.items() if k != "id"}
        serializer = self.get_serializer(school_year, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            updated = InstitutionService.update_school_year(
                school_year_id, **serializer.validated_data
            )
            return ok_response(self.get_serializer(updated).data)
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["post"], url_path="soft-delete")
    def soft_delete_school_year(self, request):
        school_year_id = request.data.get("id")
        if not school_year_id:
            return error_response('Se requiere "id"')
        try:
            InstitutionService.deactivate_school_year(school_year_id)
            return ok_response({"id": school_year_id, "active": False})
        except ValueError as e:
            return error_response(e)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            school_year = InstitutionService.create_school_year(
                name=serializer.validated_data["name"],
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
            )
            return ok_response(self.get_serializer(school_year).data, status=201)
        except ValueError as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        try:
            school_year = InstitutionService.update_school_year(
                kwargs["pk"], **serializer.validated_data
            )
            return ok_response(self.get_serializer(school_year).data)
        except ValueError as e:
            return error_response(e)

    def destroy(self, request, *args, **kwargs):
        try:
            InstitutionService.deactivate_school_year(kwargs["pk"])
            return ok_response({"id": kwargs["pk"], "active": False})
        except ValueError as e:
            return error_response(e)


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": institutions.VIEW_CLASSROOM,
        "retrieve": institutions.VIEW_CLASSROOM,
        "create": institutions.CREATE_CLASSROOM,
        "update": institutions.UPDATE_CLASSROOM,
        "partial_update": institutions.UPDATE_CLASSROOM,
        "destroy": institutions.DELETE_CLASSROOM,
        "list_by_institution": institutions.VIEW_CLASSROOM,
        "get_by_id": institutions.VIEW_CLASSROOM,
        "add_classroom": institutions.CREATE_CLASSROOM,
        "update_classroom": institutions.UPDATE_CLASSROOM,
        "soft_delete_classroom": institutions.DELETE_CLASSROOM,
    }

    def get_queryset(self):
        return Classroom.objects.filter(active=True).order_by("name")

    @action(detail=False, methods=["post"], url_path="list")
    def list_by_institution(self, request):
        return ok_response(self.get_serializer(self.get_queryset(), many=True).data)

    @action(detail=False, methods=["post"], url_path="get")
    def get_by_id(self, request):
        classroom_id = request.data.get("id")
        if not classroom_id:
            return error_response('Se requiere "id"')
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            return ok_response(self.get_serializer(classroom).data)
        except Classroom.DoesNotExist:
            return error_response("Aula no encontrada")

    @action(detail=False, methods=["post"], url_path="add")
    def add_classroom(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            classroom = InstitutionService.create_classroom(
                name=serializer.validated_data["name"],
                room_type_id=serializer.validated_data["room_type"].id,
                capacity=serializer.validated_data["capacity"],
            )
            return ok_response(self.get_serializer(classroom).data, status=201)
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["post"], url_path="update")
    def update_classroom(self, request):
        classroom_id = request.data.get("id")
        if not classroom_id:
            return error_response('Se requiere "id"')
        try:
            classroom = Classroom.objects.get(id=classroom_id)
        except Classroom.DoesNotExist:
            return error_response("Aula no encontrada")
        data = {k: v for k, v in request.data.items() if k != "id"}
        serializer = self.get_serializer(classroom, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            updated = InstitutionService.update_classroom(
                classroom_id, **serializer.validated_data
            )
            return ok_response(self.get_serializer(updated).data)
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["post"], url_path="soft-delete")
    def soft_delete_classroom(self, request):
        classroom_id = request.data.get("id")
        if not classroom_id:
            return error_response('Se requiere "id"')
        try:
            InstitutionService.deactivate_classroom(classroom_id)
            return ok_response({"id": classroom_id, "active": False})
        except ValueError as e:
            return error_response(e)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            classroom = InstitutionService.create_classroom(
                name=serializer.validated_data["name"],
                room_type_id=serializer.validated_data["room_type"].id,
                capacity=serializer.validated_data["capacity"],
            )
            return ok_response(self.get_serializer(classroom).data, status=201)
        except ValueError as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        try:
            classroom = InstitutionService.update_classroom(
                kwargs["pk"], **serializer.validated_data
            )
            return ok_response(self.get_serializer(classroom).data)
        except ValueError as e:
            return error_response(e)

    def destroy(self, request, *args, **kwargs):
        try:
            InstitutionService.deactivate_classroom(kwargs["pk"])
            return ok_response({"id": kwargs["pk"], "active": False})
        except ValueError as e:
            return error_response(e)


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": institutions.VIEW_DOCUMENT_TYPE,
        "retrieve": institutions.VIEW_DOCUMENT_TYPE,
    }

    def get_queryset(self):
        return DocumentType.objects.all().order_by("name")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ok_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)


class RoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoomTypeSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": institutions.VIEW_ROOM_TYPE,
        "retrieve": institutions.VIEW_ROOM_TYPE,
    }

    def get_queryset(self):
        return RoomType.objects.all().order_by("name")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ok_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)


class AcademicLevelViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicLevelSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": institutions.VIEW_INSTITUTION,
        "retrieve": institutions.VIEW_INSTITUTION,
        "create": institutions.CREATE_INSTITUTION,
        "update": institutions.UPDATE_INSTITUTION,
        "partial_update": institutions.UPDATE_INSTITUTION,
        "destroy": institutions.DELETE_INSTITUTION,
    }

    def get_queryset(self):
        return AcademicLevel.objects.all().order_by("name")


class AcademicGradeViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicGradeSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": institutions.VIEW_INSTITUTION,
        "retrieve": institutions.VIEW_INSTITUTION,
        "create": institutions.CREATE_INSTITUTION,
        "update": institutions.UPDATE_INSTITUTION,
        "partial_update": institutions.UPDATE_INSTITUTION,
        "destroy": institutions.DELETE_INSTITUTION,
    }

    def get_queryset(self):
        return AcademicGrade.objects.all().order_by("sequence_order")
