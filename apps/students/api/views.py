from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.constants.permissions import students
from apps.core.api.permissions import HasPermission

from ..services.students_service import StudentService
from ..services.enrollment_service import EnrollmentService
from ..repositories import EnrollmentRepository
from ..repositories.enrollment_status_repo import EnrollmentStatusRepository
from ..repositories.students_repo import (
    StudentRepository,
    StudentRepresentativeRepository,
)
from .serializers.serializers import (
    EnrollmentCreateSerializer,
    EnrollmentSerializer,
    EnrollmentStatusSerializer,
    StudentSerializer,
    StudentDetailSerializer,
    StudentRepresentativeSerializer,
)
from .filters.filters import StudentFilter


@extend_schema_view(
    list=extend_schema(summary="Listar estudiantes", tags=["students"]),
    retrieve=extend_schema(summary="Obtener estudiante", tags=["students"]),
    create=extend_schema(summary="Crear estudiante", tags=["students"]),
    update=extend_schema(summary="Actualizar estudiante", tags=["students"]),
    partial_update=extend_schema(
        summary="Actualizar estudiante parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Desactivar estudiante", tags=["students"]),
    by_section=extend_schema(summary="Estudiantes por sección", tags=["students"]),
    search=extend_schema(summary="Buscar estudiantes", tags=["students"]),
    representatives=extend_schema(
        summary="Representantes del estudiante", tags=["students"]
    ),
)
class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet para Student"""

    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = [
        "person__names",
        "person__last_names",
        "person__document_number",
        "student_code",
    ]
    ordering_fields = ["person__last_names", "is_active"]
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
        return StudentRepository.get_all()

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
            return Response(serializer.data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    def update(self, request, *args, **kwargs):
        try:
            student = StudentService.update_student(kwargs.get("pk"), **request.data)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except ValueError as e:
            return Response(str(e), status=400)

    def destroy(self, request, *args, **kwargs):
        """Desactiva un estudiante (soft delete)"""
        try:
            StudentService.deactivate_student(kwargs.get("pk"))
            return Response({"id": kwargs.get("pk"), "deleted": True})
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["get"])
    def by_section(self, request):
        """Estudiantes de una sección"""
        section_id = request.query_params.get("section_id")
        if not section_id:
            return Response("section_id requerido", status=400)

        students = StudentService.list_students_by_section(section_id)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Búsqueda de estudiantes"""
        query = request.query_params.get("q", "")
        if not query:
            return Response("Parámetro q requerido", status=400)

        students = StudentService.search_students(query)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def representatives(self, request, pk=None):
        """Representantes de un estudiante"""
        relationships = StudentRepresentativeRepository.get_by_student(pk)
        serializer = StudentRepresentativeSerializer(relationships, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="Listar representantes", tags=["students"]),
    retrieve=extend_schema(summary="Obtener representante", tags=["students"]),
    create=extend_schema(summary="Asignar representante", tags=["students"]),
    update=extend_schema(summary="Actualizar representante", tags=["students"]),
    partial_update=extend_schema(
        summary="Actualizar representante parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Eliminar representante", tags=["students"]),
    set_primary=extend_schema(
        summary="Establecer representante principal", tags=["students"]
    ),
    unlink=extend_schema(summary="Desasignar representante", tags=["students"]),
)
class StudentRepresentativeViewSet(viewsets.ModelViewSet):
    """ViewSet para StudentRepresentative"""

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
        return StudentRepresentativeRepository.get_all()

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
            return Response(serializer.data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    def update(self, request, *args, **kwargs):
        relationship = self.get_object()

        for field in [
            "kinship",
            "can_pickup",
            "emergency_contact",
            "receives_notifications",
            "is_primary",
        ]:
            if field in request.data:
                setattr(relationship, field, request.data.get(field))

        relationship.save()
        serializer = self.get_serializer(relationship)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def set_primary(self, request):
        """Establecer como principal"""
        try:
            StudentService.set_primary_representative(
                student_id=request.data.get("student"),
                person_id=request.data.get("person"),
            )
            return Response({"status": "Principal actualizado"})
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["delete"])
    def unlink(self, request, pk=None):
        """Desasignar representante"""
        relationship = self.get_object()
        try:
            StudentService.remove_representative(
                student_id=relationship.student_id,
                person_id=relationship.person_id,
            )
            return Response({"unlinked": True})
        except ValueError as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar estados de matrícula", tags=["students"]),
    retrieve=extend_schema(summary="Obtener estado de matrícula", tags=["students"]),
)
class EnrollmentStatusViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentStatusSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": students.VIEW_ENROLLMENT_STATUS,
        "retrieve": students.VIEW_ENROLLMENT_STATUS,
    }

    def get_queryset(self):
        return EnrollmentStatusRepository.get_all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar matrículas", tags=["students"]),
    retrieve=extend_schema(summary="Obtener matrícula", tags=["students"]),
    create=extend_schema(summary="Crear matrícula", tags=["students"]),
    update=extend_schema(summary="Actualizar matrícula", tags=["students"]),
    partial_update=extend_schema(
        summary="Actualizar matrícula parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Eliminar matrícula", tags=["students"]),
    withdraw=extend_schema(summary="Retirar estudiante", tags=["students"]),
    transfer=extend_schema(summary="Transferir estudiante", tags=["students"]),
    by_section=extend_schema(summary="Matrículas por sección", tags=["students"]),
    by_student=extend_schema(
        summary="Matrícula activa del estudiante", tags=["students"]
    ),
)
class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "student",
        "section",
        "enrollment_status",
        "enrollment_status__code",
    ]
    search_fields = [
        "student__person__names",
        "student__person__last_names",
        "student__student_code",
    ]
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
        return EnrollmentRepository.get_all()

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
            return Response(self.get_serializer(enrollment).data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="withdraw")
    def withdraw(self, request, pk=None):
        try:
            enrollment = self.get_object()
            reason = request.data.get("reason", "")
            EnrollmentService.withdraw_student(enrollment, reason=reason)
            return Response(self.get_serializer(enrollment).data)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="transfer")
    def transfer(self, request, pk=None):
        new_section_id = request.data.get("section_id")
        if not new_section_id:
            return Response('Se requiere "section_id"', status=400)
        try:
            enrollment = self.get_object()
            EnrollmentService.transfer_student(enrollment, new_section_id)
            return Response(self.get_serializer(enrollment).data)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["get"], url_path="by-section")
    def by_section(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return Response('Se requiere "section_id"', status=400)
        status_code = request.query_params.get("status", "ACT")
        enrollments = EnrollmentRepository.get_students_by_section(
            section_id, status_code
        )
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-student")
    def by_student(self, request):
        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response('Se requiere "student_id"', status=400)
        enrollment = EnrollmentRepository.get_active_by_student(student_id)
        if not enrollment:
            return Response("No tiene matrícula activa", status=404)
        return Response(self.get_serializer(enrollment).data)
