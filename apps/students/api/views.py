from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.core.utils import ok_response, error_response

from ..models import Student, Representative, Student_Representative
from ..services.students_service import StudentService
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    RepresentativeSerializer,
    RepresentativeDetailSerializer,
    StudentRepresentativeSerializer,
)
from .filters import StudentFilter, RepresentativeFilter


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet para Student"""

    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ["names", "last_names", "dni", "enrollment_number"]
    ordering_fields = ["last_names", "enrollment_date", "active"]
    ordering = ["last_names"]

    def get_queryset(self):
        return Student.objects.filter(active=True).select_related("section")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentSerializer

    def create(self, request, *args, **kwargs):
        try:
            student = StudentService.create_student(
                dni=request.data.get("dni"),
                names=request.data.get("names"),
                last_names=request.data.get("last_names"),
                birth_date=request.data.get("birth_date"),
                section_id=request.data.get("section"),
                enrollment_number=request.data.get("enrollment_number"),
                device_origin=request.data.get("device_origin"),
            )
            serializer = self.get_serializer(student)
            return ok_response(serializer.data, status=201)
        except ValueError as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        try:
            student = StudentService.update_student(kwargs.get("pk"), **request.data)
            serializer = self.get_serializer(student)
            return ok_response(serializer.data)
        except ValueError as e:
            return error_response(e)
    def destroy(self, request, *args, **kwargs):
        """Desactiva un estudiante (soft delete)"""
        try:
            StudentService.deactivate_student(kwargs.get("pk"))
            return ok_response({"id": kwargs.get("pk"), "deleted": True})
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["get"])
    def by_section(self, request):
        """Estudiantes de una sección"""
        section_id = request.query_params.get("section_id")
        if not section_id:
            return error_response("section_id requerido")

        students = StudentService.list_students_by_section(section_id)
        serializer = self.get_serializer(students, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Búsqueda de estudiantes"""
        query = request.query_params.get("q", "")
        if not query:
            return error_response("Parámetro q requerido")

        students = StudentService.search_students(query)
        serializer = self.get_serializer(students, many=True)
        return ok_response(serializer.data)

    @action(detail=True, methods=["get"])
    def representatives(self, request, pk=None):
        """Representantes de un estudiante"""
        from .serializers import StudentRepresentativeSerializer

        relationships = (
            Student_Representative.objects.filter(student_id=pk)
            .select_related("representative")
            .order_by("-is_primary")
        )

        serializer = StudentRepresentativeSerializer(relationships, many=True)
        return ok_response(serializer.data)


class RepresentativeViewSet(viewsets.ModelViewSet):
    """ViewSet para Representative"""

    serializer_class = RepresentativeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RepresentativeFilter
    search_fields = ["names", "last_names", "dni", "phone", "email"]
    ordering_fields = ["last_names", "kinship", "active"]
    ordering = ["last_names"]

    def get_queryset(self):
        return Representative.objects.filter(active=True)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RepresentativeDetailSerializer
        return RepresentativeSerializer

    def create(self, request, *args, **kwargs):
        try:
            representative = StudentService.create_representative(
                dni=request.data.get("dni"),
                names=request.data.get("names"),
                last_names=request.data.get("last_names"),
                phone=request.data.get("phone"),
                email=request.data.get("email"),
                address=request.data.get("address"),
            )
            serializer = self.get_serializer(representative)
            return ok_response(serializer.data, status=201)
        except ValueError as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        try:
            representative = StudentService.update_representative(
                kwargs.get("pk"), **request.data
            )
            serializer = self.get_serializer(representative)
            return ok_response(serializer.data)
        except ValueError as e:
            return error_response(e)
    def destroy(self, request, *args, **kwargs):
        """Desactiva un representante (soft delete)"""
        try:
            StudentService.deactivate_representative(kwargs.get("pk"))
            return ok_response({"id": kwargs.get("pk"), "deleted": True})
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Búsqueda de representantes"""
        query = request.query_params.get("q", "")
        if not query:
            return error_response("Parámetro q requerido")

        representatives = StudentService.search_representatives(query)
        serializer = self.get_serializer(representatives, many=True)
        return ok_response(serializer.data)


class StudentRepresentativeViewSet(viewsets.ModelViewSet):
    """ViewSet para Student_Representative"""

    serializer_class = StudentRepresentativeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "representative", "is_primary"]
    ordering_fields = ["created_at"]
    ordering = ["-is_primary", "created_at"]

    def get_queryset(self):
        return Student_Representative.objects.filter(
            student__active=True, representative__active=True
        ).select_related("student", "representative")

    def create(self, request, *args, **kwargs):
        try:
            relationship = StudentService.assign_representative(
                student_id=request.data.get("student"),
                representative_id=request.data.get("representative"),
                kinship=request.data.get("kinship", "Padre"),
                is_primary=request.data.get("is_primary", False),
                can_pickup=request.data.get("can_pickup", True),
                emergency_contact=request.data.get("emergency_contact", False),
                receives_notifications=request.data.get("receives_notifications", True),
            )
            serializer = self.get_serializer(relationship)
            return ok_response(serializer.data, status=201)
        except ValueError as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        relationship = self.get_object()

        # Actualizar campos
        for field in ["kinship", "can_pickup", "emergency_contact", "receives_notifications", "is_primary"]:
            if field in request.data:
                setattr(relationship, field, request.data.get(field))

        relationship.save()
        serializer = self.get_serializer(relationship)
        return ok_response(serializer.data)

    @action(detail=False, methods=["post"])
    def set_primary(self, request):
        """Establecer como principal"""
        try:
            StudentService.set_primary_representative(
                student_id=request.data.get("student"),
                representative_id=request.data.get("representative"),
            )
            return ok_response({"status": "Principal actualizado"})
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["delete"])
    def unlink(self, request, pk=None):
        """Desasignar representante"""
        relationship = self.get_object()
        try:
            StudentService.remove_representative(
                student_id=relationship.student_id,
                representative_id=relationship.representative_id,
            )
            return ok_response({"unlinked": True})
        except ValueError as e:
            return error_response(e)
