"""SerpApi client and hotel-rate normalisation. Offline; no network, no key.

The rate arithmetic is tested because dividing a stay total by people and nights
is exactly the sum that has gone wrong by hand before, and because a lodging
matrix publishes the per-person figure rather than the room figure the API
returns.
"""
import importlib, pathlib, sys, tempfile, unittest
from unittest import mock

from lib import serpapi

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
hotels = importlib.import_module("hotels")


def prop(name, per_night=None, total=None, **kw):
    d = {"name": name, "property_token": "tok-" + name[:4]}
    if per_night is not None:
        d["rate_per_night"] = {"extracted_lowest": per_night}
    if total is not None:
        d["total_rate"] = {"extracted_lowest": total}
    d.update(kw)
    return d


class RateRows(unittest.TestCase):
    def test_per_person_night_is_derived_from_the_stay_total(self):
        # The API returns a ROOM rate; the matrix publishes per person per night.
        r = hotels.rows({"properties": [prop("Thornbury Lodge", 30000, 90000)]},
                        nights=3, people=4)[0]
        self.assertEqual(r["per_night_room"], 30000)
        self.assertEqual(r["total_stay_room"], 90000)
        self.assertEqual(r["per_person_night"], 7500)   # 90000 / 4 / 3

    def test_missing_total_is_filled_from_the_nightly_rate(self):
        r = hotels.rows({"properties": [prop("Rivergate Inn", per_night=20000)]},
                        nights=2, people=2)[0]
        self.assertEqual(r["total_stay_room"], 40000)

    def test_missing_nightly_is_filled_from_the_total(self):
        r = hotels.rows({"properties": [prop("Rivergate Inn", total=40000)]},
                        nights=2, people=2)[0]
        self.assertEqual(r["per_night_room"], 20000)

    def test_a_property_with_no_rate_is_marked_unpriced_not_zero(self):
        # No rate means sold out or not sold here — a finding, never a free room.
        r = hotels.rows({"properties": [prop("Fully Booked House")]},
                        nights=3, people=4)[0]
        self.assertFalse(r["priced"])
        self.assertIsNone(r["per_person_night"])

    def test_checkout_must_be_after_checkin(self):
        with self.assertRaises(SystemExit):
            hotels.nights_between("2027-03-17", "2027-03-17")

    def test_nights_are_counted_not_guessed(self):
        self.assertEqual(hotels.nights_between("2027-03-14", "2027-03-17"), 3)


class Caching(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # patch the cache directory itself: it is deliberately independent of
        # the output directory now, so tests must isolate the real thing
        self.p = mock.patch.object(serpapi, "_cache_dir",
                                   lambda: pathlib.Path(self.tmp.name))
        self.p.start()

    def tearDown(self):
        self.p.stop()
        self.tmp.cleanup()

    def test_the_credential_never_reaches_a_cache_filename(self):
        a = serpapi._cache_key({"q": "x", "api_key": "SECRET-A"})
        b = serpapi._cache_key({"q": "x", "api_key": "SECRET-B"})
        self.assertEqual(a, b, "cache key must ignore the key entirely")
        self.assertNotIn("SECRET", a)

    def test_different_dates_are_different_cache_entries(self):
        a = serpapi._cache_key({"q": "x", "check_in_date": "2027-03-14"})
        b = serpapi._cache_key({"q": "x", "check_in_date": "2027-03-15"})
        self.assertNotEqual(a, b)

    def test_absent_key_degrades_instead_of_raising(self):
        # A missing key is a quality reduction, never an error.
        with mock.patch.object(serpapi, "key", lambda n: ""):
            data, meta = serpapi.search("google_hotels", q="anywhere")
        self.assertIsNone(data)
        self.assertEqual(meta["spent"], 0)

    def test_a_cache_hit_spends_no_quota(self):
        entry = {"fetched_at": 0, "engine": "google_hotels",
                 "data": {"properties": []}}
        with mock.patch.object(serpapi, "key", lambda n: "k"):
            ck = serpapi._cache_key({"q": "town", "engine": "google_hotels"})
            path = pathlib.Path(self.tmp.name)
            import json
            (path / f"google_hotels-{ck}.json").write_text(
                json.dumps(entry), encoding="utf-8")
            with mock.patch.object(serpapi, "get") as g:
                data, meta = serpapi.search("google_hotels", q="town")
            g.assert_not_called()
        self.assertTrue(meta["cached"])
        self.assertEqual(meta["spent"], 0)

    def test_an_api_level_error_raises_rather_than_looking_empty(self):
        # SerpApi reports failures as HTTP 200 with an "error" field. Unchecked,
        # a failed search is indistinguishable from a search with no results.
        with mock.patch.object(serpapi, "key", lambda n: "k"), \
             mock.patch.object(serpapi.quota, "check", lambda *a, **k: None), \
             mock.patch.object(serpapi, "get",
                               lambda url: {"error": "Invalid API key"}):
            with self.assertRaises(RuntimeError) as cm:
                serpapi.search("google_hotels", q="town")
        self.assertIn("Invalid API key", str(cm.exception))

    def test_age_note_reads_in_human_units(self):
        import time
        self.assertEqual(serpapi.age_note({"fetched_at": time.time()}), "just now")
        self.assertTrue(serpapi.age_note(
            {"fetched_at": time.time() - 90000}).endswith("d old"))
