from datetime import date
from django.db import transaction
from apps.institutions.section import SectionRepository
from ..models import Enrollment
from ..models.enrollment import EnrollmentStatusChoices
from ..repositories.enrollment_repo import EnrollmentRepository


class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def enroll_student(student, section, enrollment_date=None):
        if EnrollmentRepository.has_active_enrollment(student):
            raise ValueError("El estudiante ya tiene una matrícula activa")

        if EnrollmentRepository.has_enrollment_in_school_year(
            student, section.school_year
        ):
            raise ValueError("El estudiante ya tiene una matrícula en este año lectivo")

        if section.capacity:
            active_count = EnrollmentRepository.count_active_in_section(section)
            if active_count >= section.capacity:
                raise ValueError(
                    f"La sección ha alcanzado su capacidad máxima ({section.capacity})"
                )

        enrollment = Enrollment(
            student=student,
            section=section,
            enrollment_status=EnrollmentStatusChoices.ACTIVE,
            enrollment_date=enrollment_date or date.today(),
        )
        enrollment.save()
        return enrollment

    @staticmethod
    @transaction.atomic
    def update_enrollment(enrollment, section=None, enrollment_status=None, is_repeat=None):
        if section is not None and section.id != enrollment.section_id:
            if enrollment.enrollment_status == EnrollmentStatusChoices.ACTIVE:
                other_active = EnrollmentRepository.get_active_by_student_excluding(
                    enrollment.student, enrollment.id
                )
                if other_active:
                    raise ValueError("El estudiante tiene otra matrícula activa")

            if section.capacity:
                active_count = EnrollmentRepository.count_active_in_section(section)
                already_counted = (
                    1
                    if enrollment.section_id == section.id
                    and enrollment.enrollment_status == EnrollmentStatusChoices.ACTIVE
                    else 0
                )
                if active_count - already_counted >= section.capacity:
                    raise ValueError(
                        f"La sección ha alcanzado su capacidad máxima ({section.capacity})"
                    )

            enrollment.section = section

        if enrollment_status is not None:
            enrollment.enrollment_status = enrollment_status

        if is_repeat is not None:
            enrollment.is_repeat = is_repeat

        enrollment.save()
        return enrollment

    @staticmethod
    @transaction.atomic
    def withdraw_student(enrollment, reason=None):
        from ..models import WithdrawalReason
        enrollment.enrollment_status = EnrollmentStatusChoices.WITHDRAWN
        if reason:
            if isinstance(reason, int):
                enrollment.withdrawal_reason_id = reason
            elif isinstance(reason, str):
                try:
                    withdrawal_reason = WithdrawalReason.objects.get(id=int(reason))
                    enrollment.withdrawal_reason = withdrawal_reason
                except (ValueError, WithdrawalReason.DoesNotExist):
                    withdrawal_reason, _ = WithdrawalReason.objects.get_or_create(
                        code="OTRO",
                        defaults={"name": "Otro"}
                    )
                    enrollment.withdrawal_reason = withdrawal_reason
            else:
                enrollment.withdrawal_reason = reason
        enrollment.withdrawal_date = date.today()
        enrollment.save()
        return enrollment

    @staticmethod
    @transaction.atomic
    def transfer_student(enrollment, new_section_id):
        new_section = SectionRepository.get_by_id(new_section_id)
        if not new_section:
            raise ValueError(f"Sección {new_section_id} no encontrada")
        current_active = EnrollmentRepository.get_active_by_student(enrollment.student)
        if current_active and current_active.id != enrollment.id:
            raise ValueError("El estudiante tiene otra matrícula activa")

        if new_section.capacity:
            active_count = EnrollmentRepository.count_active_in_section(new_section)
            if active_count >= new_section.capacity:
                raise ValueError(
                    f"La sección destino ha alcanzado su capacidad máxima ({new_section.capacity})"
                )

        enrollment.section = new_section
        enrollment.enrollment_status = EnrollmentStatusChoices.ACTIVE
        enrollment.save()
        return enrollment

    @staticmethod
    @transaction.atomic
    def soft_delete_enrollment(enrollment):
        enrollment.enrollment_status = EnrollmentStatusChoices.INACTIVE
        enrollment.save()
        return {"id": enrollment.id}

    @staticmethod
    def get_active_enrollment(student):
        return EnrollmentRepository.get_active_by_student(student)
