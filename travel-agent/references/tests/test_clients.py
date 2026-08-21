"""The shared provider clients. Offline; every network call is mocked.

These exist because the same provider was being called from more than one
script, each with its own copy of the endpoint and its own idea of backoff.
The tests below pin the behaviour that has to stay identical no matter which
script is calling.
"""
import datetime, importlib, pathlib, sys, unittest
from unittest import mock

from lib import openmeteo, fxrates, quota

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
flights = importlib.import_module("flights")


class OpenMeteoHorizon(unittest.TestCase):
    """The forecast endpoint 400s past ~16 days. A trip is usually months out,
    so choosing the wrong endpoint fails on exactly the queries that matter."""

    def test_a_date_months_away_is_outside_the_horizon(self):
        far = (datetime.date.today() + datetime.timedelta(days=120)).isoformat()
        self.assertFalse(openmeteo.within_forecast_horizon(far))

    def test_a_date_next_week_is_inside(self):
        soon = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        self.assertTrue(openmeteo.within_forecast_horizon(soon))

    def test_a_past_date_is_not_forecastable(self):
        past = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        self.assertFalse(openmeteo.within_forecast_horizon(past))

    def test_far_dates_are_answered_from_a_year_earlier_and_marked_derived(self):
        far = (datetime.date.today() + datetime.timedelta(days=200)).isoformat()
        payload = {"daily": {"sunrise": ["2025-01-01T07:00"],
                             "sunset": ["2025-01-01T17:00"]}}
        with mock.patch.object(openmeteo, "_call", return_value=payload):
            got = openmeteo.solar(0, 0, [far])
        self.assertTrue(got[far]["derived"],
                        "a proxy-year answer must never be presented as observed")
        self.assertEqual(got[far]["source_date"][:4],
                         str(int(far[:4]) - 1))

    def test_every_call_is_counted(self):
        # One place must know how much traffic the skill sends.
        with mock.patch.object(openmeteo, "get", return_value={}), \
             mock.patch.object(quota, "spend") as sp:
            openmeteo.archive(1, 2, "2020-01-01", "2020-01-02", daily=["x"])
        sp.assert_called_once()


class FxChain(unittest.TestCase):
    def test_the_second_provider_is_tried_when_the_first_refuses(self):
        # One host began returning intermittent 403s mid-run; a single-provider
        # design would have made every converted figure UNVERIFIED.
        calls = []

        def flaky(url, tries=2):
            calls.append(url)
            if len(calls) == 1:
                raise RuntimeError("403")
            return {"rates": {"JPY": 150.0}, "date": "2027-01-02"}

        with mock.patch.object(fxrates, "get", side_effect=flaky), \
             mock.patch.object(fxrates.quota, "spend"):
            d = fxrates.fetch("USD", "JPY")
        self.assertEqual(d["rate"], 150.0)
        self.assertEqual(len(calls), 2)

    def test_all_providers_failing_returns_none_rather_than_a_guess(self):
        with mock.patch.object(fxrates, "get", side_effect=RuntimeError("down")), \
             mock.patch.object(fxrates.quota, "spend"):
            self.assertIsNone(fxrates.fetch("USD", "JPY"))

    def test_failed_attempts_are_counted_too(self):
        # A provider that refuses still costs a request; counting only successes
        # understates traffic exactly when traffic is going wrong.
        with mock.patch.object(fxrates, "get", side_effect=RuntimeError("down")), \
             mock.patch.object(fxrates.quota, "spend") as sp:
            fxrates.fetch("USD", "JPY")
        self.assertEqual(sp.call_count, 4)


class FlightRows(unittest.TestCase):
    def test_both_result_buckets_are_kept(self):
        # Google splits results into best/other; taking only the first hides
        # the cheaper-but-slower options a traveller most wants to weigh.
        data = {"best_flights": [{"price": 1199, "total_duration": 845,
                                  "flights": [{"airline": "ANA"}]}],
                "other_flights": [{"price": 795, "total_duration": 1250,
                                   "flights": [{"airline": "X"}, {"airline": "Y"}]}]}
        got = flights.rows(data)
        self.assertEqual(len(got), 2)
        self.assertEqual({r["bucket"] for r in got}, {"best", "other"})

    def test_stops_are_legs_minus_one_not_leg_count(self):
        data = {"best_flights": [{"price": 1, "flights": [{"airline": "A"},
                                                          {"airline": "B"}]}]}
        self.assertEqual(flights.rows(data)[0]["stops"], 1)

    def test_a_nonstop_is_zero_stops(self):
        data = {"best_flights": [{"price": 1, "flights": [{"airline": "A"}]}]}
        self.assertEqual(flights.rows(data)[0]["stops"], 0)

    def test_duration_renders_in_hours_and_minutes(self):
        self.assertEqual(flights.hhmm(845), "14h05")
        self.assertEqual(flights.hhmm(None), "—")

    def test_empty_results_produce_no_rows_rather_than_a_blank_row(self):
        self.assertEqual(flights.rows({}), [])


