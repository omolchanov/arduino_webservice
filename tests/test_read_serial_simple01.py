import unittest
from unittest.mock import patch

from main import read_serial


class ReadSerialSimple01Tests(unittest.TestCase):
    @patch("main.serial_stop")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_signal_pin_emits_logic_only(
        self, mock_logic, mock_pot, mock_detected, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"SIGNAL_PIN: Logic 1 (HIGH)\n"

        read_serial(FakePort())

        mock_logic.assert_called_once_with(1)
        mock_pot.assert_not_called()
        mock_detected.assert_not_called()

    @patch("main.serial_stop")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_pot_line_emits_pot_and_detected(
        self, mock_logic, mock_pot, mock_detected, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Pot: 2.50 V | Logic: 1 | PWM: 128\n"

        read_serial(FakePort())

        mock_logic.assert_not_called()
        mock_pot.assert_called_once_with(2.5)
        mock_detected.assert_called_once_with(1.0)

    @patch("main.serial_stop")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_pot_undefined_emits_detected_half(
        self, mock_logic, mock_pot, mock_detected, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Pot: 2.10 V | Logic: UNDEFINED\n"

        read_serial(FakePort())

        mock_logic.assert_not_called()
        mock_pot.assert_called_once_with(2.1)
        mock_detected.assert_called_once_with(0.5)
