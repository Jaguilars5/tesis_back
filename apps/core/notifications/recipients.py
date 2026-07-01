"""Resolución de destinatarios reutilizando los repositorios existentes."""

from apps.students.repositories.enrollment_repo import EnrollmentRepository
from apps.students.repositories.students_repo import StudentRepresentativeRepository


def representative_user_ids(student_id):
    """IDs de usuario de los representantes activos que reciben notificaciones."""
    reps = StudentRepresentativeRepository.get_by_student(student_id).filter(
        is_active=True,
        receives_notifications=True,
    )
    return [rep.user_id for rep in reps if rep.user_id]


def student_and_reps_user_ids(student):
    """IDs de usuario del estudiante + sus representantes."""
    user_ids = []
    student_user_id = getattr(student, "user_id", None)
    if student_user_id:
        user_ids.append(student_user_id)
    user_ids.extend(representative_user_ids(student.id))
    return user_ids


def section_students_and_reps_user_ids(section):
    """IDs de usuario de todos los estudiantes activos de una sección + reps."""
    user_ids = []
    enrollments = EnrollmentRepository.get_students_by_section(section, "ACT")
    for enrollment in enrollments:
        student = enrollment.student
        if not student:
            continue
        user_ids.extend(student_and_reps_user_ids(student))
    return user_ids
