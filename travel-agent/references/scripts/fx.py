"""Dated exchange rate, with provider fallback.

    python fx.py --from <HOME> --to <LOCAL>
    python fx.py --from <HOME> --to <LOCAL> --date <YYYY-MM-DD>

An undated FX rate is not a usable number in a budget -- it is worthless a month
later and nothing on the page says so. This always prints the rate, the date it
applies to, and which provider answered.

The fallback chain is not decoration: frankfurter.dev began returning
intermittent 403s mid-run on a live trip, and a single-provider script would
have failed the whole budget section. If every provider fails, this exits
non-zero rather than letting a plausible rate be invented.

Currency pair comes from the arguments; nothing here is trip-specific.
"""
import argparse, os, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib.common import get, save


def providers(base, quote, date):
    d = date or "latest"
    return [
        ("frankfurter.dev",
         f"https://api.frankfurter.dev/v1/{d}?base={base}&symbols={quote}",
         lambda j: (j["rates"][quote], j["date"])),
        ("frankfurter.app",
         f"https://api.frankfurter.app/{d}?from={base}&to={quote}",
         lambda j: (j["rates"][quote], j["date"])),
        ("open.er-api.com",
         f"https://open.er-api.com/v6/latest/{base}",
         lambda j: (j["rates"][quote], j.get("time_last_update_utc", "")[:16])),
        ("exchangerate.host",
         f"https://api.exchangerate.host/{d}?base={base}&symbols={quote}",
         lambda j: (j["rates"][quote], j.get("date", ""))),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="base", required=True,
                    help="the traveller's own currency, ISO code")
    ap.add_argument("--to", dest="quote", required=True,
                    help="the destination currency, ISO code")
    ap.add_argument("--date", help="YYYY-MM-DD; omit for latest")
    ap.add_argument("--out", default="fx.json")
    a = ap.parse_args()
    base, quote = a.base.upper(), a.quote.upper()

    for name, url, parse in providers(base, quote, a.date):
        try:
            rate, date = parse(get(url, tries=2))
            rate = float(rate)
            print(f"1 {base} = {rate} {quote}   as of {date}   [{name}]")
            print(f"reciprocal: 1000 {quote} = {1000 / rate:.2f} {base}")
            save({"base": base, "quote": quote, "rate": rate,
                  "date": date, "source": name}, a.out)
            return 0
        except Exception as e:
            print(f"  {name}: FAILED ({type(e).__name__})")

    print(f"\nALL FX PROVIDERS FAILED for {base}->{quote}.")
    print("Do not invent a rate. Mark every converted figure UNVERIFIED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
