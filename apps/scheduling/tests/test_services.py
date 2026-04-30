from datetime import date, time

from django.test import TestCase

from apps.academic.models import Section, Timing_Regime
from apps.institutions.models import Institution, School_Year
from apps.scheduling.models import ScheduleTemplateConfig, TimeSlot


class SchedulingServiceTest(TestCase):
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
            school_year=school_year,
            name="Matutina",
        )
        self.school_year = school_year

    def test_schedule_template_config_creation(self):
        """Probar creación de configuración de horario"""
        config = ScheduleTemplateConfig.objects.create(
            timing_regime=self.timing_regime,
            day_start_time=time(7, 0),
            class_duration_minutes=45,
            break_duration_minutes=15,
            slots_before_break=2,
            total_slots_per_day=6,
        )
        self.assertIsNotNone(config.id)
        self.assertEqual(config.timing_regime, self.timing_regime)

    def test_time_slot_generation(self):
        """Probar generación de franjas horarias"""
        time_slots = TimeSlot.objects.filter(timing_regime=self.timing_regime)
        self.assertEqual(time_slots.count(), 0)

        # Crear slots manualmente
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

        time_slots = TimeSlot.objects.filter(timing_regime=self.timing_regime)
        self.assertEqual(time_slots.count(), 2)
