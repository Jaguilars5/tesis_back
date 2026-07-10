from django.db import models
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission
from apps.core.utils import ok_response, error_response

from ..domain.services import EnrollmentService, StudentService
from ..infrastructure.repositories import (
    EnrollmentRepository,
    StudentRepository,
    StudentRepresentativeRepository,
)
from ..infrastructure.models import Kinship, StudentRepresentative
from ..application.serializers import (
    EnrollmentCreateSerializer,
    EnrollmentSerializer,
    KinshipSerializer,
    SpecialNeedsTypeSerializer,
    StudentCreateSerializer,
    StudentSerializer,
    StudentDetailSerializer,
    StudentRepresentativeSerializer,
)
from .base import BaseStudentsViewSet
from ..permissions import ACTION_PERMISSIONS
from .filters.student import StudentFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar estudiantes", tags=["students"]),
    get=extend_schema(summary="Obtener estudiante", tags=["students"]),
    create=extend_schema(summary="Crear estudiante", tags=["students"]),
    update=extend_schema(summary="Actualizar estudiante", tags=["students"]),
    partial_update=extend_schema(
        summary="Actualizar estudiante parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Desactivar estudiante", tags=["students"]),
    by_section=extend_schema(summary="Estudiantes por secci\u00f3n", tags=["students"]),
    search=extend_schema(summary="Buscar estudiantes", tags=["students"]),
    representatives=extend_schema(
        summary="Representantes del estudiante", tags=["students"]
    ),
    assign_representative=extend_schema(
        summary="Asignar representante al estudiante", tags=["students"]
    ),
)
class StudentViewSet(BaseStudentsViewSet):
    serializer_class = StudentSerializer
    action_permissions = ACTION_PERMISSIONS["student"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = [
        "user__person__names",
        "user__person__last_names",
        "user__person__document_number",
        "student_code",
    ]
    ordering_fields = ["user__person__last_names", "is_active"]
    ordering = ["user__person__last_names"]

    def get_queryset(self):
        qs = StudentRepository.get_all().select_related(
            "user__person__parish__city",
            "user__person__document_type",
        )
        if self.action == "list":
            qs = qs.prefetch_related(
                models.Prefetch(
                    "representatives_set",
                    queryset=(
                        StudentRepresentative.objects.order_by("-is_primary", "-created_at")
                        .select_related("kinship", "user__person")
                    ),
                    to_attr="_primary_rep_cache",
                )
            )
        elif self.action == "get":
            qs = qs.prefetch_related(
                models.Prefetch(
                    "representatives_set",
                    queryset=StudentRepresentative.objects.select_related(
                        "kinship", "user__person"
                    ),
                    to_attr="_representatives_all",
                )
            )
        return qs

    def get_serializer_class(self):
        if self.action == "get":
            return StudentDetailSerializer
        elif self.action == "create":
            return StudentCreateSerializer
        return StudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            student = StudentService.create_student(
                document_number=serializer.validated_data["document_number"],
                names=serializer.validated_data["names"],
                last_names=serializer.validated_data["last_names"],
                birth_date=serializer.validated_data.get("birth_date"),
                email=serializer.validated_data.get("email", ""),
                phone=serializer.validated_data.get("phone", ""),
                document_type_id=serializer.validated_data.get("document_type"),
                parish_id=serializer.validated_data.get("parish"),
                has_special_needs=serializer.validated_data.get("has_special_needs", False),
                special_needs_type_id=serializer.validated_data.get("special_needs_type"),
            )
            out_serializer = StudentSerializer(student)
            return Response(out_serializer.data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    def perform_update(self, serializer):
        try:
            student = StudentService.update_student(
                serializer.instance.id,
                **serializer.validated_data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = student

    @action(detail=False, methods=["get"])
    def by_section(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return Response("section_id requerido", status=400)

        students = StudentService.list_students_by_section(section_id)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        if not query:
            return Response("Par\u00e1metro q requerido", status=400)

        students = StudentService.search_students(query)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def representatives(self, request, pk=None):
        relationships = StudentRepresentativeRepository.get_by_student(pk)
        serializer = StudentRepresentativeSerializer(relationships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="assign-representative")
    def assign_representative(self, request, pk=None):
        user_id = request.data.get("user_id")
        kinship = request.data.get("kinship", "Padre")
        kwargs = {
            "is_primary": request.data.get("is_primary", True),
            "emergency_contact": request.data.get("emergency_contact", False),
            "receives_notifications": request.data.get("receives_notifications", True),
        }
        try:
            if user_id:
                rel = StudentService.assign_representative(
                    pk, user_id, kinship, **kwargs
                )
            else:
                rel = StudentService.create_and_assign_representative(
                    student_id=pk,
                    kinship=kinship,
                    **kwargs,
                    document_number=request.data["document_number"],
                    names=request.data["names"],
                    last_names=request.data["last_names"],
                    email=request.data.get("email", ""),
                    phone=request.data.get("phone", ""),
                    birth_date=request.data.get("birth_date"),
                    document_type_id=request.data.get("document_type"),
                    parish_id=request.data.get("parish"),
                )
            serializer = StudentRepresentativeSerializer(rel)
            return Response(serializer.data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar representantes", tags=["students"]),
    get=extend_schema(summary="Obtener representante", tags=["students"]),
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
class StudentRepresentativeViewSet(BaseStudentsViewSet):
    serializer_class = StudentRepresentativeSerializer
    action_permissions = ACTION_PERMISSIONS["student_representative"]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["student", "user", "is_primary"]
    ordering_fields = ["created_at"]
    ordering = ["-is_primary", "created_at"]

    def get_queryset(self):
        return StudentRepresentativeRepository.get_all()

    def create(self, request, *args, **kwargs):
        try:
            relationship = StudentService.assign_representative(
                student_id=request.data.get("student"),
                user_id=request.data.get("user"),
                kinship=request.data.get("kinship", "Padre"),
                is_primary=request.data.get("is_primary", False),
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
        try:
            StudentService.set_primary_representative(
                student_id=request.data.get("student"),
                user_id=request.data.get("user"),
            )
            return Response({"status": "Principal actualizado"})
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["delete"])
    def unlink(self, request, pk=None):
        relationship = self.get_object()
        try:
            StudentService.remove_representative(
                student_id=relationship.student_id,
                user_id=relationship.user_id,
            )
            return Response({"unlinked": True})
        except ValueError as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar matr\u00edculas", tags=["students"]),
    get=extend_schema(summary="Obtener matr\u00edcula", tags=["students"]),
    create=extend_schema(summary="Crear matr\u00edcula", tags=["students"]),
    update=extend_schema(summary="Actualizar matr\u00edcula", tags=["students"]),
    partial_update=extend_schema(
        summary="Actualizar matr\u00edcula parcialmente", tags=["students"]
    ),
    destroy=extend_schema(summary="Eliminar matr\u00edcula", tags=["students"]),
    soft_delete=extend_schema(summary="Desactivar matr\u00edcula (soft delete)", tags=["students"]),
    withdraw=extend_schema(summary="Retirar estudiante", tags=["students"]),
    transfer=extend_schema(summary="Transferir estudiante", tags=["students"]),
    by_section=extend_schema(summary="Matr\u00edculas por secci\u00f3n", tags=["students"]),
    by_student=extend_schema(
        summary="Matr\u00edcula activa del estudiante", tags=["students"]
    ),
)
class EnrollmentViewSet(BaseStudentsViewSet):
    serializer_class = EnrollmentSerializer
    action_permissions = ACTION_PERMISSIONS["enrollment"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "student",
        "section",
        "enrollment_status",
    ]
    search_fields = [
        "student__person__names",
        "student__person__last_names",
        "student__student_code",
    ]
    ordering = ["-enrollment_date"]

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

    def update(self, request, *args, **kwargs):
        enrollment = self.get_object()
        serializer = self.get_serializer(enrollment, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        try:
            section = serializer.validated_data.get("section")
            enrollment_status = serializer.validated_data.get("enrollment_status")
            is_repeat = serializer.validated_data.get("is_repeat")
            EnrollmentService.update_enrollment(
                enrollment,
                section=section,
                enrollment_status=enrollment_status,
                is_repeat=is_repeat,
            )
            return Response(EnrollmentSerializer(enrollment).data)
        except ValueError as e:
            return Response(str(e), status=400)

    def partial_update(self, request, *args, **kwargs):
        enrollment = self.get_object()
        serializer = self.get_serializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            section = serializer.validated_data.get("section")
            enrollment_status = serializer.validated_data.get("enrollment_status")
            is_repeat = serializer.validated_data.get("is_repeat")
            EnrollmentService.update_enrollment(
                enrollment,
                section=section,
                enrollment_status=enrollment_status,
                is_repeat=is_repeat,
            )
            return Response(EnrollmentSerializer(enrollment).data)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        try:
            enrollment = self.get_object()
            result = EnrollmentService.soft_delete_enrollment(enrollment)
            return Response(result)
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
            return Response("No tiene matricula activa", status=404)
        return Response(self.get_serializer(enrollment).data)

    @action(detail=False, methods=["get"], url_path="by-representative")
    def by_representative(self, request):
        enrollments = EnrollmentRepository.get_by_representative(request.user)
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        enrollment = self.get_object()
        try:
            result = EnrollmentService.soft_delete_enrollment(enrollment)
            return ok_response(result, msg="Matr\u00edcula desactivada exitosamente")
        except ValueError as e:
            return error_response(str(e), status_code=400)


@extend_schema_view(
    list=extend_schema(summary="Listar necesidades especiales", tags=["students"]),
    retrieve=extend_schema(summary="Obtener necesidad especial", tags=["students"]),
)
class SpecialNeedsTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecialNeedsTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from ..infrastructure.models import SpecialNeedsType as SNT

        return SNT.objects.filter(is_active=True).order_by("name")


@extend_schema_view(
    list=extend_schema(summary="Listar parentescos", tags=["students"]),
    retrieve=extend_schema(summary="Obtener parentesco", tags=["students"]),
)
class KinshipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KinshipSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Kinship.objects.all()
    action_permissions = ACTION_PERMISSIONS["kinship"]
