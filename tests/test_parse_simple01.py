import unittest

from main import parse_simple01_line


class ParseSimple01LineTests(unittest.TestCase):
    def test_high_line(self):
        result = parse_simple01_line(
            "Generated: 1 | Potentiometer: 2.50 V | Detected: 1"
        )
        self.assertEqual(result, (1, 2.5, 1))

    def test_low_line(self):
        result = parse_simple01_line(
            "Generated: 0 | Potentiometer: 1.20 V | Detected: 0"
        )
        self.assertEqual(result, (0, 1.2, 0))

    def test_invalid_line_returns_none(self):
        self.assertIsNone(parse_simple01_line("Generated: 1"))
        self.assertIsNone(parse_simple01_line("Distance: 10.0 cm"))
        self.assertIsNone(parse_simple01_line(""))
