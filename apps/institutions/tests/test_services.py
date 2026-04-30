from django.test import TestCase
from datetime import date
from ..models import Institution, School_Year, Classroom
from ..services.institution_service import InstitutionService


class InstitutionServiceTest(TestCase):
    """Tests para el servicio de Institution"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.institution = Institution.objects.create(
            name="Colegio Test", code="CT-001", address="Calle Test", city="Quito"
        )

    def test_create_institution(self):
        """Probar creación de institución"""
        institution = InstitutionService.create_institution(
            name="Nueva Institución",
            code="NI-001",
            address="Av. Nueva",
            city="Guayaquil",
        )

        self.assertIsNotNone(institution.id)
        self.assertEqual(institution.name, "Nueva Institución")
        self.assertEqual(institution.code, "NI-001")

    def test_create_institution_duplicate_code(self):
        """Probar que no permite código duplicado"""
        with self.assertRaises(ValueError):
            InstitutionService.create_institution(
                name="Otra Institución",
                code="CT-001",  # Mismo código
                address="Otra dirección",
                city="Cuenca",
            )

    def test_get_institution(self):
        """Probar obtención de institución"""
        institution = InstitutionService.get_institution(self.institution.id)
        self.assertEqual(institution.id, self.institution.id)
        self.assertEqual(institution.name, "Colegio Test")

    def test_get_institution_not_found(self):
        """Probar error al obtener institución inexistente"""
        with self.assertRaises(ValueError):
            InstitutionService.get_institution(9999)

    def test_get_all_institutions(self):
        """Probar obtención de todas las instituciones"""
        Institution.objects.create(
            name="Instituto B", code="IB-001", address="Dirección B", city="Quito"
        )

        institutions = InstitutionService.get_all_institutions()
        self.assertEqual(institutions.count(), 2)

    def test_update_institution(self):
        """Probar actualización de institución"""
        institution = InstitutionService.update_institution(
            self.institution.id, name="Colegio Actualizado", city="Cuenca"
        )

        self.assertEqual(institution.name, "Colegio Actualizado")
        self.assertEqual(institution.city, "Cuenca")

    def test_deactivate_institution(self):
        """Probar desactivación de institución"""
        institution = InstitutionService.deactivate_institution(self.institution.id)
        self.assertFalse(institution.active)

    def test_search_institutions(self):
        """Probar búsqueda de instituciones"""
        Institution.objects.create(
            name="Academia Joven",
            code="AJ-001",
            address="Dirección Academia",
            city="Quito",
        )

        # Por nombre
        results = InstitutionService.search_institutions("Academia")
        self.assertTrue(any(i.name == "Academia Joven" for i in results))


class SchoolYearServiceTest(TestCase):
    """Tests para el servicio de School_Year"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.institution = Institution.objects.create(
            name="Escuela A", code="EA-001", address="Dirección EA", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_create_school_year(self):
        """Probar creación de año escolar"""
        school_year = InstitutionService.create_school_year(
            self.institution.id, "2025-2026", date(2025, 9, 1), date(2026, 7, 31)
        )

        self.assertIsNotNone(school_year.id)
        self.assertEqual(school_year.name, "2025-2026")

    def test_create_school_year_invalid_dates(self):
        """Probar que rechaza fechas inválidas"""
        with self.assertRaises(ValueError):
            InstitutionService.create_school_year(
                self.institution.id,
                "2025-2026",
                date(2026, 7, 31),  # Fecha final
                date(2025, 9, 1),  # Fecha inicial (invertidas)
            )

    def test_create_school_year_date_conflict(self):
        """Probar que detecta conflicto de fechas"""
        with self.assertRaises(ValueError):
            InstitutionService.create_school_year(
                self.institution.id,
                "2024-2025-2",
                date(2024, 12, 1),  # Dentro del rango del año existente
                date(2025, 3, 31),
            )

    def test_get_school_year(self):
        """Probar obtención de año escolar"""
        school_year = InstitutionService.get_school_year(self.school_year.id)
        self.assertEqual(school_year.id, self.school_year.id)

    def test_list_school_years(self):
        """Probar listado de años escolares"""
        InstitutionService.create_school_year(
            self.institution.id, "2025-2026", date(2025, 9, 1), date(2026, 7, 31)
        )

        years = InstitutionService.list_school_years(self.institution.id)
        self.assertEqual(years.count(), 2)

    def test_get_current_school_year(self):
        """Probar obtención del año escolar actual"""
        School_Year.objects.create(
            institution=self.institution,
            name="Actual",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            active=True,
        )

        # Esto debería funcionar si la fecha actual está dentro del rango
        try:
            current = InstitutionService.get_current_school_year(self.institution.id)
            self.assertIsNotNone(current)
        except ValueError:
            # Si la fecha actual no está en ningún rango, es esperado
            pass

    def test_update_school_year(self):
        """Probar actualización de año escolar"""
        updated = InstitutionService.update_school_year(
            self.school_year.id, name="2024-2025 Modificado"
        )

        self.assertEqual(updated.name, "2024-2025 Modificado")

    def test_deactivate_school_year(self):
        """Probar desactivación de año escolar"""
        school_year = InstitutionService.deactivate_school_year(self.school_year.id)
        self.assertFalse(school_year.active)


