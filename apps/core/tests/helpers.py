from apps.accounts.models import Person, User
from apps.institutions.models import DocumentType


def _get_doc_type():
    return DocumentType.objects.get_or_create(
        code="CC", defaults={"name": "Cédula de Ciudadanía"}
    )[0]


def create_test_user(email, dni=None, names=None, last_names=None,
                     password="test_password_123", role=None,
                     is_superuser=False, **extra):
    doc_type = _get_doc_type()
    person = Person.objects.create(
        document_type=doc_type,
        document_number=dni or f"DNI-{email}",
        names=names or "Test",
        last_names=last_names or "User",
        email=email,
    )
    return User.objects.create_user(
        person=person,
        password=password,
        is_superuser=is_superuser,
        **extra,
    )


def create_test_student(document_number, names="Test", last_names="Student",
                        birth_date=None, email="", phone="",
                        student_code=None):
    doc_type = _get_doc_type()
    person = Person.objects.create(
        document_type=doc_type,
        document_number=document_number,
        names=names,
        last_names=last_names,
        birth_date=birth_date,
        email=email,
        phone=phone,
    )
    from apps.students.models import Student
    code = student_code or f"EST-{document_number}"
    return Student.objects.create(person=person, student_code=code)
