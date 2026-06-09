from datetime import date
from django.db import transaction
from apps.institutions.repositories.section_repository import SectionRepository
from ..models import Enrollment
from ..repositories.enrollment_repo import EnrollmentRepository
from ..repositories.enrollment_status_repo import EnrollmentStatusRepository


class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def enroll_student(student, section, enrollment_date=None):
        if EnrollmentRepository.has_active_enrollment(student):
            raise ValueError("El estudiante ya tiene una matrícula activa")

        if section.capacity:
            active_count = EnrollmentRepository.count_active_in_section(section)
            if active_count >= section.capacity:
                raise ValueError(
                    f"La sección ha alcanzado su capacidad máxima ({section.capacity})"
                )

        active_status = EnrollmentStatusRepository.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )

        enrollment = Enrollment(
            student=student,
            section=section,
            school_year=section.school_year,
            enrollment_status=active_status,
            enrollment_date=enrollment_date or date.today(),
        )
        enrollment.save()
        return enrollment

    @staticmethod
    @transaction.atomic
    def withdraw_student(enrollment, reason=""):
        withdrawn_status = EnrollmentStatusRepository.get_or_create(
            code="RET", defaults={"name": "Retirado"}
        )
        enrollment.enrollment_status = withdrawn_status
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

        active_status = EnrollmentStatusRepository.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        enrollment.section = new_section
        enrollment.enrollment_status = active_status
        enrollment.save()
        return enrollment

    @staticmethod
    def get_active_enrollment(student):
        return EnrollmentRepository.get_active_by_student(student)
