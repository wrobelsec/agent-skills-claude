"""Quota accounting and enforcement. Offline; never touches a provider.

Each case is a way a metered key has actually caused trouble, or would: a sweep
that stops half-way and leaves unverified rows looking like failed ones, a
ceiling invented in code that is wrong for every user but its author, and a
local count quietly presented as if it were authoritative.
"""
import os, pathlib, tempfile, unittest
from unittest import mock

from lib import quota


class QuotaTest(unittest.TestCase):
    def setUp(self):
        # Isolate the counter file: tests must never read or write the real one.
        self.tmp = tempfile.TemporaryDirectory()
        self.p = mock.patch.object(quota, "out_dir",
                                   lambda: pathlib.Path(self.tmp.name))
        self.p.start()
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        os.environ.pop("TESTPROV_MONTHLY_LIMIT", None)

    def tearDown(self):
        self.p.stop()
        self.env.stop()
        self.tmp.cleanup()

    def test_no_ceiling_means_unlimited_not_zero(self):
        # Inventing a default ceiling would block work the plan actually allows.
        r = quota.remaining("TESTPROV")
        self.assertIsNone(r["left"])
        self.assertEqual(r["source"], "local-unlimited")

    def test_ceiling_comes_from_the_environment(self):
        os.environ["TESTPROV_MONTHLY_LIMIT"] = "10"
        self.assertEqual(quota.limit("TESTPROV"), 10)
        self.assertEqual(quota.remaining("TESTPROV")["left"], 10)

    def test_recording_decrements_what_is_left(self):
        os.environ["TESTPROV_MONTHLY_LIMIT"] = "10"
        quota.record("TESTPROV", 3)
        r = quota.remaining("TESTPROV")
        self.assertEqual((r["used"], r["left"]), (3, 7))

    def test_a_batch_larger_than_the_remainder_is_refused_up_front(self):
        # The whole point: refuse before spending, so a sweep never ends
        # half-done with the remainder indistinguishable from real failures.
        os.environ["TESTPROV_MONTHLY_LIMIT"] = "5"
        quota.record("TESTPROV", 3)
        with self.assertRaises(quota.QuotaExceeded):
            quota.check("TESTPROV", need=3)

    def test_a_batch_that_fits_is_allowed(self):
        os.environ["TESTPROV_MONTHLY_LIMIT"] = "5"
        quota.record("TESTPROV", 3)
        self.assertEqual(quota.check("TESTPROV", need=2)["left"], 2)

    def test_provider_reported_figure_wins_over_local_count(self):
        # A provider that publishes its own meter is authoritative; our count
        # cannot see usage from another machine.
        quota.record("SERPAPI", 99)
        r = quota.remaining("SERPAPI", ask=lambda: {"left": 250, "used": 0,
                                                    "plan": "Free Plan"})
        self.assertEqual(r["left"], 250)
        self.assertEqual(r["source"], "provider")

    def test_local_numbers_are_labelled_as_local(self):
        # A local count must never read like an authoritative one.
        os.environ["TESTPROV_MONTHLY_LIMIT"] = "10"
        self.assertIn("local count", quota.line("TESTPROV",
                                                quota.remaining("TESTPROV")))

    def test_provider_numbers_are_labelled_as_provider(self):
        r = quota.remaining("SERPAPI", ask=lambda: {"left": 7, "used": 243,
                                                    "plan": "Free Plan"})
        self.assertIn("[provider]", quota.line("SERPAPI", r))

    def test_exceeded_message_says_how_to_proceed(self):
        os.environ["TESTPROV_MONTHLY_LIMIT"] = "1"
        quota.record("TESTPROV", 1)
        with self.assertRaises(quota.QuotaExceeded) as cm:
            quota.check("TESTPROV", need=1)
        self.assertIn("TESTPROV_MONTHLY_LIMIT", str(cm.exception))
