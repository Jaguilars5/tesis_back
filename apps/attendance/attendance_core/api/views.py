from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.attendance.api.base import BaseAttendanceViewSet
from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.utils.responses import ok_response, error_response
from apps.institutions.school_year.infrastructure.repositories import SchoolYearRepository

from ..application.serializers import AttendanceSerializer
from ..domain.replication import AttendanceReplicationService
from ..domain.services import AttendanceService
from ..infrastructure.repositories import AttendanceRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AttendanceFilter


def _format_record_error(exc):
    """Convierte la excepción de un registro en un mensaje legible.

    `create_attendance` lanza `ValueError(dict_de_errores)`; aquí lo
    aplanamos a un texto entendible para el usuario final.
    """
    detail = exc.args[0] if getattr(exc, "args", None) else str(exc)
    if isinstance(detail, dict):
        return "; ".join(f"{field}: {msg}" for field, msg in detail.items())
    return str(detail)


@extend_schema_view(
    list=extend_schema(summary="Listar asistencias", tags=["attendance"]),
    get=extend_schema(summary="Obtener asistencia", tags=["attendance"]),
    create=extend_schema(summary="Registrar asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar asistencia parcialmente", tags=["attendance"]),
)
class AttendanceViewSet(BaseAttendanceViewSet):
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    serializer_class = AttendanceSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AttendanceFilter
    search_fields = ["enrollment__student__user__person__names", "observation"]
    ordering_fields = ["attendance_date", "created_at"]
    ordering = ["-attendance_date"]

    def get_queryset(self):
        qs = AttendanceRepository.get_all(active_only=False)
        qs = scope_student_to_enrollment(self.request, qs)
        return qs

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = AttendanceService.create_attendance(
                enrollment_id=data["enrollment"].id,
                teacher_subject_section_id=data["teacher_subject_section"].id,
                academic_period_id=data["academic_period"].id,
                attendance_date=data["attendance_date"],
                attendance_status_id=data["attendance_status"].id,
                absence_type_id=data.get("absence_type").id if data.get("absence_type") else None,
                observation=data.get("observation", ""),
                device_origin=data.get("device_origin"),
                class_schedule_id=data.get("class_schedule").id if data.get("class_schedule") else None,
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = AttendanceService.update_attendance(
                attendance_id=serializer.instance.id,
                academic_period_id=data.get("academic_period").id if data.get("academic_period") else None,
                attendance_status_id=data.get("attendance_status").id if data.get("attendance_status") else None,
                absence_type_id=data.get("absence_type").id if data.get("absence_type") else None,
                observation=data.get("observation", ""),
                device_origin=data.get("device_origin"),
                class_schedule_id=data.get("class_schedule").id if data.get("class_schedule") else None,
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @extend_schema(
        summary="Tomar asistencia por horario",
        description="Obtener o registrar asistencia vinculada a un bloque horario específico.",
        tags=["attendance"],
    )
    @action(detail=False, methods=["get", "post"])
    def take_by_schedule(self, request):
        if request.method == "GET":
            return self._take_by_schedule_get(request)
        return self._take_by_schedule_post(request)

    @extend_schema(
        summary="Sesión de asistencia (lista unificada)",
        description=(
            "Devuelve la lista de estudiantes de la sección con su registro de "
            "asistencia para un bloque horario, materia y período. Endpoint "
            "pensado para clientes móviles (una sola petición)."
        ),
        tags=["attendance"],
    )
    @action(detail=False, methods=["get"], url_path="session")
    def session(self, request):
        tss_id = request.query_params.get("teacher_subject_section")
        period_id = request.query_params.get("academic_period")
        date_str = request.query_params.get("date")
        class_schedule_id = request.query_params.get("class_schedule_id")

        missing = [
            name
            for name, value in (
                ("teacher_subject_section", tss_id),
                ("academic_period", period_id),
                ("date", date_str),
                ("class_schedule_id", class_schedule_id),
            )
            if not value
        ]
        if missing:
            return error_response(
                f"Parámetros requeridos: {', '.join(missing)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return error_response(
                "Formato de fecha inválido. Use YYYY-MM-DD",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        tss, cs, students_data = AttendanceRepository.get_students_for_session(
            teacher_subject_section_id=int(tss_id),
            academic_period_id=int(period_id),
            attendance_date=attendance_date,
            class_schedule_id=int(class_schedule_id),
        )

        if tss is None:
            return error_response(
                "Materia-sección no encontrada",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if cs is None:
            return error_response(
                "Horario no encontrado o no pertenece a la materia-sección",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        students_result = []
        for sd in students_data:
            att_data = (
                AttendanceSerializer(sd["attendance_obj"]).data
                if sd["attendance_obj"]
                else None
            )
            students_result.append({
                "enrollment_id": sd["enrollment_id"],
                "student_id": sd["student_id"],
                "student_name": sd["student_name"],
                "attendance": att_data,
            })

        return ok_response({
            "teacher_subject_section": {
                "id": tss.id,
                "name": str(tss),
            },
            "academic_period": int(period_id),
            "class_schedule": {
                "id": cs.id,
                "day_of_week": cs.day_of_week,
                "start_time": str(cs.start_time) if cs.start_time else None,
                "end_time": str(cs.end_time) if cs.end_time else None,
            },
            "date": date_str,
            "students": students_result,
        })

    def _take_by_schedule_get(self, request):
        class_schedule_id = request.query_params.get("class_schedule_id")
        date_str = request.query_params.get("date")
        if not class_schedule_id or not date_str:
            return error_response(
                "class_schedule_id y date son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return error_response(
                "Formato de fecha inválido. Use YYYY-MM-DD",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        cs, students_data = AttendanceRepository.get_students_for_schedule(
            class_schedule_id, attendance_date
        )
        if cs is None:
            return error_response(
                "Horario no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        students_result = []
        for sd in students_data:
            att_data = AttendanceSerializer(sd["attendance_obj"]).data if sd["attendance_obj"] else None
            students_result.append({
                "enrollment_id": sd["enrollment_id"],
                "student_id": sd["student_id"],
                "student_name": sd["student_name"],
                "attendance": att_data,
            })

        return ok_response({
            "class_schedule": {
                "id": cs.id,
                "day_of_week": cs.day_of_week,
                "start_time": str(cs.start_time) if cs.start_time else None,
                "end_time": str(cs.end_time) if cs.end_time else None,
            },
            "date": date_str,
            "students": students_result,
        })

    def _take_by_schedule_post(self, request):
        class_schedule_id = request.data.get("class_schedule_id")
        date_str = request.data.get("date")
        academic_period_id = request.data.get("academic_period")
        teacher_subject_section_id = request.data.get("teacher_subject_section")
        records = request.data.get("records", [])

        if not all([class_schedule_id, date_str, academic_period_id, teacher_subject_section_id, records]):
            return error_response(
                "class_schedule_id, date, academic_period, teacher_subject_section y records son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return error_response(
                "Formato de fecha inválido. Use YYYY-MM-DD",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        errors = []
        for i, rec in enumerate(records):
            try:
                attendance = AttendanceService.create_attendance(
                    enrollment_id=rec.get("enrollment"),
                    teacher_subject_section_id=teacher_subject_section_id,
                    academic_period_id=academic_period_id,
                    attendance_date=attendance_date,
                    attendance_status_id=rec.get("attendance_status"),
                    absence_type_id=rec.get("absence_type"),
                    observation=rec.get("observation", ""),
                    class_schedule_id=class_schedule_id,
                )
                results.append(AttendanceSerializer(attendance).data)
            except Exception as e:
                errors.append({"index": i, "error": _format_record_error(e), "record": rec})

        if errors:
            return ok_response(
                {"created": results, "errors": errors},
                msg="Algunos registros no pudieron procesarse",
            )
        return ok_response(results, msg=f"{len(results)} registros procesados")

    @extend_schema(
        summary="Replicar documentos de asistencia (push)",
        description=(
            "Protocolo documental: cada ítem incluye uuid y base_rev (revisión base). "
            "Si base_rev coincide con sync_version del servidor, se aplica y rev aumenta. "
            "Si no, status=CONFLICT con el documento actual del servidor."
        ),
        tags=["attendance"],
    )
    @action(detail=False, methods=["post"], url_path="replicate/push")
    def replicate_push(self, request):
        documents = request.data.get("documents", [])
        if not documents:
            return error_response(
                "documents es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        results = AttendanceReplicationService.apply_batch(documents)
        applied = sum(1 for r in results if r.get("status") == "APPLIED")
        conflicts = sum(1 for r in results if r.get("status") == "CONFLICT")
        return ok_response(
            {
                "results": results,
                "applied": applied,
                "conflicts": conflicts,
            },
            msg=f"{applied} aplicado(s), {conflicts} conflicto(s)",
        )

    @extend_schema(
        summary="Cambios de asistencia desde timestamp (pull)",
        description="Devuelve documentos de asistencia modificados desde ``since`` (ISO 8601).",
        tags=["attendance"],
    )
    @action(detail=False, methods=["get"], url_path="replicate/changes")
    def replicate_changes(self, request):
        tss_id = request.query_params.get("teacher_subject_section")
        period_id = request.query_params.get("academic_period")
        class_schedule_id = request.query_params.get("class_schedule_id")
        since = request.query_params.get("since")

        missing = [
            name
            for name, value in (
                ("teacher_subject_section", tss_id),
                ("academic_period", period_id),
                ("class_schedule_id", class_schedule_id),
            )
            if not value
        ]
        if missing:
            return error_response(
                f"Parámetros requeridos: {', '.join(missing)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        changes = AttendanceReplicationService.get_changes(
            since=since,
            teacher_subject_section_id=int(tss_id),
            academic_period_id=int(period_id),
            class_schedule_id=int(class_schedule_id),
        )
        return ok_response(
            {
                "count": len(changes),
                "since": since,
                "results": changes,
            }
        )

    @extend_schema(
        summary="Resumen de asistencia",
        description="Devuelve conteos agregados de asistencia (total, presentes, ausentes, tardanzas, justificados). Por defecto filtra por el año lectivo activo. Soporta los mismos filtros que el listado (academic_period, teacher_subject_section, attendance_date_after, attendance_date_before, etc.).",
        tags=["attendance"],
    )
    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()

        academic_period = request.query_params.get("academic_period")
        if not academic_period:
            current_sy = SchoolYearRepository.get_current()
            if current_sy:
                period_ids = list(
                    AcademicPeriod.objects.filter(
                        school_year=current_sy, is_active=True
                    ).values_list("id", flat=True)
                )
                if period_ids:
                    qs = qs.filter(academic_period_id__in=period_ids)

        qs = self.filter_queryset(qs)
        data = AttendanceRepository.get_summary(qs)
        return ok_response(data)

    @extend_schema(
        summary="Crear/actualizar asistencias en lote",
        description="Crea o actualiza múltiples registros de asistencia en una sola transacción.",
        tags=["attendance"],
    )
    @action(detail=False, methods=["post"], url_path="batch")
    def batch_create(self, request):
        records = request.data.get("records", [])
        if not records:
            return error_response("No se enviaron registros", status_code=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []
        for i, rec in enumerate(records):
            try:
                attendance_date = rec.get("attendance_date")
                if isinstance(attendance_date, str):
                    try:
                        attendance_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()
                    except ValueError:
                        raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")

                attendance = AttendanceService.create_attendance(
                    enrollment_id=rec.get("enrollment"),
                    teacher_subject_section_id=rec.get("teacher_subject_section"),
                    academic_period_id=rec.get("academic_period"),
                    attendance_date=attendance_date,
                    attendance_status_id=rec.get("attendance_status"),
                    absence_type_id=rec.get("absence_type"),
                    observation=rec.get("observation", ""),
                    class_schedule_id=rec.get("class_schedule"),
                )
                results.append(AttendanceSerializer(attendance).data)
            except Exception as e:
                errors.append({"index": i, "error": _format_record_error(e), "record": rec})

        if errors:
            return ok_response({"created": results, "errors": errors}, msg="Algunos registros no pudieron procesarse")

        return ok_response(results, msg=f"{len(results)} registros procesados")
