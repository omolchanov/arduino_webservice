import json
import unittest

from fastapi.testclient import TestClient

import main


class ParseCondensatorTests(unittest.TestCase):
    def test_valid_line(self):
        result = main.parse_condensator_line("V = 2.45 V   Q = 539.0 uC")
        self.assertEqual(result, (2.45, 539.0))

    def test_invalid_line(self):
        self.assertIsNone(main.parse_condensator_line("Distance: 42.50 cm"))
        self.assertIsNone(main.parse_condensator_line("Charging..."))

    def test_phase_lines(self):
        self.assertEqual(main.parse_condensator_phase_line("Charging..."), "charging")
        self.assertEqual(
            main.parse_condensator_phase_line("Discharging..."), "discharging"
        )
        self.assertIsNone(main.parse_condensator_phase_line("V = 1.0 V   Q = 220.0 uC"))


class CondensatorApiTests(unittest.TestCase):
    def setUp(self):
        main.last_condensator_v = 3.21
        main.last_condensator_q_uc = 706.2
        main.last_condensator_phase = "charging"
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_condensator_v = None
        main.last_condensator_q_uc = None
        main.last_condensator_phase = None

    def test_condensator_page(self):
        response = self.client.get("/condensator")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Condensator", response.text)

    def test_status_includes_condensator_fields(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_condensator_v"], 3.21)
        self.assertEqual(data["last_condensator_q_uc"], 706.2)
        self.assertEqual(data["last_condensator_phase"], "charging")

    def test_connect_sends_cached_condensator(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 20:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                types = {m["type"] for m in messages}
                if "condensator" in types and "condensator_phase" in types:
                    break
        measurement = next(m for m in messages if m["type"] == "condensator")
        phase = next(m for m in messages if m["type"] == "condensator_phase")
        self.assertTrue(measurement["cached"])
        self.assertEqual(measurement["v"], 3.21)
        self.assertEqual(measurement["q_uc"], 706.2)
        self.assertTrue(phase["cached"])
        self.assertEqual(phase["phase"], "charging")
