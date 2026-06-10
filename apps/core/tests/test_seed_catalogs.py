from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.academic.models import DayOfWeek, PeriodType, Subject
from apps.analytics.models import AlertType, RiskFactor, UrgencyLevel
from apps.attendance.models import AbsenceType, AttendanceStatus
from apps.behavior.models import (
    DevelopmentLevel, IncidentType, Severity,
    SocioemotionalArea, SocioemotionalSkill,
)
from apps.grading.models import (
    ActivityType,
    EvaluationType,
    GradeType,
    PromotionStatus,
    QualitativeScale,
    RecoveryProcessType,
    RecoveryProcessStatus,
)
from apps.institutions.models import AcademicSublevel
from apps.integration.models import SyncOperation, SyncStatus
from apps.people.models import DocumentType
from apps.students.models import (
    EnrollmentStatus, Kinship, ResidentialZone,
    SpecialNeedsType, WithdrawalReason,
)


CATALOG_COUNTS = {
    DocumentType: 6,
    AttendanceStatus: 4,
    GradeType: 3,
    QualitativeScale: 4,
    PeriodType: 3,
    ActivityType: 6,
    EvaluationType: 3,
    PromotionStatus: 3,
    RecoveryProcessType: 3,
    RecoveryProcessStatus: 5,
    AbsenceType: 4,
    IncidentType: 4,
    SocioemotionalSkill: 5,
    Subject: 7,
    AcademicSublevel: 5,
    AlertType: 5,
    UrgencyLevel: 4,
    RiskFactor: 5,
    SyncOperation: 3,
    SyncStatus: 6,
    EnrollmentStatus: 5,
    WithdrawalReason: 6,
    ResidentialZone: 3,
    SpecialNeedsType: 7,
    Kinship: 7,
    Severity: 4,
    SocioemotionalArea: 5,
    DevelopmentLevel: 3,
    DayOfWeek: 7,
    RecoveryProcessStatus: 5,
}


class SeedCatalogsTest(TestCase):
    def test_seed_all_catalogs(self):
        out = StringIO()
        call_command("seed_catalogs", stdout=out)
        for model, expected in CATALOG_COUNTS.items():
            self.assertEqual(
                model.objects.count(),
                expected,
                f"{model.__name__} expected {expected} records, got {model.objects.count()}",
            )
        for model, expected in CATALOG_COUNTS.items():
            self.assertGreaterEqual(
                model.objects.count(),
                expected,
                f"{model.__name__} expected at least {expected} records, got {model.objects.count()}",
            )
        self.assertTrue("created" in out.getvalue())

    def test_idempotent_double_execution(self):
        call_command("seed_catalogs", stdout=StringIO())
        out = StringIO()
        call_command("seed_catalogs", stdout=out)
        for model, expected in CATALOG_COUNTS.items():
            self.assertEqual(
                model.objects.count(),
                expected,
                f"{model.__name__} expected {expected} records after second run, got {model.objects.count()}",
            )
        self.assertIn("0 created", out.getvalue())
