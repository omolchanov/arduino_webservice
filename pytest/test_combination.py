import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from main import parse_mux_line, read_serial


class ParseMuxLineTests(unittest.TestCase):
    def test_mux_line_a0(self):
        self.assertEqual(
            parse_mux_line("A=0  DI0=1  DI1=0  ->  DO=1  (selected: DI0)"),
            (0, 1, 0, 1),
        )

    def test_mux_line_a1(self):
        self.assertEqual(
            parse_mux_line("A=1  DI0=1  DI1=0  ->  DO=0  (selected: DI1)"),
            (1, 1, 0, 0),
        )

    def test_invalid_lines(self):
        self.assertIsNone(parse_mux_line("A = 0 | B = 1 | Y = 0 | Gate = AND"))
        self.assertIsNone(parse_mux_line("MUX 2-to-1  |  A -> selects DI0 (0) or DI1 (1)"))
        self.assertIsNone(parse_mux_line(""))


class ReadSerialMuxTests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_mux")
    def test_mux_line_emits_mux(self, mock_notify, mock_stop):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"A=0  DI0=1  DI1=0  ->  DO=1  (selected: DI0)\n"

        read_serial(FakePort())

        mock_notify.assert_called_once_with(0, 1, 0, 1)


class StatusApiMuxTests(unittest.TestCase):
    def setUp(self):
        main.last_mux_a = 0
        main.last_mux_di0 = 1
        main.last_mux_di1 = 0
        main.last_mux_do = 1
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_mux_a = None
        main.last_mux_di0 = None
        main.last_mux_di1 = None
        main.last_mux_do = None

    def test_status_includes_mux_fields(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_mux_a"], 0)
        self.assertEqual(data["last_mux_di0"], 1)
        self.assertEqual(data["last_mux_di1"], 0)
        self.assertEqual(data["last_mux_do"], 1)


class CombinationPageTests(unittest.TestCase):
    def test_combination_page_loads(self):
        client = TestClient(main.app)
        response = client.get("/combination")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


class WebSocketMuxCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_mux_a = 1
        main.last_mux_di0 = 1
        main.last_mux_di1 = 0
        main.last_mux_do = 0
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_mux_a = None
        main.last_mux_di0 = None
        main.last_mux_di1 = None
        main.last_mux_do = None

    def test_connect_sends_cached_mux(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 6:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                if any(m["type"] == "mux" for m in messages):
                    break
        mux = next(m for m in messages if m["type"] == "mux")
        self.assertTrue(mux["cached"])
        self.assertEqual(mux["a"], 1)
        self.assertEqual(mux["di0"], 1)
        self.assertEqual(mux["di1"], 0)
        self.assertEqual(mux["do"], 0)
