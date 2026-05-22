from datetime import date, time

from django.test import TestCase
from datetime import date, time

from apps.scheduling.models import ScheduleTemplateConfig, TimeSlot


class SchedulingServiceTest(TestCase):
    def test_schedule_template_config_creation(self):
        config = ScheduleTemplateConfig.objects.create(
            day_start_time=time(7, 0),
            class_duration_minutes=45,
            break_duration_minutes=15,
            slots_before_break=2,
            total_slots_per_day=6,
        )
        self.assertIsNotNone(config.id)

    def test_time_slot_generation(self):
        time_slots = TimeSlot.objects.all()
        self.assertEqual(time_slots.count(), 0)

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

        time_slots = TimeSlot.objects.all()
        self.assertEqual(time_slots.count(), 2)
