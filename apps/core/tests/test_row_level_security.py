from datetime import date
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, User, UserRole
from apps.people.models import Person
from apps.core.tests.helpers import create_test_user
from apps.academic.models import SubjectOffering, Subject, SubjectAcademicConfig, TeacherSubjectSection, PeriodType
from apps.institutions.models import Section, SchoolYear, AcademicGrade, AcademicLevel, AcademicSublevel
from apps.students.models import Student, StudentRepresentative, Enrollment
from apps.grading.models import EvaluativeActivity, StudentNote, BlockComponent, EvaluationBlock
from apps.students.models import Kinship
from apps.grading.models import ActivityType


class RowLevelSecurityTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Configurar Roles y Permisos en la DB
        self.role_docente = Role.objects.create(name="Docente", code="DOCENTE")
        self.role_representante = Role.objects.create(name="Representante", code="REPRESENTANTE")
        self.role_estudiante = Role.objects.create(name="Estudiante", code="ESTUDIANTE")

        self.perm_view_tss = Permission.objects.create(code="academic.view_teacher_subject", module="academic")
        self.perm_view_note = Permission.objects.create(code="grading.view_note", module="grading")

        RolePermission.objects.create(role=self.role_docente, permission=self.perm_view_tss)
        RolePermission.objects.create(role=self.role_docente, permission=self.perm_view_note)
        RolePermission.objects.create(role=self.role_representante, permission=self.perm_view_tss)
        RolePermission.objects.create(role=self.role_representante, permission=self.perm_view_note)
        RolePermission.objects.create(role=self.role_estudiante, permission=self.perm_view_note)

        # 2. Configurar metadatos institucionales
        self.school_year = SchoolYear.objects.create( start_date="2026-01-01", end_date="2026-12-31"
        )
        self.academic_level = AcademicLevel.objects.create(name="Educación General Básica")
        self.academic_sublevel = AcademicSublevel.objects.create(
            name="Subnivel 1", academic_level=self.academic_level
        )
        self.academic_grade = AcademicGrade.objects.create(
            name="Octavo Grado", academic_sublevel=self.academic_sublevel
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30
        )
        # 3. Crear Personas e Hilos de Usuarios
        # Docente 1
        self.person_t1 = Person.objects.create(names="Teacher", last_names="One", email="t1@test.com", document_number="111", birth_date=date(1980, 1, 1))
        self.user_t1 = User.objects.create_user(person=self.person_t1, password="test_password_123")
        UserRole.objects.create(user=self.user_t1, role=self.role_docente)

        # Docente 2
        self.person_t2 = Person.objects.create(names="Teacher", last_names="Two", email="t2@test.com", document_number="222", birth_date=date(1980, 1, 1))
        self.user_t2 = User.objects.create_user(person=self.person_t2, password="test_password_123")
        UserRole.objects.create(user=self.user_t2, role=self.role_docente)

        # Estudiante 1
        self.person_s1 = Person.objects.create(names="Student", last_names="One", email="s1@test.com", document_number="333", birth_date=date(1980, 1, 1))
        self.user_s1 = User.objects.create_user(person=self.person_s1, password="test_password_123")
        UserRole.objects.create(user=self.user_s1, role=self.role_estudiante)
        self.student_1 = Student.objects.create(user=self.user_s1, student_code="S001")
        self.enrollment_1 = Enrollment.objects.create(
            student=self.student_1, section=self.section, enrollment_status="ACT"
        )

        # Estudiante 2
        self.person_s2 = Person.objects.create(names="Student", last_names="Two", email="s2@test.com", document_number="444", birth_date=date(1980, 1, 1))
        self.user_s2 = User.objects.create_user(person=self.person_s2, password="test_password_123")
        UserRole.objects.create(user=self.user_s2, role=self.role_estudiante)
        self.student_2 = Student.objects.create(user=self.user_s2, student_code="S002")
        self.enrollment_2 = Enrollment.objects.create(
            student=self.student_2, section=self.section, enrollment_status="ACT"
        )

        # Kinship for representatives
        self.kinship_padre = Kinship.objects.create(code="PADRE", name="Padre")

        # Representante (vinculado a Estudiante 1 únicamente)
        self.person_rep = Person.objects.create(names="Parent", last_names="One", email="rep@test.com", document_number="555", birth_date=date(1980, 1, 1))
        self.user_rep = User.objects.create_user(person=self.person_rep, password="test_password_123")
        UserRole.objects.create(user=self.user_rep, role=self.role_representante)
        StudentRepresentative.objects.create(student=self.student_1, user=self.user_rep, kinship=self.kinship_padre, is_primary=True)

        # 5. Crear Asignación y Estructura Académica para Docente 1
        self.subject = Subject.objects.create(name="Matemáticas")
        self.subject_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade, weekly_hours=4
        )
        self.subject_offering = SubjectOffering.objects.create(
            section=self.section, subject_academic_config=self.subject_config
        )
        self.tss_1 = TeacherSubjectSection.objects.create(user=self.user_t1, subject_offering=self.subject_offering)
        
        # Asignación ficticia para Docente 2
        self.tss_2 = TeacherSubjectSection.objects.create(user=self.user_t2, subject_offering=self.subject_offering)

        from apps.academic.models import AcademicPeriod
        self.activity_type = ActivityType.objects.create(code="TAREA", name="Tarea")
        self.activity_type2 = ActivityType.objects.create(code="EXAMEN", name="Examen")
        self.academic_period = AcademicPeriod.objects.create(
            school_year=self.school_year, name="Primer Quimestre", start_date="2026-01-01", end_date="2026-06-30")
        self.eval_block = EvaluationBlock.objects.create(
            academic_period=self.academic_period,
            subject_offering=self.subject_offering,
            name="Bloque 1",
            weight_percentage=50.00,
            block_type="FORMATIVA"
        )
        self.block_comp = BlockComponent.objects.create(
            evaluation_block=self.eval_block, name="Tareas", internal_weight=100.00
        )
        self.activity_1 = EvaluativeActivity.objects.create(
            block_component=self.block_comp, teacher_subject_section=self.tss_1,
            title="Tarea de Fracciones", activity_type=self.activity_type, max_score=10, internal_weight=100.00, due_date="2026-05-01"
        )
        self.activity_2 = EvaluativeActivity.objects.create(
            block_component=self.block_comp, teacher_subject_section=self.tss_2,
            title="Examen Docente 2", activity_type=self.activity_type2, max_score=10, internal_weight=100.00, due_date="2026-05-02"
        )
        # Nota para Estudiante 1 (creada por Docente 1)
        self.note_s1 = StudentNote.objects.create(
            enrollment=self.enrollment_1, evaluative_activity=self.activity_1, numeric_score=9.50
        )

        # Nota para Estudiante 2 (creada por Docente 2)
        self.note_s2 = StudentNote.objects.create(
            enrollment=self.enrollment_2, evaluative_activity=self.activity_2, numeric_score=8.00
        )

    # ─── Pruebas RLS Docente ──────────────────────────────────────────────────

    def test_teacher_only_views_their_assigned_courses(self):
        """Docente 1 solo puede ver su propia asignación académica (tss_1) y no la del Docente 2 (tss_2)"""
        self.client.force_authenticate(user=self.user_t1)
        response = self.client.get("/api/academic/teacher-subject-section/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar la respuesta formateada por StandardResponseRenderer {"ok": True, "data": ...}
        json_data = response.json()

        # Extraer correctamente los resultados de la respuesta con doble envoltura
        if "data" in json_data and isinstance(json_data["data"], dict) and "data" in json_data["data"]:
            results = json_data["data"]["data"]["results"]
        elif "data" in json_data and isinstance(json_data["data"], dict) and "results" in json_data["data"]:
            results = json_data["data"]["results"]
        elif "data" in json_data and isinstance(json_data["data"], list):
            results = json_data["data"]
        else:
            results = json_data.get("data", [])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.tss_1.id)

    def test_teacher_only_views_their_student_notes(self):
        """Docente 1 solo puede ver las calificaciones de sus propios cursos y actividades"""
        self.client.force_authenticate(user=self.user_t1)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json().get("data", [])
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.note_s1.id)

    # ─── Pruebas RLS Representante ────────────────────────────────────────────

    def test_representative_only_views_their_represented_student_notes(self):
        """Representante solo puede ver las notas de su representado (Estudiante 1) y no de otros (Estudiante 2)"""
        self.client.force_authenticate(user=self.user_rep)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json().get("data", [])
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.note_s1.id)

    # ─── Pruebas RLS Estudiante ───────────────────────────────────────────────

    def test_student_only_views_their_own_notes(self):
        """Estudiante 1 solo puede ver sus propias notas y no las de Estudiante 2"""
        self.client.force_authenticate(user=self.user_s1)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json().get("data", [])
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.note_s1.id)
