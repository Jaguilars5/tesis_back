from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (PeriodType,
    AcademicPeriod, Subject, SubjectAcademicConfig, SubjectOffering, TeacherSubjectSection,
)
from apps.behavior.models import (
    BehaviorEvaluation, ConductIncident,
    IncidentType, Severity,
)
from apps.behavior.repositories.behavior_repository import BehaviorEvaluationRepository
from apps.behavior.repositories.conduct_incident_repository import ConductIncidentRepository
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import QualitativeScale
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment


class BehaviorRepositoryTest(TestCase):
    """Tests para los repositorios del módulo behavior."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create( start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year, name="P1",
            start_date=date(2025, 1, 1), end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="7",
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemática", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade,
            weekly_hours=5,
        )
        self.offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.user = create_test_user(
            email="teacher@test.com", dni="0102030405",
            names="Ana", last_names="Perez",
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan", last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status="ACT",
        )
        self.qualitative_scale = QualitativeScale.objects.create(
            code="MB", description="Muy Buena",
            numeric_equivalence=Decimal("9.00"),
        )
        self.severity_leve = Severity.objects.create(
            code="LEVE", name="Falta leve",
        )
        self.severity_moderada = Severity.objects.create(
            code="MODERADA", name="Falta moderada",
        )
        self.severity_grave = Severity.objects.create(
            code="GRAVE", name="Falta grave",
        )
        self.severity_muy_grave = Severity.objects.create(
            code="MUY_GRAVE", name="Falta muy grave",
        )
        self.incident_type = IncidentType.objects.create(
            code="INDISCIPLINA", name="Indisciplina",
        )

    def test_incident_type_create(self):
        obj = IncidentType.objects.create(code="BULLYING", name="Acoso Escolar")
        self.assertEqual(obj.name, "Acoso Escolar")

    def test_incident_type_get_by_id(self):
        it = IncidentType.objects.create(code="FIGHT", name="Pelea")
        result = IncidentType.objects.get(pk=it.pk)
        self.assertEqual(result.code, "FIGHT")

    def test_incident_type_delete(self):
        it = IncidentType.objects.create(code="TEMP", name="Temp")
        pk = it.pk
        IncidentType.objects.filter(pk=pk).delete()
        self.assertFalse(IncidentType.objects.filter(pk=pk).exists())

    def test_behavior_eval_create(self):
        obj = BehaviorEvaluationRepository.create(
            enrollment=self.enrollment, academic_period=self.period,
            calculated_scale=self.qualitative_scale,
        )
        self.assertEqual(obj.calculated_scale.code, "MB")

    def test_behavior_eval_get_by_id(self):
        be = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            calculated_scale=self.qualitative_scale,
        )
        result = BehaviorEvaluationRepository.get_by_id(be.pk)
        self.assertEqual(result.calculated_scale, self.qualitative_scale)

    def test_behavior_eval_get_all_ordering(self):
        period2 = AcademicPeriod.objects.create(
            school_year=self.school_year, name="P2",
            start_date=date(2025, 4, 1), end_date=date(2025, 6, 30),
        )
        be1 = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            calculated_scale=self.qualitative_scale,
        )
        be2 = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=period2,
            calculated_scale=self.qualitative_scale,
        )
        results = BehaviorEvaluationRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, be2.pk)

    def test_behavior_eval_update(self):
        be = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            calculated_scale=self.qualitative_scale,
        )
        updated = BehaviorEvaluationRepository.update(
            be.pk, general_observation="Mejorando",
        )
        self.assertEqual(updated.general_observation, "Mejorando")

    def test_behavior_eval_delete(self):
        be = BehaviorEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            calculated_scale=self.qualitative_scale,
        )
        pk = be.pk
        BehaviorEvaluationRepository.delete(pk)
        self.assertFalse(BehaviorEvaluation.objects.filter(pk=pk).exists())

    def test_conduct_incident_create(self):
        obj = ConductIncidentRepository.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_grave,
            incident_type=self.incident_type,
            description="Incidente de prueba",
        )
        self.assertEqual(obj.severity, self.severity_grave)

    def test_conduct_incident_get_by_id(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_moderada,
            incident_type=self.incident_type,
        )
        result = ConductIncidentRepository.get_by_id(ci.pk)
        self.assertEqual(result.severity, self.severity_moderada)

    def test_conduct_incident_get_all_ordering(self):
        ci1 = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_leve,
            incident_type=self.incident_type,
        )
        ci2 = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 3, 1), severity=self.severity_muy_grave,
            incident_type=self.incident_type,
        )
        results = ConductIncidentRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, ci2.pk)

    def test_conduct_incident_update(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_moderada,
            incident_type=self.incident_type,
        )
        updated = ConductIncidentRepository.update(ci.pk, severity=self.severity_grave)
        self.assertEqual(updated.severity, self.severity_grave)

    def test_conduct_incident_delete(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_leve,
            incident_type=self.incident_type,
        )
        pk = ci.pk
        ConductIncidentRepository.delete(pk)
        self.assertFalse(ConductIncident.objects.filter(pk=pk).exists())

    def test_conduct_incident_get_by_enrollment_and_period(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_grave,
            incident_type=self.incident_type,
        )
        results = ConductIncidentRepository.get_by_enrollment_and_period(
            self.enrollment.pk, self.period.pk,
        )
        self.assertIn(ci, results)

    def test_conduct_incident_get_severe_by_enrollment(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_moderada,
            incident_type=self.incident_type,
        )
        severe = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 3, 1), severity=self.severity_muy_grave,
            incident_type=self.incident_type,
        )
        results = ConductIncidentRepository.get_severe_by_enrollment(
            self.enrollment.pk, severity_codes=["GRAVE", "MUY_GRAVE"],
        )
        self.assertIn(severe, results)
        self.assertEqual(len(results), 1)

    def test_conduct_incident_list_by_filters(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_grave,
            incident_type=self.incident_type,
        )
        results = ConductIncidentRepository.list_by_filters(
            student_id=self.student.pk,
        )
        self.assertEqual(results.count(), 1)

    def test_conduct_incident_list_by_filters_with_severity(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,

            incident_date=date(2025, 2, 15), severity=self.severity_grave,
            incident_type=self.incident_type,
        )
        results = ConductIncidentRepository.list_by_filters(
            student_id=self.student.pk, severity=self.severity_grave,
        )
        self.assertEqual(results.count(), 1)