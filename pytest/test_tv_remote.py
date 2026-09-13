import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from main import parse_remote_line, read_serial


class ParseRemoteLineTests(unittest.TestCase):
    def test_known_label(self):
        self.assertEqual(parse_remote_line("Remote: POWER"), ("POWER", None))

    def test_label_with_plus(self):
        self.assertEqual(parse_remote_line("Remote: VOL+"), ("VOL+", None))

    def test_unknown_with_hex(self):
        self.assertEqual(
            parse_remote_line("Remote: UNKNOWN (0xFF629D)"),
            ("UNKNOWN", 0xFF629D),
        )

    def test_startup_banner_ignored(self):
        self.assertIsNone(parse_remote_line("Remote ready"))

    def test_invalid_lines(self):
        self.assertIsNone(parse_remote_line("Pressed: 5"))
        self.assertIsNone(parse_remote_line("Remote:"))
        self.assertIsNone(parse_remote_line(""))


class ReadSerialRemoteTests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_remote")
    def test_remote_line_emits_remote(self, mock_notify, mock_stop):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Remote: MUTE\n"

        read_serial(FakePort())

        mock_notify.assert_called_once_with("MUTE", None)

    @patch("main.serial_stop")
    @patch("main.notify_remote")
    def test_unknown_remote_line_emits_code(self, mock_notify, mock_stop):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Remote: UNKNOWN (0xFF629D)\n"

        read_serial(FakePort())

        mock_notify.assert_called_once_with("UNKNOWN", 0xFF629D)


class StatusApiRemoteTests(unittest.TestCase):
    def setUp(self):
        main.last_remote_key = "CH+"
        main.last_remote_code = None
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_remote_key = None
        main.last_remote_code = None

    def test_status_includes_remote_fields(self):
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_remote_key"], "CH+")
        self.assertIsNone(data["last_remote_code"])

    def test_status_includes_unknown_code(self):
        main.last_remote_key = "UNKNOWN"
        main.last_remote_code = 0xFF629D
        response = self.client.get("/api/status")
        data = response.json()
        self.assertEqual(data["last_remote_key"], "UNKNOWN")
        self.assertEqual(data["last_remote_code"], 0xFF629D)


class PageRouteTests(unittest.TestCase):
    def test_tv_remote_page_loads(self):
        client = TestClient(main.app)
        response = client.get("/tv-remote")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("TV Remote", response.text)

    def test_nav_link_on_keypad_page(self):
        client = TestClient(main.app)
        response = client.get("/")
        self.assertIn('href="/tv-remote"', response.text)
        self.assertIn("TV Remote", response.text)


class WebSocketRemoteCacheTests(unittest.TestCase):
    def setUp(self):
        main.last_remote_key = "MUTE"
        main.last_remote_code = None
        self.client = TestClient(main.app)

    def tearDown(self):
        main.last_remote_key = None
        main.last_remote_code = None

    def test_connect_sends_cached_remote(self):
        with self.client.websocket_connect("/ws") as ws:
            messages = []
            while len(messages) < 12:
                raw = ws.receive_text()
                messages.append(json.loads(raw))
                if any(m["type"] == "remote" for m in messages):
                    break
        remote = next(m for m in messages if m["type"] == "remote")
        self.assertTrue(remote["cached"])
        self.assertEqual(remote["key"], "MUTE")
        self.assertIsNone(remote["code"])
