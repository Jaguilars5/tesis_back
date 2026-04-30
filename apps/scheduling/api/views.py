"""
Vistas de API para el módulo Scheduling.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..repositories import (
    ScheduleSlotRepository,
    TimeSlotRepository,
    TeacherAvailabilityRepository,
    SubjectConstraintRepository,
    ScheduleTemplateConfigRepository,
)
from .serializers import (
    ScheduleSlotSerializer,
    TimeSlotSerializer,
    TeacherAvailabilitySerializer,
    SubjectConstraintSerializer,
    ScheduleTemplateConfigSerializer,
)


from apps.core.utils import ok_response, error_response


def create_repo_views(repository_class, serializer_class, model_name):
    """Generador de vistas CRUD estándar."""

    @api_view(["POST"])
    def list_view(request):
        try:
            items = repository_class.get_all()
            return ok_response(serializer_class(items, many=True).data)
        except Exception as e:
            return error_response(e)

    @api_view(["POST"])
    def get_view(request):
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
    def delete_view(request):
        try:
            pk = request.data.get("id")
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f"{model_name} not found", 404)
            item.delete()
            return ok_response({"id": pk, "deleted": True})
        except Exception as e:
            return error_response(e)

    return list_view, get_view, add_view, update_view, delete_view


# Vistas para ScheduleSlot
(
    schedule_slot_list,
    schedule_slot_get,
    schedule_slot_add,
    schedule_slot_update,
    schedule_slot_delete,
) = create_repo_views(ScheduleSlotRepository, ScheduleSlotSerializer, "ScheduleSlot")

# Vistas para TimeSlot
(
    time_slot_list,
    time_slot_get,
    time_slot_add,
    time_slot_update,
    time_slot_delete,
) = create_repo_views(TimeSlotRepository, TimeSlotSerializer, "TimeSlot")

# Vistas para TeacherAvailability
(
    teacher_availability_list,
    teacher_availability_get,
    teacher_availability_add,
    teacher_availability_update,
    teacher_availability_delete,
) = create_repo_views(
    TeacherAvailabilityRepository, TeacherAvailabilitySerializer, "TeacherAvailability"
)

# Vistas para SubjectConstraint
(
    subject_constraint_list,
    subject_constraint_get,
    subject_constraint_add,
    subject_constraint_update,
    subject_constraint_delete,
) = create_repo_views(
    SubjectConstraintRepository, SubjectConstraintSerializer, "SubjectConstraint"
)

# Vistas para ScheduleTemplateConfig
(
    schedule_config_list,
    schedule_config_get,
    schedule_config_add,
    schedule_config_update,
    schedule_config_delete,
) = create_repo_views(
    ScheduleTemplateConfigRepository,
    ScheduleTemplateConfigSerializer,
    "ScheduleTemplateConfig",
)
