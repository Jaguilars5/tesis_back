from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.constants.permissions import students
from apps.core.permissions import HasPermission
from apps.core.utils import ok_response, error_response

from ..models import Enrollment, EnrollmentStatus, Student, Student_Representative
from ..services.students_service import StudentService
from ..services.enrollment_service import EnrollmentService
from ..repositories.enrollment_repo import EnrollmentRepository
from .serializers import (
    EnrollmentCreateSerializer,
    EnrollmentSerializer,
    EnrollmentStatusSerializer,
    StudentSerializer,
    StudentDetailSerializer,
    StudentRepresentativeSerializer,
)
from .filters import StudentFilter


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet para Student"""

    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ["person__names", "person__last_names", "person__document_number", "student_code"]
    ordering_fields = ["person__last_names", "active"]
    ordering = ["person__last_names"]
    action_permissions = {
        "list": students.VIEW_STUDENT,
        "retrieve": students.VIEW_STUDENT,
        "create": students.CREATE_STUDENT,
        "update": students.UPDATE_STUDENT,
        "partial_update": students.UPDATE_STUDENT,
        "destroy": students.DELETE_STUDENT,
        "by_section": students.VIEW_STUDENT,
        "search": students.VIEW_STUDENT,
        "representatives": students.VIEW_RELATIONSHIP,
    }

    def get_queryset(self):
        return Student.objects.filter(active=True)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentSerializer

    def create(self, request, *args, **kwargs):
        try:
            student = StudentService.create_student(
                document_number=request.data.get("document_number"),
                names=request.data.get("names"),
                last_names=request.data.get("last_names"),
                birth_date=request.data.get("birth_date"),
                email=request.data.get("email", ""),
                phone=request.data.get("phone", ""),
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
            .select_related("person")
            .order_by("-is_primary")
        )

        serializer = StudentRepresentativeSerializer(relationships, many=True)
        return ok_response(serializer.data)





class StudentRepresentativeViewSet(viewsets.ModelViewSet):
    """ViewSet para Student_Representative"""

    serializer_class = StudentRepresentativeSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "person", "is_primary"]
    ordering_fields = ["created_at"]
    ordering = ["-is_primary", "created_at"]
    action_permissions = {
        "list": students.VIEW_RELATIONSHIP,
        "retrieve": students.VIEW_RELATIONSHIP,
        "create": students.CREATE_RELATIONSHIP,
        "update": students.UPDATE_RELATIONSHIP,
        "partial_update": students.UPDATE_RELATIONSHIP,
        "destroy": students.DELETE_RELATIONSHIP,
        "set_primary": students.UPDATE_RELATIONSHIP,
        "unlink": students.DELETE_RELATIONSHIP,
    }

    def get_queryset(self):
        return Student_Representative.objects.filter(
            student__active=True
        ).select_related("student", "person")

    def create(self, request, *args, **kwargs):
        try:
            relationship = StudentService.assign_representative(
                student_id=request.data.get("student"),
                person_id=request.data.get("person"),
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
                person_id=request.data.get("person"),
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
                person_id=relationship.person_id,
            )
            return ok_response({"unlinked": True})
        except ValueError as e:
            return error_response(e)


class EnrollmentStatusViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentStatusSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": students.VIEW_ENROLLMENT_STATUS,
        "retrieve": students.VIEW_ENROLLMENT_STATUS,
    }

    def get_queryset(self):
        return EnrollmentStatus.objects.all().order_by("name")

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


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["student", "section", "enrollment_status", "enrollment_status__code"]
    search_fields = ["student__person__names", "student__person__last_names", "student__student_code"]
    ordering = ["-enrollment_date"]
    action_permissions = {
        "list": students.VIEW_ENROLLMENT,
        "retrieve": students.VIEW_ENROLLMENT,
        "create": students.CREATE_ENROLLMENT,
        "update": students.UPDATE_ENROLLMENT,
        "partial_update": students.UPDATE_ENROLLMENT,
        "destroy": students.DELETE_ENROLLMENT,
        "withdraw": students.WITHDRAW_STUDENT,
        "transfer": students.TRANSFER_STUDENT,
        "by_section": students.VIEW_ENROLLMENT,
        "by_student": students.VIEW_ENROLLMENT,
    }

    def get_queryset(self):
        return Enrollment.objects.all().select_related(
            "student__person", "section", "enrollment_status"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            enrollment = EnrollmentService.enroll_student(
                student=serializer.validated_data["student"],
                section=serializer.validated_data["section"],
                enrollment_date=serializer.validated_data.get("enrollment_date"),
            )
            return ok_response(
                self.get_serializer(enrollment).data, status=201
            )
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="withdraw")
    def withdraw(self, request, pk=None):
        try:
            enrollment = self.get_object()
            EnrollmentService.withdraw_student(enrollment)
            return ok_response(
                self.get_serializer(enrollment).data
            )
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="transfer")
    def transfer(self, request, pk=None):
        new_section_id = request.data.get("section_id")
        if not new_section_id:
            return error_response('Se requiere "section_id"')
        from ..models import Section
        try:
            new_section = Section.objects.get(id=new_section_id)
        except Section.DoesNotExist:
            return error_response("Sección no encontrada", 404)
        try:
            enrollment = self.get_object()
            EnrollmentService.transfer_student(enrollment, new_section)
            return ok_response(
                self.get_serializer(enrollment).data
            )
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["get"], url_path="by-section")
    def by_section(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return error_response('Se requiere "section_id"')
        status_code = request.query_params.get("status", "ACT")
        enrollments = EnrollmentRepository.get_students_by_section(
            section_id, status_code
        )
        serializer = self.get_serializer(enrollments, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-student")
    def by_student(self, request):
        student_id = request.query_params.get("student_id")
        if not student_id:
            return error_response('Se requiere "student_id"')
        enrollment = EnrollmentRepository.get_active_by_student(student_id)
        if not enrollment:
            return error_response("No tiene matrícula activa", 404)
        return ok_response(self.get_serializer(enrollment).data)
