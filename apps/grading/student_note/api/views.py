from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework import status

from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.utils import ok_response, error_response
from apps.grading.api.base import BaseGradingViewSet

from ..application.serializers import (
    StudentNoteSerializer,
    GradeChangeHistorySerializer,
    PeriodGradeSummarySerializer,
    AnnualGradeSummarySerializer,
)
from ..domain.services import StudentNoteService, GradeCalculationService
from ..domain.replication import StudentNoteReplicationService
from ..infrastructure.repositories import (
    StudentNoteRepository,
    PeriodGradeSummaryRepository,
    AnnualGradeSummaryRepository,
)
from ..permissions import (
    ACTION_PERMISSIONS,
    GRADE_HISTORY_PERMISSIONS,
    GRADE_SUMMARY_PERMISSIONS,
    ANNUAL_GRADE_SUMMARY_PERMISSIONS,
)


@extend_schema_view(
    list=extend_schema(summary="Listar notas de estudiantes", tags=["grading"]),
    get=extend_schema(summary="Obtener nota de estudiante", tags=["grading"]),
    create=extend_schema(summary="Crear nota de estudiante", tags=["grading"]),
    update=extend_schema(summary="Actualizar nota de estudiante", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar nota parcialmente", tags=["grading"]
    ),
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
        qs = StudentNoteRepository.get_all(active_only=False).select_related(
            "evaluative_activity__activity_type",
            "evaluative_activity__teacher_subject_section__subject_offering__subject_academic_config__subject",
            "evaluative_activity__teacher_subject_section__subject_offering__section",
            "evaluative_activity__block_component__evaluation_block__academic_period",
        )
        return scope_student_to_enrollment(self.request, qs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = StudentNoteService.create_student_note(
                enrollment_id=data["enrollment"].id,
                evaluative_activity_id=data["evaluative_activity"].id,
                numeric_score=data.get("numeric_score"),
                qualitative_scale_id=(
                    data.get("qualitative_scale").id
                    if data.get("qualitative_scale")
                    else None
                ),
                teacher_observation=data.get("teacher_observation", ""),
                user_id=(
                    self.request.user.id if self.request.user.is_authenticated else None
                ),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        kwargs = {}
        for field in (
            "numeric_score",
            "teacher_observation",
            "grading_mode",
            "manually_overridden",
        ):
            if field in data:
                kwargs[field] = data[field]
        if "qualitative_scale" in data:
            scale = data["qualitative_scale"]
            kwargs["qualitative_scale_id"] = scale.id if scale else None
        try:
            obj = StudentNoteService.update_student_note(
                note_id=serializer.instance.id,
                user_id=(
                    self.request.user.id if self.request.user.is_authenticated else None
                ),
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

    @extend_schema(
        summary="Obtener/guardar notas por actividad",
        description="GET: devuelve estudiantes + notas existentes para una actividad. POST: guarda notas en lote.",
        tags=["grading"],
    )
    @action(detail=False, methods=["get", "post"], url_path="take-by-activity")
    def take_by_activity(self, request):
        if request.method == "GET":
            return self._take_by_activity_get(request)
        return self._take_by_activity_post(request)

    def _take_by_activity_get(self, request):
        evaluative_activity_id = request.query_params.get("evaluative_activity_id")
        teacher_subject_section_id = request.query_params.get(
            "teacher_subject_section_id"
        )
        if not evaluative_activity_id or not teacher_subject_section_id:
            return error_response(
                "evaluative_activity_id y teacher_subject_section_id son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            evaluative_activity_id = int(evaluative_activity_id)
            teacher_subject_section_id = int(teacher_subject_section_id)
        except (TypeError, ValueError):
            return error_response(
                "evaluative_activity_id y teacher_subject_section_id deben ser numericos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        activity, students_data = StudentNoteRepository.get_students_for_activity(
            evaluative_activity_id,
            teacher_subject_section_id,
        )
        if activity is None:
            return error_response(
                "Actividad evaluativa no encontrada",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        students_result = []
        for sd in students_data:
            note_data = (
                StudentNoteSerializer(sd["note_obj"]).data if sd["note_obj"] else None
            )
            students_result.append(
                {
                    "enrollment_id": sd["enrollment_id"],
                    "student_id": sd["student_id"],
                    "student_name": sd["student_name"],
                    "note": note_data,
                }
            )

        period = activity.block_component.evaluation_block.academic_period

        return ok_response(
            {
                "evaluative_activity": {
                    "id": activity.id,
                    "title": activity.title,
                    "max_score": str(activity.max_score),
                    "due_date": activity.due_date.isoformat(),
                },
                "academic_period": {
                    "id": period.id,
                    "name": period.name,
                    "start_date": period.start_date.isoformat(),
                    "end_date": period.end_date.isoformat(),
                    "grades_locked": period.grades_locked,
                },
                "students": students_result,
            }
        )

    def _take_by_activity_post(self, request):
        try:
            evaluative_activity_id = int(request.data.get("evaluative_activity_id"))
            teacher_subject_section_id = int(
                request.data.get("teacher_subject_section_id")
            )
        except (TypeError, ValueError):
            return error_response(
                "evaluative_activity_id y teacher_subject_section_id son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        records = request.data.get("records", [])
        if not records:
            return error_response(
                "records es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        errors = []
        for i, rec in enumerate(records):
            try:
                raw_score = rec.get("numeric_score")
                numeric_score = (
                    Decimal(str(raw_score)) if raw_score is not None else None
                )
                note = StudentNoteService.create_student_note(
                    enrollment_id=int(rec.get("enrollment")),
                    evaluative_activity_id=evaluative_activity_id,
                    numeric_score=numeric_score,
                    teacher_observation=rec.get("teacher_observation", ""),
                    user_id=request.user.id if request.user.is_authenticated else None,
                )
                results.append(StudentNoteSerializer(note).data)
            except ValueError as e:
                detail = e.args[0] if e.args else str(e)
                if isinstance(detail, dict):
                    detail = "; ".join(f"{k}: {v}" for k, v in detail.items())
                errors.append({"index": i, "error": str(detail), "record": rec})

        if errors:
            return ok_response(
                {"created": results, "errors": errors},
                msg="Algunos registros no pudieron procesarse",
            )
        return ok_response(results, msg=f"{len(results)} registros procesados")

    @extend_schema(
        summary="Replicar notas de estudiante (push)",
        tags=["grading"],
    )
    @action(detail=False, methods=["post"], url_path="replicate/push")
    def replicate_push(self, request):
        documents = request.data.get("documents", [])
        if not documents:
            return error_response(
                "documents es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        results = StudentNoteReplicationService.apply_batch(documents)
        applied = sum(1 for r in results if r.get("status") == "APPLIED")
        conflicts = sum(1 for r in results if r.get("status") == "CONFLICT")
        return ok_response(
            {"results": results, "applied": applied, "conflicts": conflicts},
            msg=f"{applied} aplicado(s), {conflicts} conflicto(s)",
        )

    @extend_schema(
        summary="Cambios de notas desde timestamp (pull)",
        tags=["grading"],
    )
    @action(detail=False, methods=["get"], url_path="replicate/changes")
    def replicate_changes(self, request):
        since = request.query_params.get("since")
        activity_id = request.query_params.get("evaluative_activity_id")
        if not activity_id:
            return error_response(
                "evaluative_activity_id es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        changes = StudentNoteReplicationService.get_changes(
            since=since,
            evaluative_activity_id=int(activity_id),
        )
        return ok_response({"count": len(changes), "since": since, "results": changes})


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

        return (
            GradeChangeHistory.objects.select_related(
                "student_note", "modified_by_user__person"
            )
            .all()
            .order_by("-modified_at")
        )


@extend_schema_view(
    list=extend_schema(summary="Listar res\u00famenes de notas", tags=["grading"]),
    get=extend_schema(summary="Obtener resumen de notas", tags=["grading"]),
    create=extend_schema(summary="Crear resumen de notas", tags=["grading"]),
    update=extend_schema(summary="Actualizar resumen de notas", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar resumen parcialmente", tags=["grading"]
    ),
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
        qs = PeriodGradeSummaryRepository.get_all(active_only=False)
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
            subject_offering=data.get("subject_offering")
            or serializer.instance.subject_offering,
            academic_period=data.get("academic_period")
            or serializer.instance.academic_period,
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
                "required": [
                    "enrollment_id",
                    "subject_offering_id",
                    "academic_period_id",
                ],
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
                {
                    "error": "enrollment_id, subject_offering_id y academic_period_id son requeridos"
                },
                msg="Error",
                status_code=400,
            )

        task = recompute_period_grade_summary_task.delay(
            enrollment_id, offering_id, period_id
        )
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
            return ok_response(
                {"error": "academic_period_id es requerido"},
                msg="Error",
                status_code=400,
            )

        if not AcademicPeriodRepository.get_by_id(period_id):
            return ok_response(
                {"error": "academic_period_id no existe"}, msg="Error", status_code=404
            )

        ids = GradeCalculationService.calculate_all_for_period(period_id)
        return ok_response(
            {"status": "OK", "summaries_calculated": len(ids), "ids": ids},
            status_code=202,
        )


@extend_schema_view(
    list=extend_schema(summary="Listar res\u00famenes anuales", tags=["grading"]),
    get=extend_schema(summary="Obtener resumen anual", tags=["grading"]),
    create=extend_schema(summary="Crear resumen anual", tags=["grading"]),
    update=extend_schema(summary="Actualizar resumen anual", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar resumen anual parcialmente", tags=["grading"]
    ),
)
class AnnualGradeSummaryViewSet(BaseGradingViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    serializer_class = AnnualGradeSummarySerializer
    action_permissions = ANNUAL_GRADE_SUMMARY_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["enrollment", "school_year"]
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = ["annual_final_avg", "calculated_at"]
    ordering = ["-id"]

    def get_queryset(self):
        qs = AnnualGradeSummaryRepository.get_all(active_only=False)
        return scope_student_to_enrollment(self.request, qs)

    @extend_schema(
        summary="Recalcular todos los res\u00famenes anuales de un año escolar",
        tags=["grading"],
        request={
            "application/json": {
                "type": "object",
                "properties": {"school_year_id": {"type": "integer"}},
                "required": ["school_year_id"],
            }
        },
        responses={202: {"type": "object"}},
    )
    @action(detail=False, methods=["post"], url_path="recalculate-school-year")
    def recalculate_school_year(self, request):
        from ..tasks import calculate_annual_grade_summaries_task

        try:
            school_year_id = int(request.data.get("school_year_id"))
        except (TypeError, ValueError):
            return ok_response(
                {"error": "school_year_id es requerido"},
                msg="Error",
                status_code=400,
            )

        task = calculate_annual_grade_summaries_task.delay(school_year_id)
        return ok_response({"task_id": task.id, "status": "PENDING"}, status_code=202)

    @extend_schema(
        summary="Reporte anual consolidado por estudiante",
        description="Retorna todas las materias con su promedio anual y si el estudiante perdi\u00f3 el año",
        tags=["grading"],
        responses={200: {"type": "object"}},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="student-report/(?P<enrollment_id>[^/.]+)",
    )
    def student_report(self, request, enrollment_id=None):
        school_year_id = request.query_params.get("school_year_id")

        summaries = AnnualGradeSummaryRepository.get_by_enrollment(enrollment_id)

        if school_year_id:
            summaries = [
                s for s in summaries if s.school_year_id == int(school_year_id)
            ]

        if not summaries:
            return ok_response(
                {
                    "enrollment_id": int(enrollment_id) if enrollment_id else None,
                    "school_year_id": int(school_year_id) if school_year_id else None,
                    "year_failed": False,
                    "subjects": [],
                }
            )

        has_failing = any(s.is_failing for s in summaries)
        school_year_name = summaries[0].school_year_name if summaries else None

        subjects = []
        for s in summaries:
            subject = s.subject_offering.subject_academic_config.subject
            subjects.append(
                {
                    "subject_code": subject.code,
                    "subject_name": subject.name,
                    "annual_final_avg": str(s.annual_final_avg),
                    "is_failing": s.is_failing,
                    "promotion_status": s.promotion_status,
                    "is_finalized": s.is_finalized,
                }
            )

        return ok_response(
            {
                "enrollment_id": int(enrollment_id),
                "school_year_id": (
                    int(school_year_id)
                    if school_year_id
                    else summaries[0].school_year_id
                ),
                "school_year_name": school_year_name,
                "year_failed": has_failing,
                "subjects": subjects,
            }
        )
