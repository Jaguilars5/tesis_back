from datetime import date, datetime

from django.db import transaction

from ..infrastructure.repositories import (
    EnrollmentRepository,
    StudentRepository,
    StudentRepresentativeRepository,
)
from ..infrastructure.models import Enrollment, EnrollmentStatusChoices, Kinship, Student, StudentRepresentative


class StudentService:
    repository = StudentRepository
    representative_repository = StudentRepresentativeRepository

    @staticmethod
    def _parse_date(value):
        if value is None or isinstance(value, date):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

    @classmethod
    @transaction.atomic
    def create_student(
        cls,
        document_number, names, last_names, birth_date=None,
        email="", phone="", document_type_id=None, parish_id=None,
        has_special_needs=False, special_needs_type_id=None,
    ):
        from apps.iam.infrastructure.models import Role, User, UserRole
        from apps.people.models import DocumentType, Person

        if not document_type_id:
            cc_type = DocumentType.objects.get_or_create(
                code="CC", defaults={"name": "Cédula de Ciudadanía"}
            )[0]
            document_type_id = cc_type.id

        person = Person.objects.create(
            document_type_id=document_type_id,
            document_number=document_number,
            names=names,
            last_names=last_names,
            birth_date=cls._parse_date(birth_date),
            email=email,
            phone=phone,
            parish_id=parish_id,
        )
        username = User.generate_username(names, last_names) or document_number
        user = User.objects.create_user(
            person=person,
            username=username,
            password=document_number,
            must_change_password=True,
        )
        role, _ = Role.objects.get_or_create(
            code="ESTUDIANTE", defaults={"name": "Estudiante"}
        )
        UserRole.objects.create(user=user, role=role)
        code = f"EST-{StudentRepository.count() + 1:05d}"
        student_data = {"user": user, "student_code": code}
        if has_special_needs:
            student_data["has_special_needs"] = True
            if special_needs_type_id:
                student_data["special_needs_type_id"] = special_needs_type_id
        student = StudentRepository.create(**student_data)
        return student

    @classmethod
    def get_student(cls, student_id):
        student = cls.repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Estudiante {student_id} no encontrado")
        return student

    @classmethod
    def get_all_students(cls):
        return cls.repository.get_all()

    @classmethod
    def list_students_by_section(cls, section_id):
        return cls.repository.get_by_section(section_id)

    @classmethod
    def search_students(cls, query):
        return cls.repository.search(query)

    @classmethod
    def update_student(cls, student_id, **kwargs):
        student = cls.get_student(student_id)
        person = student.user.person
        person_fields = {
            "parish": "parish_id",
            "document_number": "document_number",
            "names": "names",
            "last_names": "last_names",
            "birth_date": "birth_date",
            "email": "email",
            "phone": "phone",
            "document_type": "document_type_id",
        }
        person_updated = False
        for key, person_attr in person_fields.items():
            if key in kwargs:
                value = kwargs.pop(key)
                setattr(person, person_attr, value)
                person_updated = True
        if person_updated:
            person.save()
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
        student.save()
        return student

    @classmethod
    def deactivate_student(cls, student_id):
        student = cls.get_student(student_id)
        student.is_active = False
        student.save()
        return student

    @classmethod
    @transaction.atomic
    def create_and_assign_representative(
        cls, student_id, document_number, names, last_names,
        email="", phone="", birth_date=None, document_type_id=None,
        parish_id=None, kinship="Padre", **kwargs
    ):
        from apps.iam.infrastructure.models import Role, User, UserRole
        from apps.people.models import DocumentType, Person

        if not document_type_id:
            cc_type = DocumentType.objects.get_or_create(
                code="CC", defaults={"name": "Cédula de Ciudadanía"}
            )[0]
            document_type_id = cc_type.id
        person = Person.objects.create(
            document_type_id=document_type_id,
            document_number=document_number,
            names=names,
            last_names=last_names,
            birth_date=cls._parse_date(birth_date),
            email=email,
            phone=phone,
            parish_id=parish_id,
        )
        username = User.generate_username(names, last_names) or document_number
        user = User.objects.create_user(
            person=person,
            username=username,
            password=document_number,
            must_change_password=True,
        )
        role, _ = Role.objects.get_or_create(
            code="REPRESENTANTE", defaults={"name": "Representante"}
        )
        UserRole.objects.create(user=user, role=role)
        return cls.assign_representative(
            student_id=student_id, user_id=user.id, kinship=kinship, **kwargs
        )

    @classmethod
    def assign_representative(cls, student_id, user_id, kinship="Padre", **kwargs):
        if isinstance(kinship, str):
            kinship_obj, _ = Kinship.objects.get_or_create(
                code=kinship.upper() if len(kinship) <= 30 else "OTRO",
                defaults={"name": kinship}
            )
        else:
            kinship_obj = kinship
        rel = StudentRepresentative(
            student_id=student_id,
            user_id=user_id,
            kinship=kinship_obj,
            **kwargs
        )
        rel.save()
        return rel

    @classmethod
    def remove_representative(cls, student_id, user_id):
        rel = cls.representative_repository.get_relationship(student_id, user_id)
        if not rel:
            raise ValueError("Relación no encontrada")
        rel.delete()
        return True

    @classmethod
    def set_primary_representative(cls, student_id, user_id):
        cls.representative_repository.get_relationship(student_id, user_id)
        StudentRepresentative.objects.filter(
            student_id=student_id, is_primary=True
        ).update(is_primary=False)
        StudentRepresentative.objects.filter(
            student_id=student_id, user_id=user_id
        ).update(is_primary=True)


