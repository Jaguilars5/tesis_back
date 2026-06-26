from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.class_schedule.infrastructure.models import ClassSchedule
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from apps.analytics.student_risk import StudentFeatureSnapshot, StudentRiskScore
from apps.attendance.attendance_core import Attendance
from apps.behavior.behavior_evaluation import BehaviorEvaluation
from apps.behavior.conduct_incident import ConductIncident
from apps.grading.evaluation import EvaluationBlock, BlockComponent, EvaluativeActivity
from apps.grading.student_note import StudentNote, PeriodGradeSummary
from apps.iam import Role, User, UserRole
REPLACED
from apps.people.models import Person
from apps.students.models import (
    Enrollment,
    Kinship,
    Student,
    StudentRepresentative,
)


class SeedTestDataTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        out = StringIO()
        call_command("seed_catalogs", stdout=out)
        call_command("seed_permissions", stdout=out)
        call_command("seed_test_data", stdout=out)

    def test_school_year_created(self):
        self.assertEqual(SchoolYear.objects.count(), 1)
        self.assertTrue(SchoolYear.objects.filter(is_active=True).exists())

    def test_academic_levels_created(self):
        self.assertEqual(AcademicLevel.objects.count(), 2)
        self.assertTrue(AcademicLevel.objects.filter(code="EGB").exists())
        self.assertTrue(AcademicLevel.objects.filter(code="BGU").exists())

    def test_academic_sublevels_use_catalog_codes(self):
        codes = set(
            AcademicSublevel.objects.values_list("code", flat=True)
        )
        expected = {
            "PREPARATORIA",
            "BASICA_ELEMENTAL",
            "BASICA_MEDIA",
            "BASICA_SUPERIOR",
            "BACHILLERATO",
        }
        self.assertTrue(
            expected.issubset(codes),
            f"Subniveles faltantes: {expected - codes}",
        )
        self.assertNotIn("MEDIA", codes)
        self.assertNotIn("SUPERIOR", codes)

    def test_academic_grades_created(self):
        self.assertEqual(AcademicGrade.objects.count(), 3)
        for name in ("7mo EGB", "8vo EGB", "1ro BGU"):
            self.assertTrue(
                AcademicGrade.objects.filter(name=name).exists(),
                f"Falta grado {name}",
            )

    def test_sections_have_school_year(self):
        for section in Section.objects.all():
            self.assertIsNotNone(
                section.school_year,
                f"Sección {section} sin school_year",
            )

    def test_sections_count(self):
        self.assertEqual(Section.objects.count(), 4)

    def test_subjects_use_catalog_codes(self):
        codes = set(Subject.objects.values_list("code", flat=True))
        catalog_codes = {"MAT", "LEN", "CIE", "SOC", "ING"}
        self.assertTrue(
            catalog_codes.issubset(codes),
            f"Faltan códigos: {catalog_codes - codes}",
        )

    def test_subject_configs_cover_all_sections(self):
        for section in Section.objects.all():
            offerings = SubjectOffering.objects.filter(section=section)
            self.assertGreater(
                offerings.count(),
                0,
                f"Sección {section} sin ofertas de materia",
            )

    def test_subject_configs_count(self):
        self.assertEqual(SubjectAcademicConfig.objects.count(), 14)

    def test_subject_offerings_count(self):
        self.assertEqual(SubjectOffering.objects.count(), 19)

    def test_academic_periods_created(self):
        self.assertEqual(AcademicPeriod.objects.count(), 2)
        for period in AcademicPeriod.objects.all():
            self.assertIsNotNone(
                period.period_type,
                f"Período {period} sin period_type",
            )

    def test_users_created_with_roles(self):
        self.assertEqual(User.objects.count(), 8)
        for user in User.objects.filter(is_superuser=False):
            self.assertTrue(
                UserRole.objects.filter(user=user).exists(),
                f"Usuario {user} sin rol asignado",
            )

    def test_superuser_exists(self):
        self.assertTrue(User.objects.filter(is_superuser=True).exists())

    def test_students_created(self):
        self.assertEqual(Student.objects.count(), 2)

    def test_enrollments_created(self):
        self.assertEqual(Enrollment.objects.count(), 2)
        for enrollment in Enrollment.objects.all():
            self.assertEqual(enrollment.enrollment_status, "ACT")

    def test_representative_relationships_created(self):
        self.assertEqual(StudentRepresentative.objects.count(), 2)
        for rel in StudentRepresentative.objects.all():
            self.assertEqual(rel.kinship.code, "PADRE")
            self.assertTrue(rel.is_primary)

    def test_teacher_assignments_match_offerings(self):
        for tss in TeacherSubjectSection.objects.all():
            self.assertIsNotNone(
                tss.subject_offering,
                f"TSS {tss} sin offering",
            )

    def test_attendance_records_created(self):
        self.assertGreater(Attendance.objects.count(), 0)

    def test_conduct_incidents_created(self):
        self.assertGreater(ConductIncident.objects.count(), 0)

    def test_grading_structure_created(self):
        self.assertGreater(EvaluationBlock.objects.count(), 0)
        self.assertGreater(BlockComponent.objects.count(), 0)
        self.assertGreater(EvaluativeActivity.objects.count(), 0)

    def test_evaluative_activities_have_valid_tss(self):
        activities = EvaluativeActivity.objects.all()
        self.assertGreater(activities.count(), 0)
        for activity in activities:
            block_offering_id = (
                activity.block_component.evaluation_block.subject_offering_id
            )
            tss_offering_id = activity.teacher_subject_section.subject_offering_id
            self.assertEqual(
                block_offering_id,
                tss_offering_id,
                f"Actividad {activity.id}: TSS offering != block offering",
            )
            activity.full_clean()

    def test_student_notes_created(self):
        self.assertGreater(StudentNote.objects.count(), 0)

    def test_class_schedules_created(self):
        self.assertGreater(ClassSchedule.objects.count(), 0)
        for schedule in ClassSchedule.objects.all():
            self.assertLess(
                schedule.start_time,
                schedule.end_time,
                f"Horario {schedule.id}: start >= end",
            )
            self.assertIn(schedule.day_of_week, range(1, 6))

    def test_behavior_evaluations_created(self):
        self.assertGreater(BehaviorEvaluation.objects.count(), 0)
        for evaluation in BehaviorEvaluation.objects.all():
            self.assertIsNotNone(evaluation.calculated_scale)
            self.assertIsNotNone(evaluation.evaluated_by)

    def test_early_alerts_created(self):
        self.assertGreater(EarlyAlert.objects.count(), 0)
        for alert in EarlyAlert.objects.all():
            self.assertIn(alert.urgency_level, ["low", "medium", "high", "critical"])
            self.assertIsNotNone(alert.description)

    def test_student_feature_snapshots_created(self):
        self.assertGreater(StudentFeatureSnapshot.objects.count(), 0)
        for snapshot in StudentFeatureSnapshot.objects.all():
            self.assertIsNotNone(snapshot.attendance_rate)
            self.assertIsNotNone(snapshot.calculated_at)

    def test_student_risk_scores_created(self):
        self.assertGreater(StudentRiskScore.objects.count(), 0)
        for score in StudentRiskScore.objects.all():
            self.assertIn(score.risk_label, ["verde", "amarillo", "rojo"])
            self.assertIsNotNone(score.model_version)

    def test_period_grade_summaries_created(self):
        self.assertGreater(PeriodGradeSummary.objects.count(), 0)

    def test_idempotent_double_execution(self):
        users_before = User.objects.count()
        enrollments_before = Enrollment.objects.count()
        activities_before = EvaluativeActivity.objects.count()
        schedules_before = ClassSchedule.objects.count()
        behaviors_before = BehaviorEvaluation.objects.count()
        alerts_before = EarlyAlert.objects.count()
        snapshots_before = StudentFeatureSnapshot.objects.count()
        scores_before = StudentRiskScore.objects.count()

        out = StringIO()
        call_command("seed_test_data", stdout=out)

        self.assertEqual(User.objects.count(), users_before)
        self.assertEqual(Enrollment.objects.count(), enrollments_before)
        self.assertEqual(EvaluativeActivity.objects.count(), activities_before)
        self.assertEqual(ClassSchedule.objects.count(), schedules_before)
        self.assertEqual(BehaviorEvaluation.objects.count(), behaviors_before)
        self.assertEqual(EarlyAlert.objects.count(), alerts_before)
        self.assertEqual(StudentFeatureSnapshot.objects.count(), snapshots_before)
        self.assertEqual(StudentRiskScore.objects.count(), scores_before)
