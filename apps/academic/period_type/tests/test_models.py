from django.test import TestCase
from ..infrastructure.models import PeriodType


class PeriodTypeModelTest(TestCase):
    def test_period_type_creation(self):
        pt = PeriodType.objects.create(code="QUIMESTRE", name="Quimestre", divisions_per_year=2)
        self.assertEqual(pt.code, "QUIMESTRE")
        self.assertEqual(pt.divisions_per_year, 2)
        self.assertTrue(pt.is_active)

    def test_period_type_unique_code(self):
        PeriodType.objects.create(code="UNICO", name="Único")
        with self.assertRaises(Exception):
            PeriodType.objects.create(code="UNICO", name="Otro")
