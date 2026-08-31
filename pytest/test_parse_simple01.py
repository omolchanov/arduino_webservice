import unittest

from main import parse_pot_line, parse_signal_pin_line


class ParseSignalPinLineTests(unittest.TestCase):
    def test_high_line(self):
        self.assertEqual(parse_signal_pin_line("SIGNAL_PIN: Logic 1 (HIGH)"), 1)

    def test_low_line(self):
        self.assertEqual(parse_signal_pin_line("SIGNAL_PIN: Logic 0 (LOW)"), 0)

    def test_invalid_line_returns_none(self):
        self.assertIsNone(parse_signal_pin_line("Generated: 1"))
        self.assertIsNone(parse_signal_pin_line("Pot: 2.50 V | Logic: 0"))
        self.assertIsNone(parse_signal_pin_line(""))


class ParsePotLineTests(unittest.TestCase):
    def test_low_logic(self):
        self.assertEqual(
            parse_pot_line("Pot: 1.20 V | Logic: 0"), (1.2, 0.0, None, None, None)
        )

    def test_undefined_logic(self):
        self.assertEqual(
            parse_pot_line("Pot: 2.10 V | Logic: UNDEFINED"),
            (2.1, 0.0, None, None, None),
        )

    def test_high_logic_with_pwm(self):
        self.assertEqual(
            parse_pot_line("Pot: 4.00 V | Logic: 1 | PWM: 200"),
            (4.0, 1.0, None, None, None),
        )

    def test_full_line_with_current(self):
        self.assertEqual(
            parse_pot_line(
                "Pot: 4.00 V | Logic: 1 | PWM: 200 | Shunt: 0.123 V | Current: 12.3 mA"
            ),
            (4.0, 1.0, 12.3, None, None),
        )

    def test_full_line_with_resistance(self):
        self.assertEqual(
            parse_pot_line(
                "Pot: 4.00 V | Logic: 1 | Shunt: 0.123 V | Current: 12.3 mA | "
                "LED Resistance: 162.6 Ohm"
            ),
            (4.0, 1.0, 12.3, 162.6, None),
        )

    def test_simple01_combined_line(self):
        self.assertEqual(
            parse_pot_line(
                "Signal: 1 | Pot: 4.00 V | Logic: 1 (HIGH) | Shunt: 0.123 V | "
                "Current: 12.3 mA | LED Resistance: 162.6 Ohm"
            ),
            (4.0, 1.0, 12.3, 162.6, 1),
        )

    def test_simple01_combined_line_low(self):
        self.assertEqual(
            parse_pot_line(
                "Signal: 0 | Pot: 1.20 V | Logic: 0 (LOW) | Shunt: 0.010 V | "
                "Current: 1.0 mA | LED Resistance: 0.0 Ohm"
            ),
            (1.2, 0.0, 1.0, 0.0, 0),
        )

    def test_simple01_combined_line_undefined(self):
        self.assertEqual(
            parse_pot_line(
                "Signal: 1 | Pot: 2.10 V | Logic: UNDEFINED | Shunt: 0.000 V | "
                "Current: 0.0 mA | LED Resistance: 0.0 Ohm"
            ),
            (2.1, 0.0, 0.0, 0.0, 1),
        )

    def test_invalid_line_returns_none(self):
        self.assertIsNone(parse_pot_line("Generated: 1 | Potentiometer: 2.50 V"))
        self.assertIsNone(parse_pot_line("SIGNAL_PIN: Logic 1 (HIGH)"))
        self.assertIsNone(parse_pot_line(""))
