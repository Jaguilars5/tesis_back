from apps.core.repositories.base import BaseRepository
from apps.attendance.models import Attendance


class AttendanceRepository(BaseRepository):
    model = Attendance

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_unique_key(cls, enrollment_id, teacher_subject_section_id, attendance_date):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            teacher_subject_section_id=teacher_subject_section_id,
            attendance_date=attendance_date,
        ).first()

    @classmethod
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).select_related("attendance_status")

    @classmethod
    def get_absences_summary(cls, enrollment_id, academic_period_id):
        from django.db.models import Count, Q
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).aggregate(
            total=Count("id"),
            justified=Count("id", filter=Q(absence_type__code="justified")),
            unjustified=Count("id", filter=Q(absence_type__code="unjustified")),
            late=Count("id", filter=Q(absence_type__code="late")),
        )

    @classmethod
    def list_by_filters(
        cls,
        student_id=None,
        academic_period_id=None,
        section_id=None,
        date=None,
        status=None,
    ):
        queryset = cls.model.objects.all()
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        if academic_period_id:
            queryset = queryset.filter(academic_period_id=academic_period_id)
        if section_id:
            queryset = queryset.filter(teacher_subject_section__section_id=section_id)
        if date:
            queryset = queryset.filter(attendance_date=date)
        if status:
            queryset = queryset.filter(attendance_status_id=status)
        return queryset.order_by("-attendance_date", "enrollment__student__last_names", "enrollment__student__names")

    @classmethod
    def list_for_risk_snapshot(cls, student_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment__student_id=student_id,
            academic_period_id=academic_period_id,
        ).order_by("attendance_date", "id")
