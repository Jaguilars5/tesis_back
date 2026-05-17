from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    Academic_Period,
    Config_Academic,
    Section,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import (
    ClassAssignment,
    EvaluationCriteria,
    EvaluationMacro,
    EvaluationSubcriteria,
    GradeChangeHistory,
    GradeType,
    StudentNote,
)
from apps.grading.services.evaluation_service import EvaluationService
from apps.institutions.models import AcademicGrade, AcademicLevel, Institution, School_Year
from apps.students.models import Enrollment, EnrollmentStatus


class EvaluationHierarchyTest(TestCase):
    """Tests para la jerarquia EvaluationMacro > EvaluationCriteria > EvaluationSubcriteria > ClassAssignment."""

    def setUp(self):
        institution = Institution.objects.create(
            name="Institucion",
            code="INST-1",
            address="Calle 1",
            city="Quito",
        )
        school_year = School_Year.objects.create(
            institution=institution,
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        config = Config_Academic.objects.create(
            school_year=school_year,
            institution=institution,
            name="Año lectivo",
            academic_period_type="trimestre",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=config,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
            institution=institution,
        )
        academic_level = AcademicLevel.objects.create(
            institution=institution, name="Primaria",
        )
        academic_grade = AcademicGrade.objects.create(
            academic_level=academic_level, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year, timing_regime=None,
            academic_grade=academic_grade, parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan",
            last_names="Lopez", birth_date=date(2010, 1, 1),
        )

        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status=self.status,
        )

    def _create_full_hierarchy(self):
        macro = EvaluationMacro.objects.create(
            academic_period=self.period,
            name="Macro 1",
            weight_percentage=Decimal("100.00"),
        )
        criteria = EvaluationCriteria.objects.create(
            evaluation_macro=macro,
            name="Criterio 1",
            internal_weight=Decimal("100.00"),
        )
        subcriteria = EvaluationSubcriteria.objects.create(
            evaluation_criteria=criteria,
            name="Subcriterio 1",
            internal_weight=Decimal("100.00"),
        )
        assignment = ClassAssignment.objects.create(
            evaluation_subcriteria=subcriteria,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            max_score=Decimal("20"),
            due_date=date(2025, 2, 1),
        )
        return macro, criteria, subcriteria, assignment

    def test_create_evaluation_macro(self):
        macro = EvaluationMacro.objects.create(
            academic_period=self.period,
            name="Macro 1",
            weight_percentage=Decimal("50.00"),
        )
        self.assertEqual(macro.name, "Macro 1")
        self.assertEqual(macro.weight_percentage, Decimal("50.00"))

    def test_create_evaluation_criteria(self):
        macro = EvaluationMacro.objects.create(
            academic_period=self.period,
            name="Macro 1",
            weight_percentage=Decimal("100.00"),
        )
        criteria = EvaluationCriteria.objects.create(
            evaluation_macro=macro,
            name="Criterio 1",
            internal_weight=Decimal("50.00"),
        )
        self.assertEqual(criteria.name, "Criterio 1")
        self.assertEqual(criteria.internal_weight, Decimal("50.00"))
        self.assertEqual(criteria.evaluation_macro, macro)

    def test_create_evaluation_subcriteria(self):
        macro = EvaluationMacro.objects.create(
            academic_period=self.period,
            name="Macro 1",
            weight_percentage=Decimal("100.00"),
        )
        criteria = EvaluationCriteria.objects.create(
            evaluation_macro=macro,
            name="Criterio 1",
            internal_weight=Decimal("100.00"),
        )
        subcriteria = EvaluationSubcriteria.objects.create(
            evaluation_criteria=criteria,
            name="Subcriterio 1",
            internal_weight=Decimal("100.00"),
        )
        self.assertEqual(subcriteria.name, "Subcriterio 1")
        self.assertEqual(subcriteria.evaluation_criteria, criteria)

    def test_create_class_assignment(self):
        macro, criteria, subcriteria, assignment = self._create_full_hierarchy()

        self.assertEqual(assignment.title, "Examen")
        self.assertEqual(assignment.max_score, Decimal("20"))
        self.assertEqual(assignment.evaluation_subcriteria, subcriteria)

    def test_grade_change_history_creation(self):
        macro, criteria, subcriteria, assignment = self._create_full_hierarchy()
        grade_type = GradeType.objects.create(code="NUM", name="Numerica")

        note = StudentNote.objects.create(
            enrollment=self.enrollment,
            class_assignment=assignment,
            grade_type=grade_type,
            numeric_score=Decimal("15"),
        )

        history = GradeChangeHistory.objects.create(
            student_note=note,
            modified_by_user=self.user,
            previous_score=Decimal("15"),
            new_score=Decimal("18"),
            reason="Correccion",
        )

        self.assertEqual(history.previous_score, Decimal("15"))
        self.assertEqual(history.new_score, Decimal("18"))
        self.assertEqual(history.reason, "Correccion")


