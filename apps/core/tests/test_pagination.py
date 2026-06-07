from django.test import TestCase, RequestFactory
from rest_framework.request import Request
from apps.core.api.pagination import StandardResultsSetPagination
from apps.accounts.models import Role, User
from apps.core.tests.helpers import create_test_user


class StandardResultsSetPaginationTest(TestCase):
    """Tests para StandardResultsSetPagination"""

    def setUp(self):
        self.pagination = StandardResultsSetPagination()
        self.factory = RequestFactory()
        for i in range(25):
            create_test_user(
                email=f"user{i}@test.com",
                dni=f"{1000000000 + i}",
                names=f"User{i}",
                last_names="Test",
                password="testpass123",
            )

    def test_default_page_size(self):
        self.assertEqual(self.pagination.page_size, 20)

    def test_page_size_query_param(self):
        self.assertEqual(self.pagination.page_size_query_param, "page_size")

    def test_max_page_size(self):
        self.assertEqual(self.pagination.max_page_size, 100)

    def test_paginated_response_format(self):
        request = self.factory.get("/api/accounts/user/")
        drf_request = Request(request)
        queryset = User.objects.all()

        page = self.pagination.paginate_queryset(queryset, drf_request)
        response = self.pagination.get_paginated_response(page)

        self.assertTrue(response.data["ok"])
        self.assertIn("count", response.data["data"])
        self.assertIn("next", response.data["data"])
        self.assertIn("previous", response.data["data"])
        self.assertIn("results", response.data["data"])
        self.assertEqual(response.data["data"]["count"], 25)
        self.assertEqual(len(response.data["data"]["results"]), 20)

    def test_custom_page_size(self):
        request = self.factory.get("/api/accounts/user/?page_size=5")
        drf_request = Request(request)
        queryset = User.objects.all()

        page = self.pagination.paginate_queryset(queryset, drf_request)
        response = self.pagination.get_paginated_response(page)

        self.assertEqual(len(response.data["data"]["results"]), 5)

    def test_pagination_exceeds_max_page_size(self):
        request = self.factory.get("/api/accounts/user/?page_size=200")
        drf_request = Request(request)
        queryset = User.objects.all()

        page = self.pagination.paginate_queryset(queryset, drf_request)
        response = self.pagination.get_paginated_response(page)

        self.assertLessEqual(len(response.data["data"]["results"]), 100)
