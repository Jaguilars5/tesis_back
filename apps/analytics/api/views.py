"""
Vistas de API para el módulo Analytics.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..repositories import StudentRiskScoreRepository, StudentFeatureSnapshotRepository
from .serializers import StudentRiskScoreSerializer, StudentFeatureSnapshotSerializer


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

    return list_view, get_view


# Vistas para StudentRiskScore
(
    student_risk_list,
    student_risk_get,
) = create_repo_views(StudentRiskScoreRepository, StudentRiskScoreSerializer, "StudentRiskScore")

# Vistas para StudentFeatureSnapshot
(
    feature_snapshot_list,
    feature_snapshot_get,
) = create_repo_views(
    StudentFeatureSnapshotRepository, StudentFeatureSnapshotSerializer, "StudentFeatureSnapshot"
)
