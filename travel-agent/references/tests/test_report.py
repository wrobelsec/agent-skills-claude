"""The report builder, and the structural rules it exists to enforce."""
import re, unittest
from lib.report import Report


def minimal(**kw):
    """Smallest report that satisfies the structural rules, using invented
    place names so no test describes a real destination."""
    r = Report("Trip", "subtitle", {"Dates": "<range>"}, **kw)
    r.group("Start here")
    r.section("critical", "Critical", "<p>deadlines</p>")
    r.group("Calder", place="Calder, Vantia")
    r.section("calder-food", "Eating", "<p>food</p>", title="Eating — Calder")
    r.group("Trip-wide")
    r.section("entry", "Entry", "<p>entry</p>")
    r.group("Honesty")
    r.section("sources", "Sources", "<p>sources</p>")
    return r


class TestHeadingOwnership(unittest.TestCase):
    def test_body_with_its_own_h2_is_rejected(self):
        # THE bug this class exists for: a section shipped its heading twice
        # because the body and the assembly each believed they owned it.
        r = Report("Trip")
        r.group("Start here")
        with self.assertRaises(ValueError) as cm:
            r.section("critical", "Critical", "<h2>Critical</h2><p>x</p>")
        self.assertIn("owns", str(cm.exception))

    def test_builder_emits_exactly_one_heading_per_section(self):
        html = minimal().html()
        for block in re.findall(r"<section id=.*?</section>", html, re.S):
            self.assertEqual(block.count("<h2>"), 1, block[:80])


class TestStructure(unittest.TestCase):
    def test_section_before_group_is_rejected(self):
        with self.assertRaises(ValueError):
            Report("Trip").section("critical", "Critical", "<p>x</p>")

    def test_first_group_must_be_start_here(self):
        r = Report("Trip"); r.group("Elsewhere")
        r.section("critical", "C", "<p>x</p>")
        with self.assertRaises(ValueError):
            r.validate()

    def test_last_groups_must_be_trip_wide_then_honesty(self):
        r = Report("Trip")
        r.group("Start here"); r.section("critical", "C", "<p>x</p>")
        r.group("Honesty");    r.section("sources", "S", "<p>x</p>")
        with self.assertRaises(ValueError):
            r.validate()

    def test_first_section_must_be_critical(self):
        r = Report("Trip")
        r.group("Start here"); r.section("status", "Status", "<p>x</p>")
        r.group("Trip-wide");  r.section("entry", "E", "<p>x</p>")
        r.group("Honesty");    r.section("sources", "S", "<p>x</p>")
        with self.assertRaises(ValueError) as cm:
            r.validate()
        self.assertIn("critical", str(cm.exception))

    def test_duplicate_ids_are_rejected(self):
        r = Report("Trip")
        r.group("Start here")
        r.section("critical", "C", "<p>x</p>")
        r.section("critical", "C again", "<p>y</p>")
        r.group("Trip-wide"); r.section("entry", "E", "<p>x</p>")
        r.group("Honesty");   r.section("sources", "S", "<p>x</p>")
        with self.assertRaises(ValueError) as cm:
            r.validate()
        self.assertIn("duplicate", str(cm.exception))


class TestNavigation(unittest.TestCase):
    def test_every_section_appears_in_the_rail(self):
        html = minimal().html()
        ids = re.findall(r'<section id="([^"]+)"', html)
        rail = html[html.index("<nav"):html.index("</nav>")]
        for sid in ids:
            self.assertIn(f'href="#{sid}"', rail, f"{sid} missing from rail")

    def test_mobile_menu_mirrors_the_rail(self):
        html = minimal().html()
        self.assertIn('id="mobnav-menu"', html)
        for sid in re.findall(r'<section id="([^"]+)"', html):
            menu = html[html.index('id="mobnav-menu"'):html.index("</nav>")]
            self.assertIn(f'href="#{sid}"', menu + html)

    def test_city_link_appears_once_per_group(self):
        html = minimal().html()
        heads = re.findall(r"<h2>(.*?)</h2>", html, re.S)
        linked = [h for h in heads if "maps" in h]
        self.assertEqual(len(linked), 1, linked)
