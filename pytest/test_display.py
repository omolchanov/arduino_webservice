import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from main import parse_display_line, read_serial


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


class StatusApiDisplayTests(unittest.TestCase):
    def setUp(self):
        main.last_display_value = 105
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_display_value = None

    def test_status_includes_display_value(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["display_value"], 105)


class DisplayPageTests(unittest.TestCase):
    def test_mulie_page_loads(self):
        client = TestClient(main.app)
        response = client.get("/mulie")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_display_route_removed(self):
        client = TestClient(main.app)
        response = client.get("/display")
        self.assertEqual(response.status_code, 404)


class WebSocketDisplayCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_display_value = 123
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_display_value = None

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
