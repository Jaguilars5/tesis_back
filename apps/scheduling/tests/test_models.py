from datetime import date, time

from django.test import TestCase

from apps.academic.models import Section, Timing_Regime
from apps.institutions.models import Institution, School_Year
from apps.scheduling.models import (
    ScheduleTemplateConfig,
    ScheduleSlot,
    TimeSlot,
    TeacherAvailability,
    SubjectConstraint,
)
from apps.accounts.models import Role, User


class ScheduleTemplateConfigModelTest(TestCase):
    def setUp(self):
        institution = Institution.objects.create(
            name="Institucion",
            code="INST-1",
            address="Calle 1",
            city="Quito",
        )
        school_year = School_Year.objects.create(
            institution=institution,
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            institution=institution,
            name="Matutina",
        )

    def test_create_schedule_template_config(self):
        """Probar creación de configuración de plantilla"""
        config = ScheduleTemplateConfig.objects.create(
            timing_regime=self.timing_regime,
            day_start_time=time(7, 0),
            class_duration_minutes=45,
            break_duration_minutes=15,
            slots_before_break=2,
            total_slots_per_day=6,
        )
        self.assertEqual(config.timing_regime, self.timing_regime)
        self.assertEqual(config.class_duration_minutes, 45)
        self.assertEqual(config.total_slots_per_day, 6)

    def test_schedule_template_config_str(self):
        """Probar representación en string"""
        config = ScheduleTemplateConfig.objects.create(
            timing_regime=self.timing_regime,
            day_start_time=time(7, 0),
            class_duration_minutes=45,
            break_duration_minutes=15,
            slots_before_break=2,
            total_slots_per_day=6,
        )
        self.assertIn("Matutina", str(config))


class TimeSlotModelTest(TestCase):
    def setUp(self):
        institution = Institution.objects.create(
            name="Institucion",
            code="INST-1",
            address="Calle 1",
            city="Quito",
        )
        school_year = School_Year.objects.create(
            institution=institution,
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            institution=institution,
            name="Matutina",
        )

    def test_create_time_slot(self):
        """Probar creación de franja horaria"""
        slot = TimeSlot.objects.create(
            timing_regime=self.timing_regime,
            name="1ra Hora",
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        self.assertEqual(slot.timing_regime, self.timing_regime)
        self.assertEqual(slot.name, "1ra Hora")
        self.assertEqual(slot.day_of_week, 1)

    def test_time_slot_ordering(self):
        """Probar creación de múltiples franjas horarias"""
        TimeSlot.objects.create(
            timing_regime=self.timing_regime,
            name="1ra Hora",
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        TimeSlot.objects.create(
            timing_regime=self.timing_regime,
            name="2da Hora",
            day_of_week=1,
            start_time=time(7, 45),
            end_time=time(8, 30),
        )
        slots = TimeSlot.objects.filter(timing_regime=self.timing_regime)
        self.assertEqual(slots.count(), 2)


class TimeSlotBreakTest(TestCase):
    def setUp(self):
        institution = Institution.objects.create(
            name="Institucion",
            code="INST-1",
            address="Calle 1",
            city="Quito",
        )
        school_year = School_Year.objects.create(
            institution=institution,
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            institution=institution,
            name="Matutina",
        )

    def test_create_break_slot(self):
        """Probar creación de franja de recreo"""
        break_slot = TimeSlot.objects.create(
            timing_regime=self.timing_regime,
            name="Recreo",
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(9, 15),
            is_break=True,
        )
        self.assertTrue(break_slot.is_break)
