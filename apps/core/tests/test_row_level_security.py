from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, User, UserRole, Person
from apps.core.tests.helpers import create_test_user
from apps.academic.models import SubjectOffering, Subject, SubjectAcademicConfig, Teacher_Subject_Section
from apps.institutions.models import Section, School_Year, AcademicGrade, AcademicLevel
from apps.students.models import Student, Student_Representative, Enrollment, EnrollmentStatus
from apps.grading.models import EvaluativeActivity, StudentNote, ComponentIndicator, BlockComponent, EvaluationBlock, GradeType


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
        self.school_year = School_Year.objects.create(
            name="Año Test 2026", start_date="2026-01-01", end_date="2026-12-31"
        )
        self.academic_level = AcademicLevel.objects.create(name="Educación General Básica")
        self.academic_grade = AcademicGrade.objects.create(
            name="Octavo Grado", sequence_order=1, academic_level=self.academic_level
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30
        )
        self.enrollment_status = EnrollmentStatus.objects.create(code="ACT", name="Activa")

        # 3. Crear Personas e Hilos de Usuarios
        # Docente 1
        self.person_t1 = Person.objects.create(names="Teacher", last_names="One", email="t1@test.com", document_number="111")
        self.user_t1 = User.objects.create_user(person=self.person_t1, password="test_password_123", user_type="DOCENTE")
        UserRole.objects.create(user=self.user_t1, role=self.role_docente)

        # Docente 2
        self.person_t2 = Person.objects.create(names="Teacher", last_names="Two", email="t2@test.com", document_number="222")
        self.user_t2 = User.objects.create_user(person=self.person_t2, password="test_password_123", user_type="DOCENTE")
        UserRole.objects.create(user=self.user_t2, role=self.role_docente)

        # Estudiante 1
        self.person_s1 = Person.objects.create(names="Student", last_names="One", email="s1@test.com", document_number="333")
        self.user_s1 = User.objects.create_user(person=self.person_s1, password="test_password_123", user_type="ESTUDIANTE")
        UserRole.objects.create(user=self.user_s1, role=self.role_estudiante)
        self.student_1 = Student.objects.create(person=self.person_s1, student_code="S001")
        self.enrollment_1 = Enrollment.objects.create(
            student=self.student_1, section=self.section, school_year=self.school_year, enrollment_status=self.enrollment_status
        )

        # Estudiante 2
        self.person_s2 = Person.objects.create(names="Student", last_names="Two", email="s2@test.com", document_number="444")
        self.user_s2 = User.objects.create_user(person=self.person_s2, password="test_password_123", user_type="ESTUDIANTE")
        UserRole.objects.create(user=self.user_s2, role=self.role_estudiante)
        self.student_2 = Student.objects.create(person=self.person_s2, student_code="S002")
        self.enrollment_2 = Enrollment.objects.create(
            student=self.student_2, section=self.section, school_year=self.school_year, enrollment_status=self.enrollment_status
        )

        # Representante (vinculado a Estudiante 1 únicamente)
        self.person_rep = Person.objects.create(names="Parent", last_names="One", email="rep@test.com", document_number="555")
        self.user_rep = User.objects.create_user(person=self.person_rep, password="test_password_123", user_type="REPRESENTANTE")
        UserRole.objects.create(user=self.user_rep, role=self.role_representante)
        Student_Representative.objects.create(student=self.student_1, person=self.person_rep, kinship="Padre", is_primary=True)

        # 4. Crear Asignación y Estructura Académica para Docente 1
        self.subject = Subject.objects.create(name="Matemáticas")
        self.subject_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade, weekly_hours=4, pedagogical_order=1
        )
        self.subject_offering = SubjectOffering.objects.create(
            section=self.section, school_year=self.school_year, subject_academic_config=self.subject_config
        )
        self.tss_1 = Teacher_Subject_Section.objects.create(user=self.user_t1, subject_offering=self.subject_offering)
        
        # Asignación ficticia para Docente 2
        self.tss_2 = Teacher_Subject_Section.objects.create(user=self.user_t2, subject_offering=self.subject_offering)

        # 5. Crear Notas y Calificaciones
        from apps.academic.models import Academic_Period
        self.academic_period = Academic_Period.objects.create(
            school_year=self.school_year, name="Primer Quimestre", start_date="2026-01-01", end_date="2026-06-30"
        )
        self.eval_block = EvaluationBlock.objects.create(
            academic_period=self.academic_period, name="Bloque 1", weight_percentage=50.00, evaluation_type="FORMATIVA"
        )
        self.block_comp = BlockComponent.objects.create(
            evaluation_block=self.eval_block, name="Tareas", internal_weight=100.00
        )
        self.comp_ind = ComponentIndicator.objects.create(
            block_component=self.block_comp, name="Indicador Tarea 1", internal_weight=100.00
        )
        self.activity_1 = EvaluativeActivity.objects.create(
            component_indicator=self.comp_ind, teacher_subject_section=self.tss_1,
            title="Tarea de Fracciones", activity_type="TAREA", max_score=10, due_date="2026-05-01"
        )
        self.activity_2 = EvaluativeActivity.objects.create(
            component_indicator=self.comp_ind, teacher_subject_section=self.tss_2,
            title="Examen Docente 2", activity_type="EXAMEN", max_score=10, due_date="2026-05-02"
        )
        self.grade_type = GradeType.objects.create(code="NUM", name="Numérica")

        # Nota para Estudiante 1 (creada por Docente 1)
        self.note_s1 = StudentNote.objects.create(
            enrollment=self.enrollment_1, evaluative_activity=self.activity_1, grade_type=self.grade_type, numeric_score=9.50
        )

        # Nota para Estudiante 2 (creada por Docente 2)
        self.note_s2 = StudentNote.objects.create(
            enrollment=self.enrollment_2, evaluative_activity=self.activity_2, grade_type=self.grade_type, numeric_score=8.00
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
