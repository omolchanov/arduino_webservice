import unittest
from unittest.mock import patch

from main import read_serial


class ReadSerialSimple01Tests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_emits_all_three_from_one_line(
        self, mock_logic, mock_pot, mock_detected, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Generated: 1 | Potentiometer: 2.50 V | Detected: 1\n"

        read_serial(FakePort())

        mock_logic.assert_called_once_with(1)
        mock_pot.assert_called_once_with(2.5)
        mock_detected.assert_called_once_with(1)
