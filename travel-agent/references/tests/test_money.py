"""Currency formatting. Every case here is a bug that shipped."""
import unittest
from lib import money


class TestSymbols(unittest.TestCase):
    def test_known_code_becomes_a_symbol(self):
        self.assertEqual(money.sym("USD"), "$")

    def test_unknown_code_falls_back_to_the_code(self):
        # Falling back beats dropping the currency: an unfamiliar code is still
        # readable, a missing one is a number with no units.
        self.assertEqual(money.sym("ZZZ"), "ZZZ ")

    def test_lowercase_input_is_accepted(self):
        self.assertEqual(money.sym("eur"), money.sym("EUR"))


class TestFormatting(unittest.TestCase):
    def setUp(self):
        money.set_rate(100.0, "AAA", "BBB", "0000-00-00")

    def test_both_currencies_are_shown(self):
        out = money.pair(1000, 2000)
        self.assertIn("1,000–2,000", out)
        self.assertIn(money.sym("BBB"), out)

    def test_precision_is_decided_once_for_the_whole_range(self):
        # `6.29–13` mixes two decimals with none and reads as sloppiness.
        out = money.convert(500, 2000)          # -> 5.00 and 20.00
        self.assertEqual(out.count("."), 2, out)

    def test_symbol_is_printed_once_per_range(self):
        # The local side writes "X1,000–2,000", so the converted side must not
        # write "Y6–Y13".
        out = money.convert(1000, 2000)
        self.assertEqual(out.count(money.sym("BBB")), 1, out)

    def test_open_ended_range_is_marked_with_a_plus(self):
        # A single bound means "from X", and the reader has to be able to tell
        # that from a closed range.
        self.assertTrue(money.local(1000).endswith("+"), money.local(1000))
        self.assertTrue(money.convert(1000).endswith("+"))
        self.assertFalse(money.local(1000, 2000).endswith("+"))

    def test_degrades_to_local_only_when_no_rate(self):
        money._STATE["rate"] = None
        out = money.pair(1000, 2000)
        self.assertNotIn("span", out)           # no converted half appended
        self.assertIn("1,000–2,000", out)

    def test_parse_round_trips_a_formatted_range(self):
        self.assertEqual(money.parse("XYZ 1,000–2,000"), (1000, 2000))
        self.assertEqual(money.parse("XYZ 900"), (900, None))
        self.assertIsNone(money.parse("no digits here"))

    def test_rate_note_is_never_undated(self):
        money.set_rate(7.5, "AAA", "BBB", "1999-12-31")
        self.assertIn("1999-12-31", money.rate_note())
        money.set_rate(7.5, "AAA", "BBB", "")
        self.assertIn("undated", money.rate_note())
