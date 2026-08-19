"""Table rendering and link injection, against fabricated venues."""
import unittest
from lib import render, money

# Fabricated fixtures. No real place appears in a unit test -- these exist to
# exercise the transformation, not to describe anywhere.
PLACES = {
    "Aldwych Refectory": {
        "name": "Aldwych Refectory", "place_id": "PID-1",
        "maps_url": "https://maps.google.com/?cid=1",
        "status": "OPERATIONAL", "rating": 4.4, "reviews": 1200,
        "price": "AAA 1,000–2,000", "price_level": "PRICE_LEVEL_MODERATE",
        "hours": ["Monday: Closed"] + [f"{d}: 11:00 AM – 9:00 PM" for d in
                  ("Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")],
        "access": "step-free: entrance", "cash_only": True,
        "site": "https://example.invalid/refectory",
    },
    "Braddock House": {
        "name": "Braddock House", "place_id": "PID-2",
        "maps_url": "https://maps.google.com/?cid=2",
        "status": "OPERATIONAL", "rating": 4.1, "reviews": 90,
        "price": "", "price_level": "PRICE_LEVEL_VERY_EXPENSIVE",
        "hours": [], "access": "", "cards": True, "site": "",
    },
}


class TestMapLinks(unittest.TestCase):
    def test_place_id_form_is_preferred(self):
        url = render.maps_url(name="Somewhere", place_id="ABC")
        self.assertIn("query_place_id=ABC", url)

    def test_coordinates_are_used_when_there_is_no_id(self):
        self.assertIn("1.5,2.5", render.maps_url(lat=1.5, lon=2.5))

    def test_place_name_is_a_link_and_is_not_bolded(self):
        out = render.place_link(PLACES["Aldwych Refectory"])
        self.assertIn("<a href=", out)
        self.assertNotIn("<b>", out)

    def test_both_link_shapes_are_recognised(self):
        import re
        for url in ("https://www.google.com/maps/search/?api=1&query=x",
                    "https://maps.google.com/?cid=123"):
            self.assertRegex(url, render.MAPS_PATTERN)


class TestSpend(unittest.TestCase):
    def setUp(self):
        money.set_rate(100.0, "AAA", "BBB", "0000-00-00")

    def test_real_figure_wins_and_shows_both_currencies(self):
        out = render.spend(PLACES["Aldwych Refectory"])
        self.assertIn("1,000–2,000", out)
        self.assertNotIn("MID", out, "band must not sit beside a real figure")

    def test_band_is_used_only_when_there_is_no_figure(self):
        out = render.spend(PLACES["Braddock House"])
        self.assertIn("TOP", out)
        self.assertIn("band only", out)

    def test_legacy_files_storing_the_enum_in_price_still_render(self):
        out = render.spend({"price": "PRICE_LEVEL_MODERATE"})
        self.assertNotIn("PRICE_LEVEL", out)
        self.assertIn("MID", out)


class TestTables(unittest.TestCase):
    def test_row_width_mismatch_raises_rather_than_shipping(self):
        with self.assertRaises(ValueError):
            render.table("cap", ["A", "B", "C"], [["1", "2"]])

    def test_every_table_carries_a_caption_and_scrolls(self):
        out = render.table("the method", ["A"], [["1"]])
        self.assertIn("<caption>the method</caption>", out)
        self.assertIn('class="scroll"', out)

    def test_lodging_declares_its_own_arithmetic_basis(self):
        out = render.lodging("cap", [("Aldwych Refectory", "x", "y", "z", "n")],
                             PLACES, nights=3, people=4)
        self.assertIn('data-nights="3"', out)
        self.assertIn('data-people="4"', out)

    def test_venue_table_emits_the_standard_columns(self):
        out = render.venues("cap", [("Aldwych Refectory", "what", "verdict", "")],
                            PLACES, kind="food")
        for col in ("Hours", "Typical spend", "Rating", "Step-free", "Payment"):
            self.assertIn(f"<th>{col}</th>", out)
        self.assertIn("Still open?", out)


class TestLinkInjection(unittest.TestCase):
    def test_bolded_name_is_unbolded_then_linked(self):
        # `<b>Name</b>` defeated the injector and whole sections shipped with no
        # map links while every other check reported clean.
        html = "<tr><td><b>Aldwych Refectory</b></td><td>note</td></tr>"
        out = render.inject_links(render.unbold_identity(html), PLACES)
        self.assertIn("<a href=", out)
        self.assertNotIn("<b>Aldwych Refectory</b>", out)

    def test_headings_are_left_alone(self):
        # The section heading carries the city link once per group; letting the
        # injector reach it repeated that link in every heading.
        html = "<h2>Aldwych Refectory</h2><p>Aldwych Refectory again</p>"
        out = render.inject_links(html, PLACES)
        self.assertIn("<h2>Aldwych Refectory</h2>", out)

    def test_existing_anchors_are_not_nested(self):
        html = '<p><a href="x">Aldwych Refectory</a></p>'
        out = render.inject_links(html, PLACES)
        self.assertEqual(out.count("<a "), 1)

    def test_injector_does_not_link_inside_its_own_output(self):
        # Names are linked longest-first, so "<Venue> Hotel" gets an anchor and
        # then the shorter "<Venue>" matched inside it -- nested <a> tags, which
        # browsers fix by closing the outer link early. Seven shipped.
        places = {
            "Aldwych Refectory": {"maps_url": "https://maps.example/1"},
            "Aldwych Refectory Hotel": {"maps_url": "https://maps.example/2"},
        }
        out = render.inject_links("<p>Aldwych Refectory Hotel</p>", places)
        self.assertEqual(out.count("<a "), 1)
        self.assertNotRegex(out, r'<a\b[^>]*>(?:(?!</a>).)*?<a\b')

    def test_bold_outside_the_identity_cell_survives(self):
        # Bold in later cells carries a finding -- a closure day, a warning.
        html = "<tr><td><b>Aldwych Refectory</b></td><td><b>Closed Mon</b></td></tr>"
        out = render.unbold_identity(html)
        self.assertIn("<b>Closed Mon</b>", out)

    def test_strong_is_unbolded_too(self):
        # <strong> and <b> render identically. Stripping only <b> let 40 bolded
        # identity cells ship while the rule reported success.
        html = "<tr><td><strong>Aldwych Refectory</strong></td><td>note</td></tr>"
        out = render.unbold_identity(html)
        self.assertNotIn("<strong>Aldwych Refectory</strong>", out)

    def test_rows_carrying_attributes_are_not_skipped(self):
        # Matching a literal `<tr>` skipped every `<tr class=...>` -- the same
        # failure that once made the checker skip every `<table class=...>`.
        html = '<tr class="hi"><td><b>Aldwych Refectory</b></td><td>note</td></tr>'
        out = render.unbold_identity(html)
        self.assertNotIn("<b>Aldwych Refectory</b>", out)

    def test_strong_in_a_later_cell_survives(self):
        html = ("<tr><td><strong>Aldwych Refectory</strong></td>"
                "<td><strong>Cash only</strong></td></tr>")
        out = render.unbold_identity(html)
        self.assertIn("<strong>Cash only</strong>", out)
