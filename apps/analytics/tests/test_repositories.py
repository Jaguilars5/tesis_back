from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    Academic_Period, Subject, SubjectAcademicConfig, SubjectOffering, Teacher_Subject_Section,
)
from apps.accounts.models import User
from apps.analytics.models import (
    EarlyAlert, RiskFactor, StudentFeatureSnapshot, StudentRiskFactor, StudentRiskScore,
)
from apps.analytics.repositories.analytics_repo import (
    StudentRiskScoreRepository, StudentFeatureSnapshotRepository,
)
from apps.analytics.repositories.early_alert_repository import EarlyAlertRepository
from apps.core.repositories.base import BaseRepository
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AnalyticsRepositoryTest(TestCase):
    """Tests para los repositorios del módulo analytics."""

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
        Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan", last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"},
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section, enrollment_status=status,
        )

    # --- StudentRiskScoreRepository ---

    def test_student_risk_score_create(self):
        obj = StudentRiskScoreRepository.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            risk_score=Decimal("45.50"),
            risk_label="BAJO",
            model_version="v1.0",
        )
        self.assertEqual(obj.risk_score, Decimal("45.50"))
        self.assertEqual(obj.risk_label, "BAJO")
        self.assertEqual(obj.model_version, "v1.0")

    def test_student_risk_score_get_by_id(self):
        obj = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("30.00"), risk_label="BAJO",
        )
        result = StudentRiskScoreRepository.get_by_id(obj.pk)
        self.assertIsNotNone(result)
        self.assertEqual(result.pk, obj.pk)

    def test_student_risk_score_get_all_ordering(self):
        StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("10.00"), risk_label="BAJO",
        )
        s2 = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("90.00"), risk_label="ALTO",
        )
        results = StudentRiskScoreRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, s2.pk)

    def test_student_risk_score_update(self):
        obj = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("50.00"), risk_label="MEDIO",
        )
        updated = StudentRiskScoreRepository.update(obj.pk, risk_label="ALTO")
        self.assertEqual(updated.risk_label, "ALTO")

    def test_student_risk_score_delete(self):
        obj = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("20.00"), risk_label="BAJO",
        )
        pk = obj.pk
        StudentRiskScoreRepository.delete(pk)
        self.assertFalse(StudentRiskScore.objects.filter(pk=pk).exists())

    def test_student_risk_score_exists(self):
        obj = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("60.00"), risk_label="MEDIO",
        )
        self.assertTrue(StudentRiskScoreRepository.exists(pk=obj.pk))
        self.assertFalse(StudentRiskScoreRepository.exists(pk=99999))

    def test_student_risk_score_count(self):
        StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("10.00"), risk_label="BAJO",
        )
        StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("90.00"), risk_label="ALTO",
        )
        self.assertEqual(StudentRiskScoreRepository.count(), 2)

    def test_student_risk_score_get_latest_by_enrollment(self):
        obj = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("75.00"), risk_label="ALTO",
        )
        result = StudentRiskScoreRepository.get_latest_by_enrollment(self.enrollment.pk)
        self.assertEqual(result.pk, obj.pk)

    def test_student_risk_score_get_latest_by_student(self):
        obj = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("80.00"), risk_label="ALTO",
        )
        result = StudentRiskScoreRepository.get_latest_by_student(self.student.pk)
        self.assertEqual(result.pk, obj.pk)

    def test_student_risk_score_list_high_risk(self):
        StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("50.00"), risk_label="MEDIO",
        )
        high = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("85.00"), risk_label="ALTO",
        )
        results = StudentRiskScoreRepository.list_high_risk(self.period.pk, threshold=70)
        self.assertIn(high, results)
        self.assertEqual(len(results), 1)

    def test_create_score_method(self):
        obj = StudentRiskScoreRepository.create_score(
            enrollment_id=self.enrollment.pk,
            academic_period_id=self.period.pk,
            risk_score=Decimal("65.00"),
            risk_label="MEDIO",
            model_version="v2.0",
        )
        self.assertEqual(obj.risk_score, Decimal("65.00"))
        self.assertEqual(obj.risk_label, "MEDIO")

    # --- StudentFeatureSnapshotRepository ---

    def test_snapshot_create(self):
        obj = StudentFeatureSnapshotRepository.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            attendance_rate=Decimal("95.00"),
            unjustified_absences=0,
            justified_absences=2,
            residential_zone="Urbana",
        )
        self.assertEqual(obj.attendance_rate, Decimal("95.00"))
        self.assertEqual(obj.residential_zone, "Urbana")

    def test_snapshot_get_by_id(self):
        obj = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("90.00"),
        )
        result = StudentFeatureSnapshotRepository.get_by_id(obj.pk)
        self.assertIsNotNone(result)

    def test_snapshot_get_all_ordering(self):
        StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("80.00"),
        )
        s2 = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("95.00"),
        )
        results = StudentFeatureSnapshotRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, s2.pk)

    def test_snapshot_update(self):
        obj = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("70.00"),
        )
        updated = StudentFeatureSnapshotRepository.update(obj.pk, attendance_rate=Decimal("85.00"))
        self.assertEqual(updated.attendance_rate, Decimal("85.00"))

    def test_snapshot_delete(self):
        obj = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("50.00"),
        )
        pk = obj.pk
        StudentFeatureSnapshotRepository.delete(pk)
        self.assertFalse(StudentFeatureSnapshot.objects.filter(pk=pk).exists())

    def test_snapshot_get_by_enrollment_period(self):
        obj = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("88.00"),
        )
        result = StudentFeatureSnapshotRepository.get_by_enrollment_period(
            self.enrollment.pk, self.period.pk,
        )
        self.assertEqual(result.pk, obj.pk)

    def test_snapshot_get_by_student_period(self):
        obj = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            attendance_rate=Decimal("92.00"),
        )
        result = StudentFeatureSnapshotRepository.get_by_student_period(
            self.student.pk, self.period.pk,
        )
        self.assertEqual(result.pk, obj.pk)

    def test_create_snapshot_method(self):
        metrics = {
            "attendance_rate": Decimal("85.00"),
            "consecutive_absences_max": 3,
            "tardiness_count": 2,
            "failing_subjects_count": 1,
            "conduct_score": Decimal("8.50"),
            "severe_incidents_count": 0,
            "justified_absences": 1,
            "unjustified_absences": 0,
            "active_alerts": 0,
            "is_repeat": False,
            "has_special_needs": False,
            "residential_zone": "Urbana",
        }
        obj = StudentFeatureSnapshotRepository.create_snapshot(
            enrollment_id=self.enrollment.pk,
            academic_period_id=self.period.pk,
            metrics=metrics,
        )
        self.assertEqual(obj.attendance_rate, Decimal("85.00"))
        self.assertEqual(obj.consecutive_absences_max, 3)

    def test_create_snapshot_with_avg_grade_normalized_mapping(self):
        metrics = {
            "avg_grade_normalized": Decimal("7.50"),
            "consecutive_absences_max": 0,
            "tardiness_count": 0,
            "failing_subjects_count": 0,
            "conduct_score": Decimal("10.00"),
            "severe_incidents_count": 0,
        }
        obj = StudentFeatureSnapshotRepository.create_snapshot(
            enrollment_id=self.enrollment.pk,
            academic_period_id=self.period.pk,
            metrics=metrics,
        )
        self.assertEqual(obj.formative_avg_normalized, Decimal("7.50"))
        self.assertEqual(obj.summative_avg_normalized, Decimal("7.50"))

    # --- EarlyAlertRepository ---

    def test_early_alert_create(self):
        obj = EarlyAlertRepository.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            alert_type="low_attendance",
            description="Baja asistencia registrada",
            urgency_level="high",
        )
        self.assertEqual(obj.alert_type, "low_attendance")
        self.assertEqual(obj.urgency_level, "high")
        self.assertFalse(obj.attended)

    def test_early_alert_get_by_id(self):
        obj = EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="failing_grades", description="Notas bajas",
            urgency_level="medium",
        )
        result = EarlyAlertRepository.get_by_id(obj.pk)
        self.assertIsNotNone(result)

    def test_early_alert_get_all(self):
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="behavioral", description="Problemas de conducta",
            urgency_level="critical",
        )
        results = EarlyAlertRepository.get_all(active_only=False)
        self.assertEqual(results.count(), 1)

    def test_early_alert_update(self):
        obj = EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="dropout_risk", description="Riesgo de deserción",
            urgency_level="high",
        )
        updated = EarlyAlertRepository.update(obj.pk, attended=True)
        self.assertTrue(updated.attended)

    def test_early_alert_delete(self):
        obj = EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="socioemotional", description="Problemas socioemocionales",
            urgency_level="medium",
        )
        pk = obj.pk
        EarlyAlertRepository.delete(pk)
        self.assertFalse(EarlyAlert.objects.filter(pk=pk).exists())

    def test_early_alert_exists(self):
        obj = EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="low_attendance", description="Test",
            urgency_level="low",
        )
        self.assertTrue(EarlyAlertRepository.exists(pk=obj.pk))

    def test_early_alert_get_pending_alerts(self):
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="low_attendance", description="Sin atender",
            urgency_level="high", attended=False,
        )
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="failing_grades", description="Atendida",
            urgency_level="medium", attended=True,
        )
        pending = EarlyAlertRepository.get_pending_alerts()
        self.assertEqual(pending.count(), 1)

    def test_early_alert_get_pending_by_urgency(self):
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="low_attendance", description="Urgente",
            urgency_level="critical", attended=False,
        )
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="failing_grades", description="Media",
            urgency_level="medium", attended=False,
        )
        critical = EarlyAlertRepository.get_pending_alerts(urgency_level="critical")
        self.assertEqual(critical.count(), 1)

    def test_early_alert_get_by_enrollment(self):
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="dropout_risk", description="Alerta 1",
            urgency_level="high",
        )
        alerts = EarlyAlertRepository.get_by_enrollment(self.enrollment.pk)
        self.assertEqual(alerts.count(), 1)

    def test_early_alert_count_active_by_enrollment(self):
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="behavioral", description="Activa",
            urgency_level="high", attended=False,
        )
        EarlyAlert.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            alert_type="failing_grades", description="Atendida",
            urgency_level="medium", attended=True,
        )
        count = EarlyAlertRepository.count_active_by_enrollment(self.enrollment.pk)
        self.assertEqual(count, 1)

    # --- Direct RiskFactor CRUD (no dedicated repository) ---

    def test_risk_factor_create_and_get(self):
        obj = RiskFactor.objects.create(code="LOW_ATT", name="Baja Asistencia")
        result = RiskFactor.objects.get(pk=obj.pk)
        self.assertEqual(result.name, "Baja Asistencia")

    def test_risk_factor_update(self):
        obj = RiskFactor.objects.create(code="FAIL_GR", name="Notas Bajas")
        RiskFactor.objects.filter(pk=obj.pk).update(name="Calificaciones Bajas")
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Calificaciones Bajas")

    def test_risk_factor_delete(self):
        obj = RiskFactor.objects.create(code="BEHAV", name="Problemas de Conducta")
        pk = obj.pk
        obj.delete()
        self.assertFalse(RiskFactor.objects.filter(pk=pk).exists())

    def test_risk_factor_exists(self):
        obj = RiskFactor.objects.create(code="DROPOUT", name="Riesgo de Deserción")
        self.assertTrue(RiskFactor.objects.filter(pk=obj.pk).exists())
        self.assertFalse(RiskFactor.objects.filter(pk=99999).exists())

    # --- StudentRiskFactor (junction) ---

    def test_student_risk_factor_create(self):
        risk_score = StudentRiskScore.objects.create(
            enrollment=self.enrollment, academic_period=self.period,
            risk_score=Decimal("50.00"), risk_label="MEDIO",
        )
        risk_factor = RiskFactor.objects.create(code="LOW_ATT", name="Baja Asistencia")
        srf = StudentRiskFactor.objects.create(
            student_risk_score=risk_score,
            risk_factor=risk_factor,
            contribution_weight=Decimal("30.00"),
        )
        self.assertEqual(srf.contribution_weight, Decimal("30.00"))
        self.assertEqual(srf.risk_factor.name, "Baja Asistencia")
