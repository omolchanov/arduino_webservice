import json
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import main
from main import parse_clock_line, parse_display_line, read_serial, write_serial_display


class ParseDisplayLineTests(unittest.TestCase):
    def test_valid_display_line(self):
        self.assertEqual(parse_display_line("Display: 123"), 123)

    def test_zero_display_line(self):
        self.assertEqual(parse_display_line("Display: 0"), 0)

    def test_max_display_line(self):
        self.assertEqual(parse_display_line("Display: 999"), 999)

    def test_invalid_lines(self):
        self.assertIsNone(parse_display_line("Display: 1000"))
        self.assertIsNone(parse_display_line("Pot: 2.50 V | Logic: 0"))
        self.assertIsNone(parse_display_line(""))


class ParseClockLineTests(unittest.TestCase):
    def test_valid_clock_line(self):
        self.assertEqual(parse_clock_line("Clock: 12:00"), "12:00")

    def test_midnight_clock_line(self):
        self.assertEqual(parse_clock_line("Clock: 00:00"), "00:00")

    def test_invalid_clock_lines(self):
        self.assertIsNone(parse_clock_line("Clock: 25:00"))
        self.assertIsNone(parse_clock_line("Clock: 12:60"))
        self.assertIsNone(parse_clock_line("Display: 42"))
        self.assertIsNone(parse_clock_line(""))


class ReadSerialDisplayTests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_display")
    def test_display_line_emits_display(self, mock_notify, mock_stop):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Display: 42\n"

        read_serial(FakePort())

        mock_notify.assert_called_once_with(42)


class ReadSerialClockTests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_clock")
    def test_clock_line_emits_clock(self, mock_notify, mock_stop):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Clock: 12:00\n"

        read_serial(FakePort())

        mock_notify.assert_called_once_with("12:00")


class WriteSerialDisplayTests(unittest.TestCase):
    def tearDown(self):
        main.serial_connected = False
        main.serial_port = None

    def test_write_display_value(self):
        port = MagicMock()
        port.is_open = True
        main.serial_connected = True
        main.serial_port = port

        self.assertTrue(write_serial_display(567))
        port.write.assert_called_once_with(b"S567\n")

    def test_write_invalid_value(self):
        self.assertFalse(write_serial_display(1000))

    def test_write_when_disconnected(self):
        main.serial_connected = False
        main.serial_port = None
        self.assertFalse(write_serial_display(42))


class StatusApiDisplayTests(unittest.TestCase):
    def setUp(self):
        main.last_display_value = 105
        main.last_clock_time = "12:00"
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_display_value = None
        main.last_clock_time = None

    def test_status_includes_display_value(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["display_value"], 105)

    def test_status_includes_clock_time(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["clock_time"], "12:00")


class DisplayValueApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    def tearDown(self):
        main.serial_connected = False
        main.serial_port = None

    def test_invalid_value_returns_400(self):
        response = self.client.post("/api/display/value", json={"value": 1000})
        self.assertEqual(response.status_code, 400)

    def test_disconnected_returns_503(self):
        main.serial_connected = False
        main.serial_port = None
        response = self.client.post("/api/display/value", json={"value": 42})
        self.assertEqual(response.status_code, 503)

    @patch("main.write_serial_display", return_value=True)
    def test_success(self, mock_write):
        response = self.client.post("/api/display/value", json={"value": 42})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "value": 42})
        mock_write.assert_called_once_with(42)


class DisplayPageTests(unittest.TestCase):
    def test_display_page_loads(self):
        client = TestClient(main.app)
        response = client.get("/display")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


class WebSocketDisplayCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_display_value = 123
        main.last_clock_time = "14:30"
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_display_value = None
        main.last_clock_time = None

    def test_connect_sends_cached_display(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 5:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                if any(m["type"] == "display" for m in messages):
                    break
        display = next(m for m in messages if m["type"] == "display")
        self.assertTrue(display["cached"])
        self.assertEqual(display["value"], 123)

    def test_connect_sends_cached_clock(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 6:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                if any(m["type"] == "clock" for m in messages):
                    break
        clock = next(m for m in messages if m["type"] == "clock")
        self.assertTrue(clock["cached"])
        self.assertEqual(clock["time"], "14:30")


class DisplayCounterLogicTests(unittest.TestCase):
    def test_increment_hundreds_from_five(self):
        self.assertEqual(self._increment_hundreds(5), 105)

    def test_increment_hundreds_wraps_at_nine(self):
        self.assertEqual(self._increment_hundreds(900), 0)

    def test_increment_tens_from_ten(self):
        self.assertEqual(self._increment_tens(10), 20)

    def test_increment_ones_from_seven(self):
        self.assertEqual(self._increment_ones(7), 8)

    def test_increment_ones_wraps_at_nine(self):
        self.assertEqual(self._increment_ones(9), 0)

    def test_clamp_counter_range(self):
        self.assertEqual(self._clamp(0), 0)
        self.assertEqual(self._clamp(999), 999)
        self.assertEqual(self._clamp(-1), 0)
        self.assertEqual(self._clamp(1000), 999)

    def test_reset_counter(self):
        self.assertEqual(self._reset(), 0)

    @staticmethod
    def _reset() -> int:
        return 0

    @staticmethod
    def _increment_digit(d: int) -> int:
        return (d + 1) % 10

    def _increment_hundreds(self, counter: int) -> int:
        h, t, o = counter // 100, (counter // 10) % 10, counter % 10
        h = self._increment_digit(h)
        return self._clamp(h * 100 + t * 10 + o)

    def _increment_tens(self, counter: int) -> int:
        h, t, o = counter // 100, (counter // 10) % 10, counter % 10
        t = self._increment_digit(t)
        return self._clamp(h * 100 + t * 10 + o)

    def _increment_ones(self, counter: int) -> int:
        h, t, o = counter // 100, (counter // 10) % 10, counter % 10
        o = self._increment_digit(o)
        return self._clamp(h * 100 + t * 10 + o)

    @staticmethod
    def _clamp(value: int) -> int:
        if value < 0:
            return 0
        if value > 999:
            return 999
        return value
