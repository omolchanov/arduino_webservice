import json
import unittest

from fastapi.testclient import TestClient

import main


class StatusApiTests(unittest.TestCase):
    def setUp(self):
        main.last_potentiometer_v = 2.5
        main.last_detected_value = 1
        main.last_current_ma = 12.3
        main.last_led_resistance_ohm = 162.6
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_potentiometer_v = None
        main.last_detected_value = None
        main.last_current_ma = None
        main.last_led_resistance_ohm = None

    def test_status_includes_potentiometer_and_detected(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_potentiometer_v"], 2.5)
        self.assertEqual(data["last_detected_value"], 1)
        self.assertEqual(data["last_current_ma"], 12.3)
        self.assertEqual(data["last_led_resistance_ohm"], 162.6)


class WebSocketCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_potentiometer_v = 1.85
        main.last_detected_value = 0
        main.last_current_ma = 5.7
        main.last_led_resistance_ohm = 85.3
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_potentiometer_v = None
        main.last_detected_value = None
        main.last_current_ma = None
        main.last_led_resistance_ohm = None

    def test_connect_sends_cached_potentiometer_and_detected(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 10:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                types = {m["type"] for m in messages}
                if (
                    "potentiometer" in types
                    and "detected" in types
                    and "current" in types
                    and "resistance" in types
                ):
                    break
        pot = next(m for m in messages if m["type"] == "potentiometer")
        detected = next(m for m in messages if m["type"] == "detected")
        current = next(m for m in messages if m["type"] == "current")
        resistance = next(m for m in messages if m["type"] == "resistance")
        self.assertTrue(pot["cached"])
        self.assertEqual(pot["v"], 1.85)
        self.assertTrue(detected["cached"])
        self.assertEqual(detected["value"], 0)
        self.assertTrue(current["cached"])
        self.assertEqual(current["ma"], 5.7)
        self.assertTrue(resistance["cached"])
        self.assertEqual(resistance["ohm"], 85.3)
