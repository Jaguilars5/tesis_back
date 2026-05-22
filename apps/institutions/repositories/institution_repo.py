from django.db import models
from ..models import School_Year, Classroom


class BaseRepository:
    model = None

    @classmethod
    def get_all(cls, active_only=True):
        queryset = cls.model.objects.all()
        if active_only and hasattr(cls.model, "active"):
            queryset = queryset.filter(active=True)
        return queryset

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None


class SchoolYearRepository(BaseRepository):
    model = School_Year


class ClassroomRepository(BaseRepository):
    model = Classroom

    @classmethod
    def get_by_type(cls, room_type_id):
        return cls.model.objects.filter(
            room_type_id=room_type_id, active=True
        ).order_by("name")

    @classmethod
    def get_by_capacity(cls, min_capacity):
        return cls.model.objects.filter(
            capacity__gte=min_capacity, active=True
        ).order_by("-capacity")
