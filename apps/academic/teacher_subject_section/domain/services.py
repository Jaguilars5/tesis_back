from ..infrastructure.repositories import TeacherSubjectSectionRepository


class TeacherSubjectSectionService:
    repository = TeacherSubjectSectionRepository

    @classmethod
    def assign_teacher(cls, user_id, subject_offering_id):
        if cls.repository.exists_by_user_and_offering(user_id, subject_offering_id):
            raise ValueError("Docente ya está asignado a esta oferta de materia")
        return cls.repository.create(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )

    @classmethod
    def get_assignment(cls, assignment_id):
        assignment = cls.repository.get_by_id(assignment_id)
        if not assignment:
            raise ValueError(f"Asignación {assignment_id} no encontrada")
        return assignment

    @classmethod
    def remove_assignment(cls, assignment_id):
        cls.get_assignment(assignment_id)
        cls.repository.delete(assignment_id)
        return True

    @classmethod
    def list_assignments(cls, user_id=None, subject_offering_id=None):
        return cls.repository.filter_by_assignments(
            user_id=user_id,
            subject_offering_id=subject_offering_id,
        )
