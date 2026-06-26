from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.utils import ok_response
from apps.grading.api.base import BaseGradingViewSet

from ..application.serializers import (
    StudentNoteSerializer,
    GradeChangeHistorySerializer,
    PeriodGradeSummarySerializer,
)
from ..domain.services import StudentNoteService, GradeCalculationService
from ..infrastructure.repositories import (
    StudentNoteRepository,
    PeriodGradeSummaryRepository,
)
from ..permissions import ACTION_PERMISSIONS, GRADE_HISTORY_PERMISSIONS, GRADE_SUMMARY_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar notas de estudiantes", tags=["grading"]),
    get=extend_schema(summary="Obtener nota de estudiante", tags=["grading"]),
    create=extend_schema(summary="Crear nota de estudiante", tags=["grading"]),
    update=extend_schema(summary="Actualizar nota de estudiante", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar nota parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar nota de estudiante", tags=["grading"]),
    anular=extend_schema(summary="Anular nota de estudiante", tags=["grading"]),
)
class StudentNoteViewSet(BaseGradingViewSet):
    serializer_class = StudentNoteSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["enrollment", "evaluative_activity"]
    search_fields = ["enrollment__student__user__person__names", "teacher_observation"]
    ordering_fields = ["numeric_score", "created_at"]
    ordering = ["-id"]

    def get_queryset(self):
        qs = StudentNoteRepository.get_all()
        return scope_student_to_enrollment(self.request, qs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = StudentNoteService.create_student_note(
                enrollment_id=data["enrollment"].id,
                evaluative_activity_id=data["evaluative_activity"].id,
                numeric_score=data.get("numeric_score"),
                qualitative_scale_id=data.get("qualitative_scale").id if data.get("qualitative_scale") else None,
                teacher_observation=data.get("teacher_observation", ""),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        kwargs = {}
        for field in ("numeric_score", "teacher_observation", "grading_mode", "manually_overridden"):
            if field in data:
                kwargs[field] = data[field]
        if "qualitative_scale" in data:
            scale = data["qualitative_scale"]
            kwargs["qualitative_scale_id"] = scale.id if scale else None
        try:
            obj = StudentNoteService.update_student_note(
                note_id=serializer.instance.id,
                **kwargs,
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @action(detail=True, methods=["post"], url_path="anular")
    def anular(self, request, pk=None):
        """
        Anula una nota marcándola como manualmente anulada.

        POST /api/grading/student-notes/{id}/anular/
        Body: {"reason": "Razón de la anulación"}
        """
        reason = request.data.get("reason", "")
        try:
            note = StudentNoteService.anular_nota(
                note_id=pk,
                user_id=request.user.id,
                reason=reason,
            )
            return ok_response(
                StudentNoteSerializer(note).data,
                msg="Nota anulada exitosamente",
            )
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))


@extend_schema_view(
    list=extend_schema(summary="Listar historial de cambios", tags=["grading"]),
    get=extend_schema(summary="Obtener cambio de nota", tags=["grading"]),
)
class GradeChangeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeChangeHistorySerializer
    action_permissions = GRADE_HISTORY_PERMISSIONS
    permission_classes = BaseGradingViewSet.permission_classes
    pagination_class = BaseGradingViewSet.pagination_class
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    ordering = ["-modified_at"]

    def get_queryset(self):
        from ..infrastructure.models import GradeChangeHistory
        return GradeChangeHistory.objects.select_related(
            "student_note", "modified_by_user__person"
        ).all().order_by("-modified_at")


@extend_schema_view(
    list=extend_schema(summary="Listar res\u00famenes de notas", tags=["grading"]),
    get=extend_schema(summary="Obtener resumen de notas", tags=["grading"]),
    create=extend_schema(summary="Crear resumen de notas", tags=["grading"]),
    update=extend_schema(summary="Actualizar resumen de notas", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar resumen parcialmente", tags=["grading"]),
)
class PeriodGradeSummaryViewSet(BaseGradingViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    serializer_class = PeriodGradeSummarySerializer
    action_permissions = GRADE_SUMMARY_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["enrollment", "academic_period"]
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = ["final_avg_truncated", "created_at"]
    ordering = ["-id"]

    def get_queryset(self):
        qs = PeriodGradeSummaryRepository.get_all()
        return scope_student_to_enrollment(self.request, qs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = GradeCalculationService.calculate_period_summary(
            enrollment=data["enrollment"],
            subject_offering=data["subject_offering"],
            academic_period=data["academic_period"],
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = serializer.validated_data
        obj = GradeCalculationService.calculate_period_summary(
            enrollment=data.get("enrollment") or serializer.instance.enrollment,
            subject_offering=data.get("subject_offering") or serializer.instance.subject_offering,
            academic_period=data.get("academic_period") or serializer.instance.academic_period,
        )
        serializer.instance = obj

    @extend_schema(
        summary="Recalcular un resumen de notas",
        tags=["grading"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "enrollment_id": {"type": "integer"},
                    "subject_offering_id": {"type": "integer"},
                    "academic_period_id": {"type": "integer"},
                },
                "required": ["enrollment_id", "subject_offering_id", "academic_period_id"],
            }
        },
        responses={202: {"type": "object"}},
    )
    @action(detail=False, methods=["post"], url_path="recalculate")
    def recalculate(self, request):
        from ..tasks import recompute_period_grade_summary_task

        try:
            enrollment_id = int(request.data.get("enrollment_id"))
            offering_id = int(request.data.get("subject_offering_id"))
            period_id = int(request.data.get("academic_period_id"))
        except (TypeError, ValueError):
            return ok_response(
                {"error": "enrollment_id, subject_offering_id y academic_period_id son requeridos"},
                msg="Error", status_code=400,
            )

        task = recompute_period_grade_summary_task.delay(enrollment_id, offering_id, period_id)
        return ok_response({"task_id": task.id, "status": "PENDING"}, status_code=202)

    @extend_schema(
        summary="Recalcular todos los res\u00famenes de un periodo",
        tags=["grading"],
        request={
            "application/json": {
                "type": "object",
                "properties": {"academic_period_id": {"type": "integer"}},
                "required": ["academic_period_id"],
            }
        },
        responses={202: {"type": "object"}},
    )
    @action(detail=False, methods=["post"], url_path="recalculate-period")
    def recalculate_period(self, request):
        from apps.academic.academic_period.infrastructure.repositories import (
            AcademicPeriodRepository,
        )

        try:
            period_id = int(request.data.get("academic_period_id"))
        except (TypeError, ValueError):
            return ok_response({"error": "academic_period_id es requerido"}, msg="Error", status_code=400)

        if not AcademicPeriodRepository.get_by_id(period_id):
            return ok_response({"error": "academic_period_id no existe"}, msg="Error", status_code=404)

        ids = GradeCalculationService.calculate_all_for_period(period_id)
        return ok_response(
            {"status": "OK", "summaries_calculated": len(ids), "ids": ids},
            status_code=202,
        )
