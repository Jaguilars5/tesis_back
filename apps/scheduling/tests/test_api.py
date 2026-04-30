from datetime import date, time

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import Section, Timing_Regime
from apps.accounts.models import Role, User
from apps.institutions.models import Institution, School_Year
from apps.scheduling.models import (
    ScheduleTemplateConfig,
    ScheduleSlot,
    TimeSlot,
)


class SchedulingAPITest(APITestCase):
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

        # Create test user
        role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="scheduling@test.com",
            dni="1717171717",
            names="Scheduling",
            last_names="Tester",
            password="test_password_123",
            role=role,
            institution=institution,
        )
        self.client.force_authenticate(user=self.user)

        self.schedule_template_url = "/api/scheduling/schedule-template/"
        self.schedule_slot_url = "/api/scheduling/schedule-slot/"

    def test_schedule_template_creation(self):
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
        self.assertEqual(config.total_slots_per_day, 6)

    def test_time_slot_creation(self):
        """Probar creación de franjas horarias"""
        time_slot = TimeSlot.objects.create(
            timing_regime=self.timing_regime,
            name="1ra Hora",
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        self.assertIsNotNone(time_slot.id)
        self.assertEqual(time_slot.name, "1ra Hora")
