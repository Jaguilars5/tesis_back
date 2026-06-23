from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    AbsenceTypeSerializer,
    AttendanceSerializer,
    AttendanceStatusSerializer,
)
from ..repositories import (
    AbsenceTypeRepository,
    AttendanceRepository,
    AttendanceStatusRepository,
)
from ..services.attendance_service import AttendanceService
from apps.academic.api.serializers import ClassScheduleSerializer
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.constants.permissions import attendance as perm
from apps.core.utils.responses import ok_response, error_response


@extend_schema_view(
    list=extend_schema(summary="Listar asistencias", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener asistencia", tags=["attendance"]),
    create=extend_schema(summary="Registrar asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar asistencia parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar asistencia", tags=["attendance"]),
)
class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ATTENDANCE,
        "retrieve": perm.VIEW_ATTENDANCE,
        "create": perm.CREATE_ATTENDANCE,
        "update": perm.UPDATE_ATTENDANCE,
        "partial_update": perm.UPDATE_ATTENDANCE,
        "destroy": perm.DELETE_ATTENDANCE,
        "batch_create": perm.CREATE_ATTENDANCE,
        "take_by_schedule": perm.CREATE_ATTENDANCE,
    }

    def get_queryset(self):
        qs = AttendanceRepository.get_all()
        qs = scope_student_to_enrollment(self.request, qs)
        enrollment = self.request.query_params.get("enrollment")
        tss = self.request.query_params.get("teacher_subject_section")
        date = self.request.query_params.get("attendance_date")
        period = self.request.query_params.get("academic_period")
        if enrollment:
            qs = qs.filter(enrollment_id=enrollment)
        if tss:
            qs = qs.filter(teacher_subject_section_id=tss)
        if date:
            qs = qs.filter(attendance_date=date)
        if period:
            qs = qs.filter(academic_period_id=period)
        return qs

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

    def _take_by_schedule_get(self, request):
        class_schedule_id = request.query_params.get("class_schedule_id")
        date_str = request.query_params.get("date")
        if not class_schedule_id or not date_str:
            return error_response(
                "class_schedule_id y date son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        from datetime import datetime
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

        schedule_serializer = ClassScheduleSerializer(cs)
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
            "class_schedule": schedule_serializer.data,
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
        from datetime import datetime
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
                errors.append({"index": i, "error": str(e), "record": rec})

        if errors:
            return ok_response(
                {"created": results, "errors": errors},
                msg="Algunos registros no pudieron procesarse",
            )
        return ok_response(results, msg=f"{len(results)} registros procesados")

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
                attendance = AttendanceService.create_attendance(
                    enrollment_id=rec.get("enrollment"),
                    teacher_subject_section_id=rec.get("teacher_subject_section"),
                    academic_period_id=rec.get("academic_period"),
                    attendance_date=rec.get("attendance_date"),
                    attendance_status_id=rec.get("attendance_status"),
                    absence_type_id=rec.get("absence_type"),
                    observation=rec.get("observation", ""),
                )
                results.append(AttendanceSerializer(attendance).data)
            except Exception as e:
                errors.append({"index": i, "error": str(e), "record": rec})

        if errors:
            return ok_response({"created": results, "errors": errors}, msg="Algunos registros no pudieron procesarse")

        return ok_response(results, msg=f"{len(results)} registros procesados")


@extend_schema_view(
    list=extend_schema(summary="Listar estados de asistencia", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener estado de asistencia", tags=["attendance"]),
    create=extend_schema(summary="Crear estado de asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar estado de asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar estado parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar estado de asistencia", tags=["attendance"]),
)
class AttendanceStatusViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceStatusSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ATTENDANCE_STATUS,
        "retrieve": perm.VIEW_ATTENDANCE_STATUS,
        "create": perm.CREATE_ATTENDANCE_STATUS,
        "update": perm.UPDATE_ATTENDANCE_STATUS,
        "partial_update": perm.UPDATE_ATTENDANCE_STATUS,
        "destroy": perm.DELETE_ATTENDANCE_STATUS,
    }

    def get_queryset(self):
        return AttendanceStatusRepository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de ausencia", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener tipo de ausencia", tags=["attendance"]),
    create=extend_schema(summary="Crear tipo de ausencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar tipo de ausencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar tipo de ausencia parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar tipo de ausencia", tags=["attendance"]),
)
class AbsenceTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AbsenceTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ABSENCE_TYPE,
        "retrieve": perm.VIEW_ABSENCE_TYPE,
        "create": perm.CREATE_ABSENCE_TYPE,
        "update": perm.UPDATE_ABSENCE_TYPE,
        "partial_update": perm.UPDATE_ABSENCE_TYPE,
        "destroy": perm.DELETE_ABSENCE_TYPE,
    }

    def get_queryset(self):
        return AbsenceTypeRepository.get_all()
