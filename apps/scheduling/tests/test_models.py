from datetime import date, time

from django.test import TestCase

from apps.institutions.models import School_Year
from apps.scheduling.models import (
    ScheduleTemplateConfig,
    ScheduleSlot,
    TimeSlot,
    TeacherAvailability,
    SubjectConstraint,
)


class ScheduleTemplateConfigModelTest(TestCase):
    def test_create_schedule_template_config(self):
        config = ScheduleTemplateConfig.objects.create(
            day_start_time=time(7, 0),
            class_duration_minutes=45,
            break_duration_minutes=15,
            slots_before_break=2,
            total_slots_per_day=6,
        )
        self.assertEqual(config.class_duration_minutes, 45)
        self.assertEqual(config.total_slots_per_day, 6)

    def test_schedule_template_config_str(self):
        config = ScheduleTemplateConfig.objects.create(
            day_start_time=time(7, 0),
            class_duration_minutes=45,
            break_duration_minutes=15,
            slots_before_break=2,
            total_slots_per_day=6,
        )
        self.assertTrue(str(config))


class TimeSlotModelTest(TestCase):
    def test_create_time_slot(self):
        slot = TimeSlot.objects.create(
            name="1ra Hora",
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        self.assertEqual(slot.name, "1ra Hora")
        self.assertEqual(slot.day_of_week, 1)

    def test_time_slot_ordering(self):
        TimeSlot.objects.create(
            name="1ra Hora",
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        TimeSlot.objects.create(
            name="2da Hora",
            day_of_week=1,
            start_time=time(7, 45),
            end_time=time(8, 30),
        )
        slots = TimeSlot.objects.all()
        self.assertEqual(slots.count(), 2)


class TimeSlotBreakTest(TestCase):
    def test_create_break_slot(self):
        break_slot = TimeSlot.objects.create(
            name="Recreo",
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(9, 15),
            is_break=True,
        )
        self.assertTrue(break_slot.is_break)
