from io import BytesIO
from unittest import TestCase

from fastapi.testclient import TestClient
from PIL import Image

from microscope.api import app

class CaptureTests(TestCase):
    def test_capture_validate(self):
        with TestClient(app) as client:
            settings = {   
                "seed": 42,
                "z_um": 0.0,
                "exposure_ms": 25
            }

            first = client.post("/capture", json=settings)
            second = client.post("/capture", json=settings)
            invalid = client.post("/capture", json={**settings, "exposure_ms": 81})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.headers["content-type"], "image/png")
        self.assertEqual(first.content, second.content)
        self.assertNotEqual(first.headers["X-Capture-ID"], second.headers["X-Capture-ID"])
        self.assertEqual(invalid.status_code, 422)