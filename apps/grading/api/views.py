"""
Vistas de API para el módulo Grading.

Utiliza un patrón de generación de vistas dinámicas para operaciones CRUD básicas
sobre calificaciones, asistencia e incidentes de conducta.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..repositories import (
    AttendanceRepository,
    ConductIncidentRepository,
    StudentNoteRepository,
)
from .serializers import (
    AttendanceSerializer,
    ConductIncidentSerializer,
    StudentNoteSerializer,
)


from apps.core.utils import ok_response, error_response


def create_repo_views(repository_class, serializer_class, model_name):
    """
    Genera un conjunto de vistas CRUD estándar para un repositorio y serializador dados.

    Retorna una tupla con las funciones de vista para:
    list, get, add, update, soft_delete, delete.
    """

    @api_view(["POST"])
    def list_view(request):
        """Lista todos los registros (activos por defecto)."""
        try:
            items = repository_class.get_all()
            return ok_response(serializer_class(items, many=True).data)
        except Exception as e:
            return error_response(e)

    @api_view(["POST"])
    def get_view(request):
        """Obtiene un registro por ID pasado en el body."""
        try:
            pk = request.data.get("id")
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f"{model_name} not found", 404)
            return ok_response(serializer_class(item).data)
        except Exception as e:
            return error_response(e)

    @api_view(["POST"])
    def add_view(request):
        """Crea un nuevo registro."""
        try:
            serializer = serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data, status=201)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    @api_view(["POST"])
    def update_view(request):
        """Actualiza parcialmente un registro existente."""
        try:
            pk = request.data.get("id")
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f"{model_name} not found", 404)
            serializer = serializer_class(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    @api_view(["POST"])
    def soft_delete_view(request):
        """Desactiva un registro (active=False) si el modelo lo soporta."""
        try:
            pk = request.data.get("id")
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f"{model_name} not found", 404)
            if hasattr(item, "active"):
                item.active = False
                item.save()
                return ok_response({"id": pk, "active": False})
            return error_response(f"{model_name} does not support soft delete.")
        except Exception as e:
            return error_response(e)

    @api_view(["POST"])
    def delete_view(request):
        """Elimina físicamente un registro."""
        try:
            pk = request.data.get("id")
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f"{model_name} not found", 404)
            item.delete()
            return ok_response({"id": pk, "deleted": True})
        except Exception as e:
            return error_response(e)

    return list_view, get_view, add_view, update_view, soft_delete_view, delete_view


# Vistas para Calificaciones
(
    student_note_list,
    student_note_get,
    student_note_add,
    student_note_update,
    student_note_soft_delete,
    student_note_delete,
) = create_repo_views(StudentNoteRepository, StudentNoteSerializer, "StudentNote")

# Vistas para Asistencia
(
    attendance_list,
    attendance_get,
    attendance_add,
    attendance_update,
    attendance_soft_delete,
    attendance_delete,
) = create_repo_views(AttendanceRepository, AttendanceSerializer, "Attendance")

# Vistas para Incidentes de Conducta
(
    conduct_incident_list,
    conduct_incident_get,
    conduct_incident_add,
    conduct_incident_update,
    conduct_incident_soft_delete,
    conduct_incident_delete,
) = create_repo_views(
    ConductIncidentRepository, ConductIncidentSerializer, "ConductIncident"
)

