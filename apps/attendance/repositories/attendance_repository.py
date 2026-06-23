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
    def get_by_unique_key_with_schedule(cls, enrollment_id, class_schedule_id, attendance_date):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            class_schedule_id=class_schedule_id,
            attendance_date=attendance_date,
        ).first()

    @classmethod
    def get_students_for_schedule(cls, class_schedule_id, attendance_date):
        from apps.academic.models import ClassSchedule
        from apps.students.models import Enrollment
        try:
            cs = ClassSchedule.objects.select_related(
                "teacher_subject_section__subject_offering__section",
                "teacher_subject_section__subject_offering__subject_academic_config__subject",
                "teacher_subject_section__user__person",
            ).get(id=class_schedule_id)
        except ClassSchedule.DoesNotExist:
            return None, []

        section = cs.teacher_subject_section.subject_offering.section
        enrollments = Enrollment.objects.filter(
            section=section,
            enrollment_status="ACT",
        ).select_related(
            "student__user__person",
        ).order_by("student__user__person__last_names", "student__user__person__names")

        attendance_records = cls.model.objects.filter(
            class_schedule_id=class_schedule_id,
            attendance_date=attendance_date,
            enrollment_id__in=enrollments.values_list("id", flat=True),
        ).select_related("attendance_status", "absence_type")

        attendance_map = {a.enrollment_id: a for a in attendance_records}

        students_data = []
        for enr in enrollments:
            att = attendance_map.get(enr.id)
            students_data.append({
                "enrollment_id": enr.id,
                "student_id": enr.student_id,
                "student_name": enr.student.get_full_name(),
                "attendance_obj": att,
            })

        return cs, students_data

    @classmethod
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).select_related("attendance_status")

    @classmethod
    def get_absences_summary(cls, enrollment_id, academic_period_id):
        """
        Resumen de asistencia usando la taxonomía CANÓNICA `attendance_status.code`
        (P/J/A/T), la misma fuente que consume `feature_builder` (Fase 2, §6.3).

        El catálogo `absence_type` queda deprecado como fuente de cálculo; se mapea
        a estos estados: J→justified, A→unjustified, T→late, P→present.
        """
        from django.db.models import Count, Q
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(attendance_status__code="P")),
            justified=Count("id", filter=Q(attendance_status__code="J")),
            unjustified=Count("id", filter=Q(attendance_status__code="A")),
            late=Count("id", filter=Q(attendance_status__code="T")),
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
