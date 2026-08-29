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
    @patch("main.notify_current")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_pot_line_emits_pot_and_detected(
        self, mock_logic, mock_pot, mock_detected, mock_current, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Pot: 2.50 V | Logic: 1 | PWM: 128\n"

        read_serial(FakePort())

        mock_logic.assert_not_called()
        mock_pot.assert_called_once_with(2.5)
        mock_detected.assert_called_once_with(1.0)
        mock_current.assert_not_called()

    @patch("main.serial_stop")
    @patch("main.notify_current")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_pot_line_with_current_emits_current(
        self, mock_logic, mock_pot, mock_detected, mock_current, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return (
                    b"Pot: 4.00 V | Logic: 1 | PWM: 200 | Shunt: 0.123 V | "
                    b"Current: 12.3 mA\n"
                )

        read_serial(FakePort())

        mock_logic.assert_not_called()
        mock_pot.assert_called_once_with(4.0)
        mock_detected.assert_called_once_with(1.0)
        mock_current.assert_called_once_with(12.3)

    @patch("main.serial_stop")
    @patch("main.notify_resistance")
    @patch("main.notify_current")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_pot_line_with_resistance_emits_resistance(
        self, mock_logic, mock_pot, mock_detected, mock_current, mock_resistance, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return (
                    b"Pot: 4.00 V | Logic: 1 | Shunt: 0.123 V | Current: 12.3 mA | "
                    b"LED Resistance: 162.6 Ohm\n"
                )

        read_serial(FakePort())

        mock_logic.assert_not_called()
        mock_pot.assert_called_once_with(4.0)
        mock_detected.assert_called_once_with(1.0)
        mock_current.assert_called_once_with(12.3)
        mock_resistance.assert_called_once_with(162.6)

    @patch("main.serial_stop")
    @patch("main.notify_resistance")
    @patch("main.notify_current")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_simple01_combined_line_emits_all(
        self, mock_logic, mock_pot, mock_detected, mock_current, mock_resistance, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return (
                    b"Signal: 1 | Pot: 4.00 V | Logic: 1 (HIGH) | Shunt: 0.123 V | "
                    b"Current: 12.3 mA | LED Resistance: 162.6 Ohm\n"
                )

        read_serial(FakePort())

        mock_logic.assert_called_once_with(1)
        mock_pot.assert_called_once_with(4.0)
        mock_detected.assert_called_once_with(1.0)
        mock_current.assert_called_once_with(12.3)
        mock_resistance.assert_called_once_with(162.6)

    @patch("main.serial_stop")
    @patch("main.notify_detected")
    @patch("main.notify_potentiometer")
    @patch("main.notify_logic")
    def test_pot_undefined_emits_detected_zero(
        self, mock_logic, mock_pot, mock_detected, mock_stop
    ):
        mock_stop.is_set.side_effect = [False, True]

        class FakePort:
            def readline(self):
                return b"Pot: 2.10 V | Logic: UNDEFINED\n"

        read_serial(FakePort())

        mock_logic.assert_not_called()
        mock_pot.assert_called_once_with(2.1)
        mock_detected.assert_called_once_with(0.0)
