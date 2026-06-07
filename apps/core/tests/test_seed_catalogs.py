from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.analytics.models import RiskFactor
from apps.grading.models import GradeType, QualitativeScale
from apps.attendance.models import AttendanceStatus
from apps.institutions.models import DocumentType
from apps.students.models import EnrollmentStatus


class SeedCatalogsTest(TestCase):
    def test_seed_all_catalogs(self):
        out = StringIO()
        call_command("seed_catalogs", stdout=out)
        self.assertEqual(DocumentType.objects.count(), 6)
        self.assertEqual(AttendanceStatus.objects.count(), 4)
        self.assertEqual(GradeType.objects.count(), 3)
        self.assertEqual(QualitativeScale.objects.count(), 4)
        self.assertEqual(EnrollmentStatus.objects.count(), 5)
        self.assertEqual(RiskFactor.objects.count(), 5)
        self.assertIn("27 created", out.getvalue())

    def test_idempotent_double_execution(self):
        call_command("seed_catalogs", stdout=StringIO())
        out = StringIO()
        call_command("seed_catalogs", stdout=out)
        self.assertEqual(DocumentType.objects.count(), 6)
        self.assertIn("0 created", out.getvalue())