class NothingBypassesTheClients(unittest.TestCase):
    """The architecture rule, enforced rather than remembered.

    Two scripts once called the same host independently, each with its own
    endpoint and its own backoff. Nothing was wrong with either, and nothing
    could tell you how much traffic the skill actually sent. These tests fail
    the moment a script reintroduces a direct provider call.
    """

    SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
    LIB = pathlib.Path(__file__).resolve().parent.parent / "lib"
    # Map links are inert strings in generated HTML, not API calls.
    ALLOWED = ("google.com/maps", "maps.google.com")

    def _sources(self, folder):
        return [(p, p.read_text(encoding="utf-8")) for p in folder.glob("*.py")]

    def test_no_script_hardcodes_a_provider_endpoint(self):
        import re
        offenders = []
        for p, src in self._sources(self.SCRIPTS):
            # capture the PATH too -- matching only the host meant a maps URL
            # looked identical to an API endpoint and the allowance never fired
            for m in re.finditer(r"https?://[^\s\"'\)]+", src):
                if not any(a in m.group(0) for a in self.ALLOWED):
                    offenders.append(f"{p.name}: {m.group(0)[:48]}")
        self.assertEqual(offenders, [],
                         "provider endpoints belong in lib/, behind a client that "
                         "checks and counts the call: " + "; ".join(offenders))

    def test_no_script_imports_the_raw_http_helpers(self):
        # get()/post() skip the quota layer entirely. Scripts compose clients.
        import re
        offenders = [p.name for p, src in self._sources(self.SCRIPTS)
                     if re.search(r"from lib\.common import [^\n]*\b(get|post)\b", src)]
        self.assertEqual(offenders, [],
                         "scripts must call a lib/ client, not get()/post(): "
                         + ", ".join(offenders))

    def test_every_lib_client_declares_a_provider_tag(self):
        # The tag is what the counter and the ceiling are keyed on; a client
        # without one is a client whose traffic lands nowhere.
        import re
        clients = [p for p, src in self._sources(self.LIB)
                   if re.search(r"^\s*quota\.(spend|check|record)\(", src, re.M)]
        self.assertTrue(clients, "expected at least one metered client in lib/")
        for p in clients:
            self.assertTrue(
                re.search(r"^PROVIDER = ", p.read_text(encoding="utf-8"), re.M),
                f"{p.name} meters calls but declares no PROVIDER")


class VenueFallback(unittest.TestCase):
    """When the second provider is reached for, and what it may claim.

    The fallback resolves the same places but cannot see business status or
    opening hours. Every case here guards the line between "verified" and
    "found" -- a distinction that decides whether a row can say a venue is open.
    """

    PLACE = {"displayName": {"text": "Thornbury Museum"},
             "formattedAddress": "1 High St", "businessStatus": "OPERATIONAL",
             "rating": 4.5, "userRatingCount": 100,
             "googleMapsUri": "https://maps.google.com/?cid=1"}
    ALT = {"title": "Thornbury Museum", "address": "1 High St", "rating": 4.4,
           "reviews": 98, "place_id": "abc",
           "gps_coordinates": {"latitude": 1.0, "longitude": 2.0}}

    def test_primary_success_never_spends_the_fallback(self):
        from lib import venues, gplaces, serpapi
        with mock.patch.object(gplaces, "available", lambda: True), \
             mock.patch.object(gplaces, "search_text", lambda *a, **k: self.PLACE), \
             mock.patch.object(serpapi, "maps") as m:
            r = venues.resolve("Thornbury Museum")
        m.assert_not_called()
        self.assertEqual(r["source"], venues.SOURCE_PLACES)
        self.assertFalse(r["partial"])

    def test_no_primary_key_falls_back(self):
        from lib import venues, gplaces, serpapi
        with mock.patch.object(gplaces, "available", lambda: False), \
             mock.patch.object(serpapi, "maps",
                               lambda *a, **k: (self.ALT, {})):
            r = venues.resolve("Thornbury Museum")
        self.assertEqual(r["source"], venues.SOURCE_SERPAPI)

    def test_primary_quota_exhaustion_falls_back_rather_than_failing(self):
        from lib import venues, gplaces, serpapi, quota
        def boom(*a, **k):
            raise quota.QuotaExceeded("spent")
        with mock.patch.object(gplaces, "available", lambda: True), \
             mock.patch.object(gplaces, "search_text", boom), \
             mock.patch.object(serpapi, "maps", lambda *a, **k: (self.ALT, {})):
            r = venues.resolve("Thornbury Museum")
        self.assertEqual(r["source"], venues.SOURCE_SERPAPI)

    def test_a_fallback_row_never_claims_a_status(self):
        # The critical one. Absent verification must not read as passed
        # verification -- a venue that closed permanently is exactly what the
        # status field exists to catch.
        from lib import venues, gplaces, serpapi
        with mock.patch.object(gplaces, "available", lambda: False), \
             mock.patch.object(serpapi, "maps", lambda *a, **k: (self.ALT, {})):
            r = venues.resolve("Thornbury Museum")
        self.assertIsNone(r["status"])
        self.assertTrue(r["partial"])
        self.assertIn("business status", r["missing"])

    def test_fallback_can_be_refused_outright(self):
        from lib import venues, gplaces, serpapi
        with mock.patch.object(gplaces, "available", lambda: False), \
             mock.patch.object(serpapi, "maps") as m:
            r = venues.resolve("Thornbury Museum", allow_fallback=False)
        m.assert_not_called()
        self.assertIsNone(r)

    def test_both_providers_failing_returns_none_not_a_stub(self):
        from lib import venues, gplaces, serpapi
        with mock.patch.object(gplaces, "available", lambda: True), \
             mock.patch.object(gplaces, "search_text", lambda *a, **k: None), \
             mock.patch.object(serpapi, "maps", lambda *a, **k: (None, {})):
            self.assertIsNone(venues.resolve("Nonexistent Place"))