class EvaluationServiceTest(TestCase):
    """Tests para EvaluationService."""

    def setUp(self):
        institution = Institution.objects.create(
            name="Institucion",
            code="INST-1",
            address="Calle 1",
            city="Quito",
        )
        school_year = School_Year.objects.create(
            institution=institution,
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        config = Config_Academic.objects.create(
            school_year=school_year,
            institution=institution,
            name="Año lectivo",
            academic_period_type="trimestre",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=config,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
            institution=institution,
        )
        academic_level = AcademicLevel.objects.create(
            institution=institution, name="Primaria",
        )
        academic_grade = AcademicGrade.objects.create(
            academic_level=academic_level, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year, timing_regime=None,
            academic_grade=academic_grade, parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan",
            last_names="Lopez", birth_date=date(2010, 1, 1),
        )

        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status=self.status,
        )

        self.macro = EvaluationMacro.objects.create(
            academic_period=self.period,
            name="Macro 1",
            weight_percentage=Decimal("100.00"),
        )
        self.criteria = EvaluationCriteria.objects.create(
            evaluation_macro=self.macro,
            name="Criterio 1",
            internal_weight=Decimal("100.00"),
        )
        self.subcriteria = EvaluationSubcriteria.objects.create(
            evaluation_criteria=self.criteria,
            name="Subcriterio 1",
            internal_weight=Decimal("100.00"),
        )
        self.assignment = ClassAssignment.objects.create(
            evaluation_subcriteria=self.subcriteria,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            max_score=Decimal("10"),
            due_date=date(2025, 2, 1),
        )
        self.grade_type = GradeType.objects.create(code="NUM", name="Numerica")

    def test_calculate_macro_grade(self):
        StudentNote.objects.create(
            enrollment=self.enrollment,
            class_assignment=self.assignment,
            grade_type=self.grade_type,
            numeric_score=Decimal("8"),
        )

        grade = EvaluationService.calculate_macro_grade(
            self.enrollment, self.macro
        )

        self.assertIsNotNone(grade)
        expected = Decimal("8.00")
        self.assertEqual(grade, expected)

    def test_calculate_macro_grade_no_notes(self):
        grade = EvaluationService.calculate_macro_grade(
            self.enrollment, self.macro
        )

        self.assertIsNone(grade)

    def test_calculate_macro_grade_multiple_assignments(self):
        subcriteria2 = EvaluationSubcriteria.objects.create(
            evaluation_criteria=self.criteria,
            name="Subcriterio 2",
            internal_weight=Decimal("100.00"),
        )
        assignment2 = ClassAssignment.objects.create(
            evaluation_subcriteria=subcriteria2,
            teacher_subject_section=self.teacher_subject_section,
            title="Tarea",
            max_score=Decimal("10"),
            due_date=date(2025, 2, 15),
        )
        StudentNote.objects.create(
            enrollment=self.enrollment,
            class_assignment=self.assignment,
            grade_type=self.grade_type,
            numeric_score=Decimal("8"),
        )
        StudentNote.objects.create(
            enrollment=self.enrollment,
            class_assignment=assignment2,
            grade_type=self.grade_type,
            numeric_score=Decimal("6"),
        )

        grade = EvaluationService.calculate_macro_grade(
            self.enrollment, self.macro
        )

        self.assertIsNotNone(grade)

    def test_get_grade_hierarchy(self):
        hierarchy = EvaluationService.get_grade_hierarchy(self.assignment)

        self.assertEqual(hierarchy["class_assignment"], self.assignment)
        self.assertEqual(hierarchy["subcriteria"], self.subcriteria)
        self.assertEqual(hierarchy["criteria"], self.criteria)
        self.assertEqual(hierarchy["macro"], self.macro)
        self.assertEqual(hierarchy["academic_period"], self.period)

    def test_create_grade_change_history(self):
        note = StudentNote.objects.create(
            enrollment=self.enrollment,
            class_assignment=self.assignment,
            grade_type=self.grade_type,
            numeric_score=Decimal("5"),
        )

        history = EvaluationService.create_grade_change_history(
            student_note=note,
            new_score=Decimal("9"),
            user=self.user,
            reason="Error de captura",
        )

        self.assertIsNotNone(history.id)
        self.assertEqual(history.previous_score, Decimal("5"))
        self.assertEqual(history.new_score, Decimal("9"))
        self.assertEqual(history.reason, "Error de captura")
        note.refresh_from_db()
        self.assertEqual(note.numeric_score, Decimal("9"))
        self.assertTrue(note.manually_overridden)
