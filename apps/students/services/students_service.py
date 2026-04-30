from datetime import date
from django.db import transaction
from ..models import Student, Representative, Student_Representative
from ..repositories.students_repo import (
    StudentRepository,
    RepresentativeRepository,
    StudentRepresentativeRepository,
)


class StudentService:
    """Lógica de negocio para estudiantes y representantes"""

    # =====================
    # STUDENT METHODS
    # =====================

    @staticmethod
    def create_student(
        dni,
        names,
        last_names,
        birth_date,
        section_id,
        enrollment_number=None,
        device_origin=None,
    ):
        """Crear nuevo estudiante"""
        # Validar DNI único
        if StudentRepository.get_by_dni(dni):
            raise ValueError(f"DNI {dni} ya existe")

        # Validar edad razonable
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        if age < 5 or age > 30:
            raise ValueError(f"Edad calculada {age} no es válida para un estudiante")

        student = Student(
            dni=dni,
            names=names,
            last_names=last_names,
            birth_date=birth_date,
            section_id=section_id,
            enrollment_number=enrollment_number,
            device_origin=device_origin,
        )
        student.save()
        return student

    @staticmethod
    def get_student(student_id):
        """Obtener estudiante"""
        student = StudentRepository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Estudiante {student_id} no encontrado")
        return student

    @staticmethod
    def get_student_by_dni(dni):
        """Obtener estudiante por DNI"""
        student = StudentRepository.get_by_dni(dni)
        if not student:
            raise ValueError(f"Estudiante con DNI {dni} no encontrado")
        return student

    @staticmethod
    def get_all_students(active_only=True):
        """Listar todos los estudiantes"""
        return StudentRepository.get_all(active_only=active_only)

    @staticmethod
    def list_students_by_section(section_id):
        """Listar estudiantes de una sección"""
        return StudentRepository.get_by_section(section_id)

    @staticmethod
    def get_student_details(student_id):
        """Obtener detalles completos de estudiante"""
        student = StudentService.get_student(student_id)
        representatives = Student_Representative.objects.filter(
            student=student
        ).select_related("representative")

        return {
            "student": student,
            "full_name": student.get_full_name(),
            "age": student.get_age(),
            "section": student.section,
            "representatives": representatives,
            "primary_representative": StudentService.get_primary_representative(
                student_id
            ),
            "enrollment_date": student.enrollment_date,
        }

    @staticmethod
    def update_student(student_id, **kwargs):
        """Actualizar estudiante"""
        student = StudentService.get_student(student_id)

        # Validar DNI único si cambia
        if "dni" in kwargs and kwargs["dni"] != student.dni:
            if StudentRepository.get_by_dni(kwargs["dni"]):
                raise ValueError(f"DNI {kwargs['dni']} ya existe")

        for key, value in kwargs.items():
            if hasattr(student, key) and key not in ["id", "created_at"]:
                setattr(student, key, value)

        student.save()
        return student

    @staticmethod
    def deactivate_student(student_id):
        """Desactivar estudiante (soft delete)"""
        student = StudentService.get_student(student_id)
        student.active = False
        student.save()
        return student

    @staticmethod
    def search_students(query):
        """Buscar estudiantes por nombre, DNI o matrícula"""
        return StudentRepository.search(query)

    @staticmethod
    def count_students_by_section(section_id):
        """Contar estudiantes en una sección"""
        return Student.objects.filter(section_id=section_id, active=True).count()

    # =====================
    # REPRESENTATIVE METHODS
    # =====================

    @staticmethod
    def create_representative(
        dni, names, last_names, phone, email=None, address=None
    ):
        """Crear nuevo representante"""
        # Validar DNI único
        if RepresentativeRepository.get_by_dni(dni):
            raise ValueError(f"DNI {dni} ya existe como representante")

        representative = Representative(
            dni=dni,
            names=names,
            last_names=last_names,
            phone=phone,
            email=email,
            address=address,
        )
        representative.save()
        return representative

    @staticmethod
    def get_representative(representative_id):
        """Obtener representante"""
        representative = RepresentativeRepository.get_by_id(representative_id)
        if not representative:
            raise ValueError(f"Representante {representative_id} no encontrado")
        return representative

    @staticmethod
    def get_representative_by_dni(dni):
        """Obtener representante por DNI"""
        representative = RepresentativeRepository.get_by_dni(dni)
        if not representative:
            raise ValueError(f"Representante con DNI {dni} no encontrado")
        return representative

    @staticmethod
    def get_all_representatives(active_only=True):
        """Listar todos los representantes"""
        return RepresentativeRepository.get_all(active_only=active_only)

    @staticmethod
    def get_representative_details(representative_id):
        """Obtener detalles de representante"""
        representative = StudentService.get_representative(representative_id)
        students = Student_Representative.objects.filter(
            representative=representative
        ).select_related("student")

        return {
            "representative": representative,
            "full_name": representative.get_full_name(),
            "students": students,
            "student_count": students.count(),
        }

    @staticmethod
    def update_representative(representative_id, **kwargs):
        """Actualizar representante"""
        representative = StudentService.get_representative(representative_id)

        # Validar DNI único si cambia
        if "dni" in kwargs and kwargs["dni"] != representative.dni:
            if RepresentativeRepository.get_by_dni(kwargs["dni"]):
                raise ValueError(f"DNI {kwargs['dni']} ya existe")

        for key, value in kwargs.items():
            if hasattr(representative, key) and key not in ["id", "created_at"]:
                setattr(representative, key, value)

        representative.save()
        return representative

    @staticmethod
    def deactivate_representative(representative_id):
        """Desactivar representante"""
        representative = StudentService.get_representative(representative_id)
        representative.active = False
        representative.save()
        return representative

    @staticmethod
    def search_representatives(query):
        """Buscar representantes"""
        return RepresentativeRepository.search(query)

    # =====================
    # STUDENT_REPRESENTATIVE METHODS
    # =====================

    @staticmethod
    def assign_representative(
        student_id,
        representative_id,
        kinship="Padre",
        is_primary=False,
        can_pickup=True,
        emergency_contact=False,
        receives_notifications=True,
    ):
        """Asignar representante a estudiante"""
        # Validar ambos existen
        student = StudentService.get_student(student_id)
        representative = StudentService.get_representative(representative_id)

        # Validar que no sea duplicado
        existing = StudentRepresentativeRepository.get_relationship(
            student_id, representative_id
        )
        if existing:
            raise ValueError("Este representante ya está asignado al estudiante")

        # Si es el primero, hacerlo primario automáticamente
        has_primary = Student_Representative.objects.filter(
            student_id=student_id, is_primary=True
        ).exists()
        if not has_primary:
            is_primary = True

        relationship = Student_Representative(
            student=student,
            representative=representative,
            kinship=kinship,
            is_primary=is_primary,
            can_pickup=can_pickup,
            emergency_contact=emergency_contact,
            receives_notifications=receives_notifications,
        )
        relationship.save()
        return relationship

    @staticmethod
    def get_student_representatives(student_id):
        """Obtener todos los representantes de un estudiante"""
        return StudentRepresentativeRepository.get_by_student(student_id)

    @staticmethod
    def get_primary_representative(student_id):
        """Obtener el representante principal"""
        return RepresentativeRepository.get_primary_representative(student_id)

    @staticmethod
    def set_primary_representative(student_id, representative_id):
        """Establecer un representante como principal"""
        # Desmarcar el actual principal
        Student_Representative.objects.filter(
            student_id=student_id, is_primary=True
        ).update(is_primary=False)

        # Marcar el nuevo como principal
        relationship = StudentRepresentativeRepository.get_relationship(
            student_id, representative_id
        )
        if not relationship:
            raise ValueError("Relación no existe")

        relationship.is_primary = True
        relationship.save()
        return relationship

    @staticmethod
    def update_representative_authorization(student_id, representative_id, **kwargs):
        """Actualizar autorizaciones de un representante"""
        relationship = StudentRepresentativeRepository.get_relationship(
            student_id, representative_id
        )
        if not relationship:
            raise ValueError("Relación no existe")

            if key in [
                "kinship",
                "can_pickup",
                "emergency_contact",
                "receives_notifications",
            ]:
                setattr(relationship, key, value)

        relationship.save()
        return relationship

    @staticmethod
    def remove_representative(student_id, representative_id):
        """Desasignar representante de estudiante"""
        relationship = StudentRepresentativeRepository.get_relationship(
            student_id, representative_id
        )
        if not relationship:
            raise ValueError("Relación no existe")

        # Validar que no sea el único representante
        other_reps = (
            Student_Representative.objects.filter(student_id=student_id)
            .exclude(id=relationship.id)
            .count()
        )

        if other_reps == 0:
            raise ValueError(
                "No se puede eliminar el último representante del estudiante"
            )

        relationship.delete()
        return True

    @staticmethod
    def get_representative_students(representative_id):
        """Obtener todos los estudiantes de un representante"""
        return StudentRepresentativeRepository.get_by_representative(representative_id)

    @staticmethod
    def get_contact_info_for_student(student_id):
        """Obtener información de contacto completa de un estudiante"""
        student = StudentService.get_student(student_id)
        representatives = (
            Student_Representative.objects.filter(student_id=student_id)
            .select_related("representative")
            .order_by("-is_primary")
        )

        contacts = []
        for rel in representatives:
            rep = rel.representative
            if rep.active:
                contacts.append(
                    {
                        "representative": rep,
                        "kinship": rel.kinship,
                        "phone": rep.phone,
                        "email": rep.email,
                        "is_primary": rel.is_primary,
                        "can_pickup": rel.can_pickup,
                        "emergency_contact": rel.emergency_contact,
                        "receives_notifications": rel.receives_notifications,
                    }
                )

        return {
            "student": student,
            "contacts": contacts,
            "primary_contact": contacts[0] if contacts else None,
        }
