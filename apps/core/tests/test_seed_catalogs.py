from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.academic.models import PeriodType, Subject
from apps.analytics.student_risk import RiskFactor
from apps.attendance.models import AbsenceType, AttendanceStatus
from apps.behavior.models import (
    IncidentType, Severity,
)
from apps.grading.qualitative_scale import QualitativeScale
from apps.grading.activity_type import ActivityType
from apps.institutions.models import AcademicLevel, AcademicSublevel
from apps.people.models import DocumentType
from apps.students.models import (
    Kinship,
    SpecialNeedsType, WithdrawalReason,
)


CATALOG_COUNTS = {
    DocumentType: 6,
    AttendanceStatus: 4,
    QualitativeScale: 4,
    PeriodType: 6,
    ActivityType: 6,
    AbsenceType: 4,
    IncidentType: 4,
    Subject: 7,
    AcademicLevel: 2,
    AcademicSublevel: 5,
    RiskFactor: 5,
    WithdrawalReason: 6,
    SpecialNeedsType: 7,
    Kinship: 7,
    Severity: 4,
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
