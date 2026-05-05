from django.test import TestCase
from apps.core.renderers import StandardResponseRenderer


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class StandardResponseRendererTest(TestCase):
    """Tests para StandardResponseRenderer"""

    def setUp(self):
        self.renderer = StandardResponseRenderer()
        self.context = {"response": MockResponse(200)}

    def test_success_response_format(self):
        data = {"name": "test"}
        result = self.renderer.render(data, renderer_context=self.context)
        import json
        parsed = json.loads(result)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["data"], {"name": "test"})
        self.assertEqual(parsed["msg"], "")

    def test_error_response_format(self):
        error_context = {"response": MockResponse(400)}
        data = {"detail": "Not found"}
        result = self.renderer.render(data, renderer_context=error_context)
        import json
        parsed = json.loads(result)
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["data"], {"detail": "Not found"})
        self.assertEqual(parsed["msg"], "Error de validaci\u00f3n o proceso.")

    def test_already_formatted_response(self):
        data = {"ok": True, "data": {"id": 1}, "msg": "Success"}
        result = self.renderer.render(data, renderer_context=self.context)
        import json
        parsed = json.loads(result)
        self.assertEqual(parsed, data)

    def test_server_error_format(self):
        error_context = {"response": MockResponse(500)}
        data = {"error": "Internal error"}
        result = self.renderer.render(data, renderer_context=error_context)
        import json
        parsed = json.loads(result)
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["msg"], "Error de validaci\u00f3n o proceso.")
