"""Live checks: are the endpoints reachable today, and do the keyed ones give
the right answer FOR THIS DESTINATION?

These are not unit tests and they are not deterministic -- they depend on the
network and on third-party services that move, get rate-limited, and change
their terms. That is exactly why they exist: every provider this skill uses has
broken at least once mid-project, and the failures were silent.

The destination probe is the important one and it needs a REAL address whose
answer you already know. That is the whole mechanism: the failure being hunted
is a confident wrong answer, not an error, and the only way to catch it is to
check against a known truth.

Configured by scripts/run_tests.py via set_destination(); with no destination
supplied the destination tests skip rather than pass.
"""
import unittest, urllib.parse
from lib.common import get, key, post

_DEST = {"country": None, "address": None, "romanized": None, "bbox": None}


def set_destination(country=None, address=None, romanized=None, bbox=None):
    _DEST.update(country=country, address=address, romanized=romanized, bbox=bbox)


def _inside(lat, lon):
    s, w, n, e = _DEST["bbox"]
    return s <= lat <= n and w <= lon <= e


class TestKeylessEndpoints(unittest.TestCase):
    """The commodity layer. No signup, and the skill must work on these alone."""

    def test_climate_archive_returns_daily_series(self):
        d = get("https://archive-api.open-meteo.com/v1/archive"
                "?latitude=0&longitude=0&start_date=2024-01-01&end_date=2024-01-03"
                "&daily=temperature_2m_max&timezone=UTC")
        self.assertIn("daily", d)
        self.assertEqual(len(d["daily"]["time"]), 3)

    def test_climate_archive_reports_grid_elevation(self):
        # Without this the grid-snap check cannot run, and a highland base
        # silently reports a valley's temperatures.
        d = get("https://archive-api.open-meteo.com/v1/archive"
                "?latitude=46.5&longitude=8.0&start_date=2024-01-01"
                "&end_date=2024-01-02&daily=temperature_2m_max&timezone=UTC")
        self.assertIn("elevation", d)

    def test_daylight_comes_back_with_sunrise_and_sunset(self):
        d = get("https://archive-api.open-meteo.com/v1/archive"
                "?latitude=0&longitude=0&start_date=2024-06-01&end_date=2024-06-02"
                "&daily=sunrise,sunset&timezone=UTC")
        self.assertTrue(d["daily"]["sunrise"][0])

    def test_public_holidays(self):
        d = get("https://date.nager.at/api/v3/PublicHolidays/2024/US")
        self.assertTrue(isinstance(d, list) and d)

    def test_fx_returns_a_rate_with_its_date(self):
        # An undated rate is worthless a month later.
        from lib import money
        d = get("https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR")
        self.assertIn("date", d)
        self.assertIn("EUR", d["rates"])
        self.assertTrue(money.sym("EUR"))

    def test_nominatim_is_reachable(self):
        d = get("https://nominatim.openstreetmap.org/search"
                "?q=Eiffel+Tower&format=json&limit=1")
        self.assertTrue(d)


class TestKeyedProviders(unittest.TestCase):
    """Skipped, not failed, when a key is absent: a missing key is a quality
    reduction the skill degrades around, never an error."""

    def test_places_key_is_accepted_and_returns_the_rich_fields(self):
        k = key("GOOGLE_PLACES_API_KEY")
        if not k:
            self.skipTest("GOOGLE_PLACES_API_KEY not configured")
        fields = ("places.id,places.displayName,places.businessStatus,"
                  "places.location,places.rating")
        j = post("https://places.googleapis.com/v1/places:searchText",
                 {"textQuery": "Eiffel Tower", "maxResultCount": 1},
                 headers={"X-Goog-Api-Key": k, "X-Goog-FieldMask": fields})
        p = (j.get("places") or [None])[0]
        self.assertIsNotNone(p, "key accepted but no result")
        self.assertIn("id", p)
        self.assertIn("location", p)

    def test_serpapi_key_if_present(self):
        k = key("SERPAPI_API_KEY")
        if not k:
            self.skipTest("SERPAPI_API_KEY not configured — "
                          "multi-city and open-jaw fares will be UNVERIFIED")
        d = get("https://serpapi.com/account?api_key=" + urllib.parse.quote(k))
        self.assertNotIn("error", {k_.lower() for k_ in d})


class TestDestinationProbe(unittest.TestCase):
    """The per-destination check. A key that authenticates is not a key that
    works HERE -- one geocoder answers with the wrong country for local-script
    addresses, with HTTP 200 and nothing to signal it."""

    def setUp(self):
        if not (_DEST["address"] and _DEST["bbox"]):
            self.skipTest("no destination supplied — pass --country/--address/--bbox")

    def test_places_resolves_the_local_script_address_inside_the_bounds(self):
        k = key("GOOGLE_PLACES_API_KEY")
        if not k:
            self.skipTest("GOOGLE_PLACES_API_KEY not configured")
        j = post("https://places.googleapis.com/v1/places:searchText",
                 {"textQuery": _DEST["address"], "maxResultCount": 1},
                 headers={"X-Goog-Api-Key": k,
                          "X-Goog-FieldMask": "places.location,places.formattedAddress"})
        p = (j.get("places") or [None])[0]
        self.assertIsNotNone(p, "no result for the local-script probe")
        loc = p["location"]
        self.assertTrue(_inside(loc["latitude"], loc["longitude"]),
                        f"resolved OUTSIDE the expected area: {p.get('formattedAddress')}")

    def test_geoapify_is_checked_and_may_legitimately_fail(self):
        k = key("GEOAPIFY_API_KEY")
        if not k:
            self.skipTest("GEOAPIFY_API_KEY not configured")
        u = ("https://api.geoapify.com/v1/geocode/search?"
             + urllib.parse.urlencode({"text": _DEST["address"], "format": "json",
                                       "limit": 1, "apiKey": k}))
        r = (get(u).get("results") or [None])[0]
        if not r:
            self.skipTest("returned an honest empty — safe behaviour")
        self.assertTrue(
            _inside(r["lat"], r["lon"]),
            f"resolved OUTSIDE the expected area ({r.get('country')}). "
            f"Record it in api-compatibility.md with today's date and use "
            f"another provider for this destination.")

    def test_nominatim_is_honest_about_what_it_cannot_find(self):
        q = _DEST["romanized"] or _DEST["address"]
        d = get("https://nominatim.openstreetmap.org/search?"
                + urllib.parse.urlencode({"q": q, "format": "json", "limit": 1}))
        if not d:
            self.skipTest("honest empty — better behaviour than a wrong answer")
        self.assertTrue(_inside(float(d[0]["lat"]), float(d[0]["lon"])),
                        "returned a result outside the expected area")