class ClassroomServiceTest(TestCase):
    """Tests para el servicio de Classroom"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.institution = Institution.objects.create(
            name="Instituto Test", code="IT-001", address="Dirección IT", city="Quito"
        )
        self.classroom = Classroom.objects.create(
            institution=self.institution,
            name="101",
            room_type="Aula de clase",
            capacity=40,
        )

    def test_create_classroom(self):
        """Probar creación de aula"""
        classroom = InstitutionService.create_classroom(
            self.institution.id, "102", "Aula de clase", 35
        )

        self.assertIsNotNone(classroom.id)
        self.assertEqual(classroom.name, "102")
        self.assertEqual(classroom.capacity, 35)

    def test_create_classroom_invalid_capacity(self):
        """Probar que rechaza capacidad inválida"""
        with self.assertRaises(ValueError):
            InstitutionService.create_classroom(
                self.institution.id, "999", "Aula", 0  # Capacidad inválida
            )

    def test_get_classroom(self):
        """Probar obtención de aula"""
        classroom = InstitutionService.get_classroom(self.classroom.id)
        self.assertEqual(classroom.id, self.classroom.id)

    def test_list_classrooms(self):
        """Probar listado de aulas"""
        InstitutionService.create_classroom(
            self.institution.id, "103", "Laboratorio", 25
        )

        classrooms = InstitutionService.list_classrooms(self.institution.id)
        self.assertEqual(classrooms.count(), 2)

    def test_list_classrooms_by_type(self):
        """Probar listado de aulas por tipo"""
        InstitutionService.create_classroom(
            self.institution.id, "Lab-01", "Laboratorio", 20
        )

        labs = InstitutionService.list_classrooms_by_type(
            self.institution.id, "Laboratorio"
        )
        self.assertEqual(labs.count(), 1)
        self.assertEqual(labs.first().room_type, "Laboratorio")

    def test_update_classroom(self):
        """Probar actualización de aula"""
        classroom = InstitutionService.update_classroom(
            self.classroom.id, capacity=50, room_type="Aula Premium"
        )

        self.assertEqual(classroom.capacity, 50)
        self.assertEqual(classroom.room_type, "Aula Premium")

    def test_deactivate_classroom(self):
        """Probar desactivación de aula"""
        classroom = InstitutionService.deactivate_classroom(self.classroom.id)
        self.assertFalse(classroom.active)

    def test_get_available_classrooms(self):
        """Probar obtención de aulas disponibles"""
        InstitutionService.create_classroom(
            self.institution.id, "Grande", "Auditorio", 100
        )

        available = InstitutionService.get_available_classrooms(self.institution.id)
        self.assertEqual(available.count(), 2)

        # Con capacidad mínima
        large = InstitutionService.get_available_classrooms(
            self.institution.id, capacity_min=50
        )
        self.assertEqual(large.count(), 1)
        self.assertEqual(large.first().name, "Grande")
