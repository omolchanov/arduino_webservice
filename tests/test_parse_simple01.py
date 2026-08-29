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
        self.assertEqual(parse_pot_line("Pot: 1.20 V | Logic: 0"), (1.2, 0.0))

    def test_undefined_logic(self):
        self.assertEqual(parse_pot_line("Pot: 2.10 V | Logic: UNDEFINED"), (2.1, 0.5))

    def test_high_logic_with_pwm(self):
        self.assertEqual(
            parse_pot_line("Pot: 4.00 V | Logic: 1 | PWM: 200"), (4.0, 1.0)
        )

    def test_invalid_line_returns_none(self):
        self.assertIsNone(parse_pot_line("Generated: 1 | Potentiometer: 2.50 V"))
        self.assertIsNone(parse_pot_line("SIGNAL_PIN: Logic 1 (HIGH)"))
        self.assertIsNone(parse_pot_line(""))
