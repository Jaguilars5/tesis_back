from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import Permission
from apps.accounts.management.commands.seed_permissions import PERMISSIONS_CATALOG


class SeedPermissionsTest(TestCase):
    def setUp(self):
        self.total_permissions = sum(len(v) for v in PERMISSIONS_CATALOG.values())

    def test_seed_all_permissions(self):
        out = StringIO()
        call_command("seed_permissions", stdout=out)
        self.assertEqual(Permission.objects.count(), self.total_permissions)
        self.assertIn(f"{self.total_permissions} created", out.getvalue())

    def test_idempotent_double_execution(self):
        call_command("seed_permissions", stdout=StringIO())
        out = StringIO()
        call_command("seed_permissions", stdout=out)
        self.assertEqual(Permission.objects.count(), self.total_permissions)
        self.assertIn("0 created", out.getvalue())

    def test_seed_specific_module(self):
        out = StringIO()
        call_command("seed_permissions", "--module", "grading", stdout=out)
        grading_count = len(PERMISSIONS_CATALOG["grading"])
        self.assertEqual(Permission.objects.count(), grading_count)
        self.assertTrue(
            Permission.objects.filter(code__startswith="grading.").exists()
        )
        self.assertFalse(
            Permission.objects.filter(code__startswith="accounts.").exists()
        )

    def test_seed_inexistent_module(self):
        out = StringIO()
        err = StringIO()
        call_command("seed_permissions", "--module", "inexistente", stdout=out, stderr=err)
        self.assertEqual(Permission.objects.count(), 0)
        self.assertIn("not found", err.getvalue())
