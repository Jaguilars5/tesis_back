from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..repositories.institution_repo import (
    InstitutionRepository, SchoolYearRepository, ClassroomRepository
)
from .serializers import (
    InstitutionSerializer, School_YearSerializer, ClassroomSerializer
)

from apps.core.utils import ok_response, error_response

def create_repo_views(repository_class, serializer_class, model_name):
    @api_view(['POST'])
    def list_view(request):
        try:
            items = repository_class.get_all()
            return ok_response(serializer_class(items, many=True).data)
        except Exception as e:
            return error_response(e)

    @api_view(['POST'])
    def get_view(request):
        try:
            pk = request.data.get('id')
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f'{model_name} not found', 404)
            return ok_response(serializer_class(item).data)
        except Exception as e:
            return error_response(e)

    @api_view(['POST'])
    def add_view(request):
        try:
            serializer = serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data, status=201)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    @api_view(['POST'])
    def update_view(request):
        try:
            pk = request.data.get('id')
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f'{model_name} not found', 404)
            serializer = serializer_class(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    @api_view(['POST'])
    def soft_delete_view(request):
        try:
            pk = request.data.get('id')
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f'{model_name} not found', 404)
            if hasattr(item, 'active'):
                item.active = False
                item.save()
                return ok_response({'id': pk, 'active': False})
            return error_response(f'{model_name} does not support soft delete.')
        except Exception as e:
            return error_response(e)

    @api_view(['POST'])
    def delete_view(request):
        try:
            pk = request.data.get('id')
            item = repository_class.get_by_id(pk)
            if not item:
                return error_response(f'{model_name} not found', 404)
            item.delete()
            return ok_response({'id': pk, 'deleted': True})
        except Exception as e:
            return error_response(e)

    return list_view, get_view, add_view, update_view, soft_delete_view, delete_view

# Institution
institution_list, institution_get, institution_add, institution_update, institution_soft_delete, institution_delete = create_repo_views(InstitutionRepository, InstitutionSerializer, 'Institution')

# School Year
school_year_list, school_year_get, school_year_add, school_year_update, school_year_soft_delete, school_year_delete = create_repo_views(SchoolYearRepository, School_YearSerializer, 'School_Year')

# Classroom
classroom_list, classroom_get, classroom_add, classroom_update, classroom_soft_delete, classroom_delete = create_repo_views(ClassroomRepository, ClassroomSerializer, 'Classroom')
