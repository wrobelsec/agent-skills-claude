"""Run the skill's test suite. Do this at the START of every run.

    python references/scripts/run_tests.py                       # offline, ~1s
    python references/scripts/run_tests.py --live                # + reach every API
    python references/scripts/run_tests.py --live \
        --country "<Country>" \
        --address "<a real street address in the LOCAL script>" \
        --romanized "<the same address romanized>" \
        --bbox <S> <W> <N> <E>                                   # + destination probe

Three tiers, and the third is the one that catches the dangerous failure.

  UNIT        Offline, no key, fabricated fixtures. Guards the transformations
              that have actually broken: currency formatting, machine-value
              translation, link injection, heading ownership.

  LIVE        Are the endpoints reachable TODAY? Every provider this skill uses
              has broken at least once mid-project -- an FX host started
              returning 403s, a daylight API began refusing fetchers, a flight
              API was decommissioned outright. None announced itself.

  DESTINATION Does a keyed provider give the right answer HERE? A key that
              authenticates is not a key that works for this country. One
              geocoder returns coordinates in the wrong country for local-script
              addresses -- HTTP 200, well-formed, wrong continent. The only way
              to catch that is to check an answer you already know, which is why
              the probe address must be REAL and must be one you can verify.
              Use a granular street address, not a landmark: landmarks resolve
              by name and hide exactly this failure.

Exit code is the number of failures, so this can gate a run.
Record any destination failure in references/api-compatibility.md with the date.
"""
import argparse, pathlib, sys, unittest

# Running the suite must leave nothing behind in the skill. Importing lib/ and
# tests/ writes __pycache__ directories into folders meant to hold source only,
# and deleting them by hand just means they return on the next run.
sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

UNIT = ["tests.test_money", "tests.test_humanize", "tests.test_render",
        "tests.test_report"]
LIVE = ["tests.test_live_apis"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="also hit the network and check every API is reachable")
    ap.add_argument("--country", help="expected country, for the destination probe")
    ap.add_argument("--address", help="a REAL street address in the local script")
    ap.add_argument("--romanized", help="the same address romanized, if applicable")
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("S", "W", "N", "E"),
                    help="bounds every geocoded answer must fall inside")
    ap.add_argument("-v", "--verbose", action="count", default=1)
    a = ap.parse_args()

    mods = list(UNIT)
    if a.live or a.address:
        mods += LIVE
        from tests import test_live_apis
        test_live_apis.set_destination(a.country, a.address, a.romanized, a.bbox)
        if a.address and not a.bbox:
            print("note: --address given without --bbox; the destination probe "
                  "cannot check the answer and will skip.\n")

    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromName(m) for m in mods)
    print(f"{'offline + live' if a.live or a.address else 'offline'} suite: "
          f"{suite.countTestCases()} tests\n")
    result = unittest.TextTestRunner(verbosity=a.verbose).run(suite)

    print()
    if result.skipped:
        print(f"{len(result.skipped)} skipped — usually a key that is not "
              f"configured, which is a quality reduction, not an error:")
        for t, why in result.skipped[:8]:
            print(f"    {t.id().split('.')[-1]}: {why}")
    n = len(result.failures) + len(result.errors)
    if n:
        print(f"\n{n} FAILURE(S). If a destination probe failed, record it in "
              f"references/api-compatibility.md with today's date and use a "
              f"different provider for this country.")
    else:
        print("all good — safe to start the run")
    return n


if __name__ == "__main__":
    sys.exit(main())
