import json
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import main
from main import parse_valve_line, read_serial, write_serial_gate


class ParseValveLineTests(unittest.TestCase):
    def test_and_gate_line(self):
        self.assertEqual(
            parse_valve_line("A = 0 | B = 1 | Y = 0 | Gate = AND"),
            (0, 1, 0, "AND"),
        )

    def test_or_gate_line(self):
        self.assertEqual(
            parse_valve_line("A = 1 | B = 1 | Y = 1 | Gate = OR"),
            (1, 1, 1, "OR"),
        )

    def test_xor_gate_line(self):
        self.assertEqual(
            parse_valve_line("A = 1 | B = 0 | Y = 1 | Gate = XOR"),
            (1, 0, 1, "XOR"),
        )

    def test_not_gate_line(self):
        self.assertEqual(
            parse_valve_line("A = 1 | B = 0 | Y = 0 | Gate = NOT"),
            (1, 0, 0, "NOT"),
        )

    def test_invalid_lines(self):
        self.assertIsNone(parse_valve_line("Pot: 2.50 V | Logic: 0"))
        self.assertIsNone(parse_valve_line("Выбран AND"))
        self.assertIsNone(parse_valve_line(""))


class ReadSerialValveTests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_valve")
    def test_valve_line_emits_valve(self, mock_notify, mock_stop):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"A = 0 | B = 1 | Y = 0 | Gate = AND\n"

        read_serial(FakePort())

        mock_notify.assert_called_once_with(0, 1, 0, "AND")


class WriteSerialGateTests(unittest.TestCase):
    def tearDown(self):
        main.serial_connected = False
        main.serial_port = None

    def test_write_and_gate(self):
        port = MagicMock()
        port.is_open = True
        main.serial_connected = True
        main.serial_port = port

        self.assertTrue(write_serial_gate("AND"))
        port.write.assert_called_once_with(b"AND\n")

    def test_write_xor_gate(self):
        port = MagicMock()
        port.is_open = True
        main.serial_connected = True
        main.serial_port = port

        self.assertTrue(write_serial_gate("XOR"))
        port.write.assert_called_once_with(b"XOR\n")

    def test_write_or_gate(self):
        port = MagicMock()
        port.is_open = True
        main.serial_connected = True
        main.serial_port = port

        self.assertTrue(write_serial_gate("OR"))
        port.write.assert_called_once_with(b"OR\n")

    def test_write_when_disconnected(self):
        main.serial_connected = False
        main.serial_port = None
        self.assertFalse(write_serial_gate("AND"))


class StatusApiValveTests(unittest.TestCase):
    def setUp(self):
        main.last_valve_a = 0
        main.last_valve_b = 1
        main.last_valve_y = 0
        main.last_valve_gate = "AND"
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_valve_a = None
        main.last_valve_b = None
        main.last_valve_y = None
        main.last_valve_gate = None

    def test_status_includes_valve_fields(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_valve_a"], 0)
        self.assertEqual(data["last_valve_b"], 1)
        self.assertEqual(data["last_valve_y"], 0)
        self.assertEqual(data["last_valve_gate"], "AND")


class GateApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    def tearDown(self):
        main.serial_connected = False
        main.serial_port = None

    def test_invalid_gate_returns_400(self):
        response = self.client.post("/api/valve/gate", json={"gate": "INVALID"})
        self.assertEqual(response.status_code, 400)

    def test_disconnected_returns_503(self):
        main.serial_connected = False
        main.serial_port = None
        response = self.client.post("/api/valve/gate", json={"gate": "AND"})
        self.assertEqual(response.status_code, 503)

    @patch("main.write_serial_gate", return_value=True)
    def test_success_xor(self, mock_write):
        response = self.client.post("/api/valve/gate", json={"gate": "XOR"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "gate": "XOR"})
        mock_write.assert_called_once_with("XOR")

    @patch("main.write_serial_gate", return_value=True)
    def test_success(self, mock_write):
        response = self.client.post("/api/valve/gate", json={"gate": "OR"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "gate": "OR"})
        mock_write.assert_called_once_with("OR")


class ValvesPageTests(unittest.TestCase):
    def test_valves_page_loads(self):
        client = TestClient(main.app)
        response = client.get("/valves")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


class WebSocketValveCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_valve_a = 1
        main.last_valve_b = 0
        main.last_valve_y = 0
        main.last_valve_gate = "AND"
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_valve_a = None
        main.last_valve_b = None
        main.last_valve_y = None
        main.last_valve_gate = None

    def test_connect_sends_cached_valve(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 5:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                if any(m["type"] == "valve" for m in messages):
                    break
        valve = next(m for m in messages if m["type"] == "valve")
        self.assertTrue(valve["cached"])
        self.assertEqual(valve["a"], 1)
        self.assertEqual(valve["b"], 0)
        self.assertEqual(valve["y"], 0)
        self.assertEqual(valve["gate"], "AND")
