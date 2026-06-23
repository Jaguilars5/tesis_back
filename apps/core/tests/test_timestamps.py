import datetime

from django.test import TestCase

from apps.institutions.models import SchoolYear


class TimeStampedModelTest(TestCase):
    def test_updated_at_changes_on_modify(self):
        obj = SchoolYear.objects.create(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            is_active=True,
        )
        original_created = obj.created_at
        original_updated = obj.updated_at

        obj.name = "Updated Year"
        obj.save()

        obj.refresh_from_db()
        self.assertEqual(obj.created_at, original_created)
        self.assertNotEqual(obj.updated_at, original_updated)

    def test_created_at_set_on_create(self):
        obj = SchoolYear.objects.create(
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 12, 31),
            is_active=True,
        )
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)
