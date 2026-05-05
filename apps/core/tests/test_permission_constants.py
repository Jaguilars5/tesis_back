from django.test import TestCase

from apps.core.constants.permissions import (
    academic,
    accounts,
    analytics,
    grading,
    institutions,
    scheduling,
    students,
)


def _all_modules():
    return [
        accounts,
        institutions,
        academic,
        students,
        grading,
        scheduling,
        analytics,
    ]


class PermissionConstantsTestCase(TestCase):
    def test_all_permissions_are_strings(self):
        for module in _all_modules():
            for field_name in dir(module):
                if field_name.isupper():
                    value = getattr(module, field_name)
                    self.assertIsInstance(value, str)

    def test_permissions_follow_format(self):
        import re

        pattern = re.compile(r"^[a-z_]+\.[a-z_]+$")
        for module in _all_modules():
            for field_name in dir(module):
                if field_name.isupper():
                    value = getattr(module, field_name)
                    self.assertRegex(value, pattern)

    def test_no_duplicate_permissions(self):
        all_permissions = set()
        duplicates = set()
        for module in _all_modules():
            for field_name in dir(module):
                if field_name.isupper():
                    value = getattr(module, field_name)
                    if value in all_permissions:
                        duplicates.add(value)
                    all_permissions.add(value)
        self.assertEqual(len(duplicates), 0, f"Duplicates found: {duplicates}")

    def test_grading_permissions_match_seed_catalog(self):
        from apps.accounts.management.commands.seed_permissions import (
            PERMISSIONS_CATALOG,
        )

        grading_perms_in_catalog = {
            p[0] for p in PERMISSIONS_CATALOG.get("grading", [])
        }
        grading_perms_constants = set()
        for field_name in dir(grading):
            if field_name.isupper():
                grading_perms_constants.add(getattr(grading, field_name))
        self.assertEqual(grading_perms_in_catalog, grading_perms_constants)
