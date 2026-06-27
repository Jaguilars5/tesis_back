from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import ClassScheduleRepository


class ClassScheduleService:
    repository = ClassScheduleRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_schedule(
        cls, teacher_subject_section_id, day_of_week, start_time, end_time
    ):
        cls._validate_or_raise(
            teacher_subject_section_id=teacher_subject_section_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )
        if cls.repository.check_overlap(
            teacher_subject_section_id, day_of_week, start_time, end_time
        ):
            raise ValueError({
                "non_field_errors": "El horario se superpone con otro existente"
            })
        return cls.repository.create(
            teacher_subject_section_id=teacher_subject_section_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )

    @classmethod
    def get_schedule(cls, schedule_id):
        schedule = cls.repository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError({"id": f"Horario {schedule_id} no encontrado"})
        return schedule

    @classmethod
    @transaction.atomic
    def update_schedule(cls, schedule_id, **kwargs):
        allowed = {
            "day_of_week",
            "start_time",
            "end_time",
            "is_active",
            "teacher_subject_section_id",
        }
        schedule = cls.get_schedule(schedule_id)
        day_of_week = kwargs.get("day_of_week", schedule.day_of_week)
        start_time = kwargs.get("start_time", schedule.start_time)
        end_time = kwargs.get("end_time", schedule.end_time)

        cls._validate_or_raise(
            teacher_subject_section_id=kwargs.get("teacher_subject_section_id", schedule.teacher_subject_section_id),
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )
        if cls.repository.check_overlap(
            schedule.teacher_subject_section_id,
            day_of_week,
            start_time,
            end_time,
            exclude_id=schedule.id,
        ):
            raise ValueError({
                "non_field_errors": "El horario se superpone con otro existente"
            })
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(schedule.id, **clean)

    @classmethod
    def delete_schedule(cls, schedule_id):
        cls.get_schedule(schedule_id)
        cls.repository.delete(schedule_id)
        return True

    @classmethod
    @transaction.atomic
    def soft_delete(cls, pk, confirm=False):
        obj = cls.get_schedule(pk)
        counts = cls.repository.get_cascade_counts(pk)
        total = sum(counts.values())

        if total > 0 and not confirm:
            parts = [f"{v} {k}" for k, v in counts.items()]
            return {
                "requires_confirmation": True,
                "affected_records": total,
                "message": f"Esta accion desactivar\u00e1 {', '.join(parts)} relacionados",
                "id": obj.id,
                "is_active": True,
            }

        total = cls.repository.deactivate_cascade(pk)
        return {
            "id": obj.id,
            "is_active": False,
            "deactivated_records": total,
        }

    @classmethod
    def get_by_teacher(cls, user_id):
        return cls.repository.get_by_teacher(user_id)

    @classmethod
    def get_by_student(cls, student_id):
        return cls.repository.get_by_student(student_id)

    @classmethod
    def get_by_section(cls, section_id):
        return cls.repository.get_by_section(section_id)

    @classmethod
    def get_today_for_teacher(cls, user_id):
        return cls.repository.get_today_for_teacher(user_id)
