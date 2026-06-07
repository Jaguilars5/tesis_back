from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    Academic_Period, Subject, SubjectAcademicConfig, SubjectOffering, Teacher_Subject_Section,
)
from apps.attendance.models import (
    Attendance, AttendanceStatus, BehaviorEvaluation, ConductIncident, IncidentType,
    SkillEvaluation, SocioemotionalSkill,
)
from apps.attendance.repositories.attendance_repository import AttendanceRepository
from apps.attendance.repositories.attendance_status_repository import AttendanceStatusRepository
from apps.attendance.repositories.behavior_evaluation_repository import BehaviorEvaluationRepository
from apps.attendance.repositories.conduct_incident_repository import ConductIncidentRepository
from apps.attendance.repositories.incident_type_repository import IncidentTypeRepository
from apps.attendance.repositories.skill_evaluation_repository import SkillEvaluationRepository
from apps.attendance.repositories.socioemotional_skill_repository import SocioemotionalSkillRepository
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import QualitativeScale
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceRepositoryTest(TestCase):
    """Tests para los repositorios del módulo attendance."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2025", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        self.period = Academic_Period.objects.create(
            school_year=self.school_year, name="P1",
            start_date=date(2025, 1, 1), end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemática", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        self.offering = SubjectOffering.objects.create(
            school_year=self.school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.user = create_test_user(
            email="teacher@test.com", dni="0102030405",
            names="Ana", last_names="Perez",
        )
        self.tss = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan", last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        self.status_enr, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"},
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status=self.status_enr,
        )
        self.qualitative_scale = QualitativeScale.objects.create(
            code="MB", description="Muy Buena",
            numeric_equivalence=Decimal("9.00"),
        )

    # --- AttendanceStatusRepository (simple) ---

    def test_attendance_status_create(self):
        obj = AttendanceStatusRepository.create(code="P", name="Presente")
        self.assertEqual(obj.name, "Presente")

    def test_attendance_status_get_by_id(self):
        st = AttendanceStatus.objects.create(code="P", name="Presente")
        result = AttendanceStatusRepository.get_by_id(st.pk)
        self.assertEqual(result.code, "P")

    def test_attendance_status_get_all(self):
        AttendanceStatus.objects.create(code="P", name="Presente")
        AttendanceStatus.objects.create(code="A", name="Ausente")
        self.assertEqual(AttendanceStatusRepository.get_all(active_only=False).count(), 2)

    def test_attendance_status_update(self):
        st = AttendanceStatus.objects.create(code="P", name="Presente")
        updated = AttendanceStatusRepository.update(st.pk, name="Presentó")
        self.assertEqual(updated.name, "Presentó")

    def test_attendance_status_delete(self):
        st = AttendanceStatus.objects.create(code="TMP", name="Temporal")
        pk = st.pk
        AttendanceStatusRepository.delete(pk)
        self.assertFalse(AttendanceStatus.objects.filter(pk=pk).exists())

    def test_attendance_status_exists(self):
        st = AttendanceStatus.objects.create(code="P", name="Presente")
        self.assertTrue(AttendanceStatusRepository.exists(pk=st.pk))
        self.assertFalse(AttendanceStatusRepository.exists(pk=99999))

    # --- IncidentTypeRepository (simple) ---

    def test_incident_type_create(self):
        obj = IncidentTypeRepository.create(code="BULLYING", name="Acoso Escolar")
        self.assertEqual(obj.name, "Acoso Escolar")

    def test_incident_type_get_by_id(self):
        it = IncidentType.objects.create(code="FIGHT", name="Pelea")
        result = IncidentTypeRepository.get_by_id(it.pk)
        self.assertEqual(result.code, "FIGHT")

    def test_incident_type_delete(self):
        it = IncidentType.objects.create(code="TEMP", name="Temp")
        pk = it.pk
        IncidentTypeRepository.delete(pk)
        self.assertFalse(IncidentType.objects.filter(pk=pk).exists())

    # --- SocioemotionalSkillRepository (simple) ---

    def test_socioemotional_skill_create(self):
        obj = SocioemotionalSkillRepository.create(
            code="EMPATIA", name="Empatía",
        )
        self.assertEqual(obj.name, "Empatía")

    def test_socioemotional_skill_get_by_id(self):
        sk = SocioemotionalSkill.objects.create(code="RESPETO", name="Respeto")
        result = SocioemotionalSkillRepository.get_by_id(sk.pk)
        self.assertEqual(result.code, "RESPETO")

    def test_socioemotional_skill_inactive(self):
        sk = SocioemotionalSkill.objects.create(code="INACT", name="Inactiva", active=False)
        results_active = SocioemotionalSkillRepository.get_all(active_only=True)
        self.assertNotIn(sk, results_active)

    # --- BehaviorEvaluationRepository ---

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
        period2 = Academic_Period.objects.create(
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

    # --- SkillEvaluationRepository ---

    def test_skill_eval_create(self):
        sk = SocioemotionalSkill.objects.create(code="EMPATIA", name="Empatía")
        obj = SkillEvaluationRepository.create(
            enrollment=self.enrollment, academic_period=self.period,
            socioemotional_skill=sk,
            qualitative_scale=self.qualitative_scale,
        )
        self.assertEqual(obj.socioemotional_skill.code, "EMPATIA")

    def test_skill_eval_get_by_id(self):
        sk = SocioemotionalSkill.objects.create(code="RESP", name="Responsabilidad")
        se = SkillEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            socioemotional_skill=sk,
            qualitative_scale=self.qualitative_scale,
        )
        result = SkillEvaluationRepository.get_by_id(se.pk)
        self.assertEqual(result.socioemotional_skill.code, "RESP")

    def test_skill_eval_get_all_ordering(self):
        sk1 = SocioemotionalSkill.objects.create(code="TOL", name="Tolerancia")
        sk2 = SocioemotionalSkill.objects.create(code="EMP", name="Empatía")
        se1 = SkillEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            socioemotional_skill=sk1,
            qualitative_scale=self.qualitative_scale,
        )
        se2 = SkillEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            socioemotional_skill=sk2,
            qualitative_scale=self.qualitative_scale,
        )
        results = SkillEvaluationRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, se2.pk)

    def test_skill_eval_delete(self):
        sk = SocioemotionalSkill.objects.create(code="TEMP", name="Temp")
        se = SkillEvaluation.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            socioemotional_skill=sk,
            qualitative_scale=self.qualitative_scale,
        )
        pk = se.pk
        SkillEvaluationRepository.delete(pk)
        self.assertFalse(SkillEvaluation.objects.filter(pk=pk).exists())

    # --- ConductIncidentRepository ---

    def test_conduct_incident_create(self):
        obj = ConductIncidentRepository.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=3,
            description="Incidente de prueba",
        )
        self.assertEqual(obj.severity, 3)

    def test_conduct_incident_get_by_id(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=2,
        )
        result = ConductIncidentRepository.get_by_id(ci.pk)
        self.assertEqual(result.severity, 2)

    def test_conduct_incident_get_all_ordering(self):
        ci1 = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=1,
        )
        ci2 = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 3, 1), severity=4,
        )
        results = ConductIncidentRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, ci2.pk)

    def test_conduct_incident_update(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=2,
        )
        updated = ConductIncidentRepository.update(ci.pk, severity=5)
        self.assertEqual(updated.severity, 5)

    def test_conduct_incident_delete(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=1,
        )
        pk = ci.pk
        ConductIncidentRepository.delete(pk)
        self.assertFalse(ConductIncident.objects.filter(pk=pk).exists())

    def test_conduct_incident_get_by_enrollment_and_period(self):
        ci = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=3,
        )
        results = ConductIncidentRepository.get_by_enrollment_and_period(
            self.enrollment.pk, self.period.pk,
        )
        self.assertIn(ci, results)

    def test_conduct_incident_get_severe_by_enrollment(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=2,
        )
        severe = ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 3, 1), severity=4,
        )
        results = ConductIncidentRepository.get_severe_by_enrollment(
            self.enrollment.pk, severity_threshold=3,
        )
        self.assertIn(severe, results)
        self.assertEqual(len(results), 1)

    def test_conduct_incident_list_by_filters(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=3,
        )
        results = ConductIncidentRepository.list_by_filters(
            student_id=self.student.pk,
        )
        self.assertEqual(results.count(), 1)

    def test_conduct_incident_list_by_filters_with_severity(self):
        ConductIncident.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            reported_by_user=self.user,
            incident_date=date(2025, 2, 15), severity=3,
        )
        results = ConductIncidentRepository.list_by_filters(
            student_id=self.student.pk, severity=3,
        )
        self.assertEqual(results.count(), 1)

    # --- AttendanceRepository ---

    def test_attendance_create(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        obj = AttendanceRepository.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        self.assertEqual(obj.attendance_date, date(2025, 2, 1))

    def test_attendance_get_by_id(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        result = AttendanceRepository.get_by_id(att.pk)
        self.assertEqual(result.attendance_date, date(2025, 2, 1))

    def test_attendance_get_all_ordering(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att1 = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        att2 = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 2),
            attendance_status=att_status,
        )
        results = AttendanceRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, att2.pk)

    def test_attendance_update(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        updated = AttendanceRepository.update(att.pk, observation="Llegó tarde")
        self.assertEqual(updated.observation, "Llegó tarde")

    def test_attendance_delete(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        pk = att.pk
        AttendanceRepository.delete(pk)
        self.assertFalse(Attendance.objects.filter(pk=pk).exists())

    def test_attendance_exists(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        self.assertTrue(AttendanceRepository.exists(pk=att.pk))
        self.assertFalse(AttendanceRepository.exists(pk=99999))

    def test_attendance_get_by_unique_key(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        result = AttendanceRepository.get_by_unique_key(
            self.enrollment.pk, self.tss.pk, date(2025, 2, 1),
        )
        self.assertIsNotNone(result)

    def test_attendance_get_by_unique_key_not_found(self):
        result = AttendanceRepository.get_by_unique_key(99999, 99999, date(2025, 1, 1))
        self.assertIsNone(result)

    def test_attendance_get_by_enrollment_and_period(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        results = AttendanceRepository.get_by_enrollment_and_period(
            self.enrollment.pk, self.period.pk,
        )
        self.assertIn(att, results)

    def test_attendance_get_absences_summary(self):
        p_status = AttendanceStatus.objects.create(code="P", name="Presente")
        a_status = AttendanceStatus.objects.create(code="A", name="Ausente")
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 1),
            attendance_status=p_status, absence_type="none",
        )
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 2),
            attendance_status=a_status, absence_type="unjustified",
        )
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 3),
            attendance_status=a_status, absence_type="justified",
        )
        summary = AttendanceRepository.get_absences_summary(
            self.enrollment.pk, self.period.pk,
        )
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["justified"], 1)
        self.assertEqual(summary["unjustified"], 1)
        self.assertEqual(summary["late"], 0)

    def test_attendance_list_by_filters(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        results = AttendanceRepository.list_by_filters(
            student_id=self.student.pk,
        )
        self.assertEqual(results.count(), 1)

    def test_attendance_list_by_filters_with_period(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        results = AttendanceRepository.list_by_filters(
            academic_period_id=self.period.pk,
        )
        self.assertEqual(results.count(), 1)
