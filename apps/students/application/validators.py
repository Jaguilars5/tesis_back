from ..infrastructure.repositories import EnrollmentRepository, StudentRepository


class StudentValidators:
    @staticmethod
    def validate_document_number_unique(document_number, exclude_id=None):
        from apps.people.models import Person

        qs = Person.objects.filter(document_number=document_number)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            raise ValueError("El número de documento ya está registrado.")

    @staticmethod
    def validate_student_exists(student_id):
        student = StudentRepository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Estudiante {student_id} no encontrado")
        return student


class EnrollmentValidators:
    @staticmethod
    def validate_no_active_enrollment(student):
        if EnrollmentRepository.has_active_enrollment(student):
            raise ValueError("El estudiante ya tiene una matrícula activa")

    @staticmethod
    def validate_section_capacity(section, exclude_enrollment_id=None):
        if not section.capacity:
            return
        active_count = EnrollmentRepository.count_active_in_section(section)
        if exclude_enrollment_id:
            enrollment = EnrollmentRepository.get_by_id(exclude_enrollment_id)
            if enrollment and enrollment.section_id == section.id and enrollment.enrollment_status == "ACT":
                active_count -= 1
        if active_count >= section.capacity:
            raise ValueError(
                f"La sección ha alcanzado su capacidad máxima ({section.capacity})"
            )
