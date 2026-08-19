"""Machine values must never reach a reader. Each test is a shipped defect."""
import unittest
from lib import humanize as H
from lib import money


class TestBands(unittest.TestCase):
    def test_every_price_level_maps_to_a_short_label(self):
        for enum in ("PRICE_LEVEL_FREE", "PRICE_LEVEL_INEXPENSIVE",
                     "PRICE_LEVEL_MODERATE", "PRICE_LEVEL_EXPENSIVE",
                     "PRICE_LEVEL_VERY_EXPENSIVE"):
            out = H.band(enum)
            self.assertTrue(out, f"{enum} has no label")
            self.assertNotIn("PRICE_LEVEL", out)

    def test_bands_are_colour_coded_cheap_to_expensive(self):
        self.assertIn("c-ok", H.band("PRICE_LEVEL_INEXPENSIVE"))
        self.assertIn("c-warn", H.band("PRICE_LEVEL_MODERATE"))
        self.assertIn("c-flag", H.band("PRICE_LEVEL_VERY_EXPENSIVE"))

    def test_unknown_level_yields_nothing_rather_than_a_guess(self):
        self.assertEqual(H.band("PRICE_LEVEL_UNSPECIFIED"), "")
        self.assertEqual(H.band(""), "")


class TestStatus(unittest.TestCase):
    def test_api_codes_become_sentences(self):
        for code in ("OPERATIONAL", "CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY",
                     "NO_MATCH", "?"):
            out = H.status(code)
            self.assertNotIn("_", out.replace("c-ok", "").replace("c-warn", "")
                             .replace("c-flag", ""), f"{code} leaked an enum")

    def test_lookup_failure_is_readable(self):
        self.assertIn("Lookup failed", H.status("LOOKUP_FAILED TypeError"))


class TestValues(unittest.TestCase):
    def test_none_never_reaches_the_reader(self):
        # Python's None printed into a document reads as a bug, correctly.
        self.assertNotIn("None", H.value(None))

    def test_booleans_become_words(self):
        self.assertEqual(H.value(True), "yes")
        self.assertEqual(H.value(False), "no")


class TestHours(unittest.TestCase):
    def test_closed_days_survive_compaction(self):
        # Closure days have ruined more itineraries than any other single fact,
        # so they must never be the thing compaction drops.
        hrs = ["Monday: Closed"] + [f"{d}: 9:00 AM – 5:00 PM" for d in
               ("Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")]
        out = H.hours(hrs)
        self.assertIn("Closed Mon", out)
        self.assertIn("9:00am", out)

    def test_uniform_week_is_labelled_daily(self):
        hrs = [f"{d}: 10:00 AM – 6:00 PM" for d in H.DAYS]
        self.assertTrue(H.hours(hrs).startswith("Daily"))

    def test_missing_hours_are_marked_not_invented(self):
        self.assertIn("UNVERIFIED", H.hours([]))


class TestAccess(unittest.TestCase):
    def test_positive_and_negative_are_distinguishable(self):
        self.assertIn("c-ok", H.access("step-free: entrance, restroom"))
        self.assertIn("c-flag", H.access("no entrance"))

    def test_field_names_never_appear(self):
        self.assertNotIn("wheelchair", H.access("step-free: entrance").lower())


class TestScrub(unittest.TestCase):
    def test_null_only_cells_are_replaced(self):
        self.assertNotIn("None", H.scrub("<td>None</td>"))
        self.assertNotIn("null", H.scrub("<td>null</td>"))

    def test_english_none_in_a_sentence_survives(self):
        # "None required." is correct prose; only a bare cell is a leak.
        keep = "<td>None required. Check the official page.</td>"
        self.assertIn("None required", H.scrub(keep))

    def test_status_enums_are_translated(self):
        self.assertNotIn("CLOSED_PERMANENTLY", H.scrub("<td>CLOSED_PERMANENTLY</td>"))

    def test_every_known_currency_code_becomes_a_symbol(self):
        # An earlier version listed five codes by hand, so a trip in any other
        # currency silently shipped the bare ISO code.
        for code, symbol in list(money.SYMBOL.items())[:12]:
            out = H.scrub(f"<td>{code} 250</td>")
            self.assertNotIn(f"{code} 250", out, f"{code} not symbolized")
            self.assertIn(symbol, out)
