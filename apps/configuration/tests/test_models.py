from django.test import TestCase
from ..models import SystemConfig


class SystemConfigModelTest(TestCase):
    def setUp(self):
        self.config = SystemConfig.objects.create(
            key="SITE_NAME", value="Mi Colegio", description="Nombre del sitio"
        )

    def test_creation(self):
        self.assertEqual(self.config.key, "SITE_NAME")
        self.assertEqual(self.config.value, "Mi Colegio")

    def test_str(self):
        self.assertEqual(str(self.config), "SITE_NAME")

    def test_unique_key(self):
        with self.assertRaises(Exception):
            SystemConfig.objects.create(key="SITE_NAME", value="Duplicado")
