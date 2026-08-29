import json
import unittest

from fastapi.testclient import TestClient

import main


class StatusApiTests(unittest.TestCase):
    def setUp(self):
        main.last_potentiometer_v = 2.5
        main.last_detected_value = 1
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_potentiometer_v = None
        main.last_detected_value = None

    def test_status_includes_potentiometer_and_detected(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_potentiometer_v"], 2.5)
        self.assertEqual(data["last_detected_value"], 1)


class WebSocketCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_potentiometer_v = 1.85
        main.last_detected_value = 0
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_potentiometer_v = None
        main.last_detected_value = None

    def test_connect_sends_cached_potentiometer_and_detected(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 10:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                types = {m["type"] for m in messages}
                if "potentiometer" in types and "detected" in types:
                    break
        pot = next(m for m in messages if m["type"] == "potentiometer")
        detected = next(m for m in messages if m["type"] == "detected")
        self.assertTrue(pot["cached"])
        self.assertEqual(pot["v"], 1.85)
        self.assertTrue(detected["cached"])
        self.assertEqual(detected["value"], 0)
