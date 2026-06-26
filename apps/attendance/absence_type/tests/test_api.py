from rest_framework.test import APITestCase
from rest_framework import status

from apps.attendance.absence_type.infrastructure.models import AbsenceType
from apps.core.tests.helpers import create_test_user


class AbsenceTypeAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="absence_type@test.com",
            dni="9999999999",
            names="AT",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/attendance/absence-types/"

    def _create(self, code="justified", name="Justificada", description=""):
        return AbsenceType.objects.create(
            code=code, name=name, description=description
        )

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_with_data(self):
        self._create()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create(self):
        data = {
            "code": "unjustified",
            "name": "Injustificada",
            "description": "Sin justificación",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["code"], "unjustified")

    def test_get(self):
        obj = self._create()
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Justificada")

    def test_update(self):
        obj = self._create()
        data = {"code": obj.code, "name": "Justificada (editada)"}
        response = self.client.put(f"{self.url}{obj.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Justificada (editada)")

    def test_destroy(self):
        obj = self._create()
        response = self.client.delete(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(AbsenceType.objects.filter(pk=obj.id).exists())

    def test_soft_delete_without_confirm(self):
        obj = self._create()
        response = self.client.post(
            f"{self.url}{obj.id}/soft-delete/", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        # Catálogo sin hijos en cascada: desactiva inmediatamente
        self.assertFalse(response.data["data"]["is_active"])
        obj.refresh_from_db()
        self.assertFalse(obj.is_active)

    def test_soft_delete_with_confirm(self):
        obj = self._create()
        response = self.client.post(
            f"{self.url}{obj.id}/soft-delete/",
            {"confirm": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_filter_by_is_active(self):
        self._create(code="a", name="Activa")
        inactive = self._create(code="b", name="Inactiva")
        inactive.is_active = False
        inactive.save(update_fields=["is_active"])
        response = self.client.get(f"{self.url}?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["code"], "a")

    def test_search_by_name(self):
        self._create(code="a", name="Justificada")
        self._create(code="b", name="Injustificada")
        response = self.client.get(f"{self.url}?search=Injustificada")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["code"], "b")

    def test_create_validation_error_missing_fields(self):
        response = self.client.post(self.url, {"description": "x"}, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_create_validation_error_duplicate_code(self):
        self._create(code="justified", name="Justificada")
        data = {"code": "justified", "name": "Otra"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_permission_denied(self):
        user_no_perm = create_test_user(
            email="noperm_absence@test.com",
            dni="8888888888",
            names="No",
            last_names="Perm",
            is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