class EnrollmentService:
    repository = EnrollmentRepository

    @classmethod
    @transaction.atomic
    def enroll_student(cls, student, section, enrollment_date=None):
        if cls.repository.has_active_enrollment(student):
            raise ValueError("El estudiante ya tiene una matrícula activa")

        if section.capacity:
            active_count = cls.repository.count_active_in_section(section)
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

    @classmethod
    @transaction.atomic
    def update_enrollment(cls, enrollment, section=None, enrollment_status=None, is_repeat=None):
        if section is not None and section.id != enrollment.section_id:
            if enrollment.enrollment_status == EnrollmentStatusChoices.ACTIVE:
                if section.capacity:
                    active_count = cls.repository.count_active_in_section(section)
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

    @classmethod
    @transaction.atomic
    def withdraw_student(cls, enrollment, reason=None):
        from ..infrastructure.models import WithdrawalReason

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

    @classmethod
    @transaction.atomic
    def transfer_student(cls, enrollment, new_section_id):
        from apps.institutions.section import SectionRepository

        new_section = SectionRepository.get_by_id(new_section_id)
        if not new_section:
            raise ValueError(f"Sección {new_section_id} no encontrada")
        current_active = cls.repository.get_active_by_student(enrollment.student)
        if current_active and current_active.id != enrollment.id:
            raise ValueError("El estudiante tiene otra matrícula activa")

        if new_section.capacity:
            active_count = cls.repository.count_active_in_section(new_section)
            if active_count >= new_section.capacity:
                raise ValueError(
                    f"La sección destino ha alcanzado su capacidad máxima ({new_section.capacity})"
                )

        enrollment.section = new_section
        enrollment.enrollment_status = EnrollmentStatusChoices.ACTIVE
        enrollment.save()
        return enrollment

    @classmethod
    @transaction.atomic
    def soft_delete_enrollment(cls, enrollment):
        enrollment.enrollment_status = EnrollmentStatusChoices.INACTIVE
        enrollment.save()
        return {"id": enrollment.id}

    @classmethod
    def get_active_enrollment(cls, student):
        return cls.repository.get_active_by_student(student)
