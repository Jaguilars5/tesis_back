"""
ViewSet de API para dashboard y reportes analíticos.

No hereda de BaseAnalyticsViewSet porque es un ViewSet de acciones custom
(no CRUD estándar). Todas las respuestas usan ok_response/error_response.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.api.permissions import HasPermission
from apps.core.utils import ok_response, error_response

from ..permissions import DASHBOARD_ACTION_PERMISSIONS
from ..domain.services import (
    CSVExportService,
    DashboardService,
    DirectorDashboardService,
    RecalculationService,
    TeacherDashboardService,
)


@extend_schema_view(
    overview=extend_schema(summary="KPIs globales del período", tags=["analytics"]),
    risk_distribution=extend_schema(
        summary="Distribución semáforo por grado", tags=["analytics"]
    ),
    risk_by_city=extend_schema(
        summary="Distribución de riesgo por ciudad", tags=["analytics"]
    ),
    risk_by_special_needs=extend_schema(
        summary="Distribución de riesgo por NEE", tags=["analytics"]
    ),
    dropout_by_city=extend_schema(
        summary="Índice de deserción por ciudad", tags=["analytics"]
    ),
    withdrawal_reasons=extend_schema(
        summary="Motivos de retiro", tags=["analytics"]
    ),
    students_at_risk=extend_schema(
        summary="Estudiantes en nivel de riesgo", tags=["analytics"]
    ),
    export_csv=extend_schema(summary="Exportar CSV", tags=["analytics"]),
    section_summary=extend_schema(summary="Resumen de sección", tags=["analytics"]),
    enrollment_trend=extend_schema(
        summary="Tendencia de matrículas por mes", tags=["analytics"]
    ),
    recalculate_period=extend_schema(
        summary="Recalcular riesgo del período", tags=["analytics"]
    ),
    director_dashboard=extend_schema(
        summary="Dashboard unificado del director", tags=["analytics"]
    ),
    teacher_dashboard=extend_schema(
        summary="Dashboard unificado del docente", tags=["analytics"]
    ),
)
class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para endpoints de dashboard y reportes analíticos.

    Todos los endpoints son acciones custom (no CRUD).
    """

    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = DASHBOARD_ACTION_PERMISSIONS

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """
        KPIs globales del período.

        GET /api/analytics/dashboard/overview/?period_id=<id>
        """
        period_id = request.query_params.get("period_id")
        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        try:
            data = DashboardService.get_overview(int(period_id))
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def risk_distribution(self, request):
        """
        Distribución de riesgo por grado.

        GET /api/analytics/dashboard/risk_distribution/?period_id=<id>
        """
        period_id = request.query_params.get("period_id")
        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        try:
            data = DashboardService.get_risk_distribution_by_grade(int(period_id))
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def risk_by_city(self, request):
        """
        Distribución de riesgo por ciudad de origen.

        GET /api/analytics/dashboard/risk_by_city/?period_id=<id>
        """
        period_id = request.query_params.get("period_id")
        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        try:
            data = DashboardService.get_risk_distribution_by_city(int(period_id))
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def risk_by_special_needs(self, request):
        """
        Distribución de riesgo por tipo de NEE.

        GET /api/analytics/dashboard/risk_by_special_needs/?period_id=<id>
        """
        period_id = request.query_params.get("period_id")
        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        try:
            data = DashboardService.get_risk_distribution_by_special_needs_type(
                int(period_id)
            )
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def dropout_by_city(self, request):
        """
        Índice de deserción por ciudad.

        GET /api/analytics/dashboard/dropout_by_city/?school_year_id=<id>
        """
        school_year_id = request.query_params.get("school_year_id")

        try:
            data = DashboardService.get_dropout_by_city(
                int(school_year_id) if school_year_id else None
            )
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def withdrawal_reasons(self, request):
        """
        Conteo de motivos de retiro.

        GET /api/analytics/dashboard/withdrawal_reasons/?school_year_id=<id>
        """
        school_year_id = request.query_params.get("school_year_id")

        try:
            data = DashboardService.get_withdrawal_reasons(
                int(school_year_id) if school_year_id else None
            )
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def students_at_risk(self, request):
        """
        Lista de estudiantes en nivel de riesgo específico.

        GET /api/analytics/dashboard/students_at_risk/?period_id=<id>&risk_label=rojo
        """
        period_id = request.query_params.get("period_id")
        risk_label = request.query_params.get("risk_label", "rojo")

        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        try:
            data = DashboardService.get_students_at_risk(int(period_id), risk_label)
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        """
        Exportar datos a CSV.

        GET /api/analytics/dashboard/export_csv/?type=risk|attendance&period_id=<id>
        """
        export_type = request.query_params.get("type")
        period_id = request.query_params.get("period_id")

        if not export_type or not period_id:
            return error_response("type y period_id son requeridos", status_code=400)

        try:
            csv_data = CSVExportService.generate_csv(export_type, int(period_id))
            response = HttpResponse(csv_data, content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{export_type}_{period_id}.csv"'
            )
            return response
        except ValueError as e:
            return error_response(str(e), status_code=400)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def section_summary(self, request):
        """
        Resumen de métricas para una sección específica.

        GET /api/analytics/dashboard/section_summary/?section_id=<id>
        """
        section_id = request.query_params.get("section_id")
        if not section_id:
            return error_response("section_id es requerido", status_code=400)

        try:
            data = DashboardService.get_section_summary(int(section_id))
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def enrollment_trend(self, request):
        """
        Tendencia de matrículas por mes.

        GET /api/analytics/dashboard/enrollment_trend/?school_year_id=<id>
        """
        school_year_id = request.query_params.get("school_year_id")

        try:
            data = DashboardService.get_enrollment_trend(
                int(school_year_id) if school_year_id else None
            )
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def enrollment_comparison(self, request):
        """
        Comparativa de matrículas entre años lectivos.

        GET /api/analytics/dashboard/enrollment_comparison/
        
        Devuelve lista de años lectivos con su total de matrículas
        para poder comparar años entre sí.
        """
        try:
            data = DashboardService.get_enrollment_comparison()
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def enrollment_cumulative(self, request):
        """
        Evolución acumulada de matrículas dentro de un año lectivo.

        GET /api/analytics/dashboard/enrollment_cumulative/?school_year_id=<id>
        
        Muestra cómo crece el número de matrículas a lo largo del tiempo
        desde el inicio del año lectivo.
        """
        school_year_id = request.query_params.get("school_year_id")
        if not school_year_id:
            return error_response("school_year_id es requerido", status_code=400)

        try:
            data = DashboardService.get_enrollment_cumulative(int(school_year_id))
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["post"])
    def recalculate_period(self, request):
        """
        Recalcula el riesgo para todos los estudiantes de un período.

        POST /api/analytics/dashboard/recalculate_period/
        Body: {"academic_period_id": <id>}
        """
        period_id = request.data.get("academic_period_id")
        if not period_id:
            return error_response("academic_period_id es requerido", status_code=400)

        try:
            task = RecalculationService.recalculate_period(
                int(period_id), user_id=request.user.id
            )
            if task:
                return ok_response(
                    {"task_id": task.id, "status": "PENDING"},
                    msg="Recálculo iniciado",
                )
            return ok_response(
                {"task_id": None, "status": "NO_STUDENTS"},
                msg="No hay estudiantes para recalcular",
            )
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def director_dashboard(self, request):
        """
        Dashboard unificado del director.

        GET /api/analytics/dashboard/director_dashboard/?period_id=<id>
        Parámetros opcionales:
          - school_year_id=<id>            (para tendencia de matrículas)
          - include_risk_by_city=true       (distribución por ciudad)
          - include_risk_by_parish=true     (distribución por parroquia)
          - include_special_needs_gap=true  (brecha NEE)
        """
        period_id = request.query_params.get("period_id")
        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        school_year_id = request.query_params.get("school_year_id")
        include_city = request.query_params.get("include_risk_by_city", "").lower() == "true"
        include_parish = request.query_params.get("include_risk_by_parish", "").lower() == "true"
        include_needs = request.query_params.get("include_special_needs_gap", "").lower() == "true"

        try:
            data = DirectorDashboardService.get_director_dashboard(
                academic_period_id=int(period_id),
                school_year_id=int(school_year_id) if school_year_id else None,
                include_risk_by_city=include_city,
                include_risk_by_parish=include_parish,
                include_special_needs_gap=include_needs,
            )
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["get"])
    def teacher_dashboard(self, request):
        """
        Dashboard unificado del docente.

        Retorna métricas scoped a las secciones que el docente enseña.

        GET /api/analytics/dashboard/teacher_dashboard/?period_id=<id>
        """
        period_id = request.query_params.get("period_id")
        if not period_id:
            return error_response("period_id es requerido", status_code=400)

        try:
            data = TeacherDashboardService.get_teacher_dashboard(
                user_id=request.user.id,
                academic_period_id=int(period_id),
            )
            return ok_response(data)
        except Exception as e:
            return error_response(str(e), status_code=400)
