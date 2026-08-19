"""Sunrise and sunset per location, for the trip window.

    python daylight.py --places places.json --dates <YYYY-MM-DD> [<YYYY-MM-DD> ...]
    python daylight.py --places places.json --start <YYYY-MM-DD> --end <YYYY-MM-DD> --every 4

Two traps this script exists to encode, both discovered the hard way:

1. sunrise-sunset.org now returns HTTP 403 to a plain fetcher. It was the
   recommended keyless daylight source; it no longer works. Daylight comes from
   Open-Meteo instead.

2. Open-Meteo's *forecast* endpoint returns HTTP 400 for dates beyond its ~16-day
   horizon, which any real trip planned in advance will be. The *archive*
   endpoint is therefore queried for the same calendar dates in an earlier year.
   Solar times for a fixed calendar date move well under a minute year to year,
   so this is accurate to the printed precision -- but it is DERIVED, not
   observed for the target year, and the deliverable must label it so.

Nothing here is destination-specific.
"""
import argparse, os, sys, time, datetime as dt, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib.common import get, save, load_places

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--places", required=True)
    ap.add_argument("--dates", nargs="+", help="explicit YYYY-MM-DD dates")
    ap.add_argument("--start", help="YYYY-MM-DD")
    ap.add_argument("--end", help="YYYY-MM-DD")
    ap.add_argument("--every", type=int, default=1,
                    help="with --start/--end, sample every N days")
    ap.add_argument("--proxy-year", type=int,
                    help="year actually queried (default: most recent complete year)")
    ap.add_argument("--out", default="daylight.json")
    a = ap.parse_args()

    if a.dates:
        want = [dt.date.fromisoformat(d) for d in a.dates]
    elif a.start and a.end:
        s, e = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
        want = [s + dt.timedelta(days=i)
                for i in range(0, (e - s).days + 1, max(1, a.every))]
    else:
        raise SystemExit("give --dates, or --start and --end")

    proxy_year = a.proxy_year or (dt.date.today().year - 1)
    derived = any(d.year != proxy_year for d in want)

    places = load_places(a.places)
    out = {}
    for name, (lat, lon, _) in places.items():
        # query a contiguous span in the proxy year covering every wanted date
        keys = sorted({d.replace(year=proxy_year) for d in want})
        d = get(f"{ARCHIVE}?latitude={lat}&longitude={lon}"
                f"&start_date={keys[0]}&end_date={keys[-1]}"
                f"&daily=sunrise,sunset&timezone=auto")["daily"]
        got = {t[:10]: (d["sunrise"][i][-5:], d["sunset"][i][-5:])
               for i, t in enumerate(d["time"])}
        out[name] = {}
        for orig in want:
            k = str(orig.replace(year=proxy_year))
            if k in got:
                out[name][str(orig)] = got[k]
        time.sleep(1)

    hdr = f"{'Place':<24}" + "".join(f"{str(d)[5:]:>16}" for d in want)
    print(hdr)
    for name, rows in out.items():
        line = f"{name:<24}"
        for d in want:
            sr, ss = rows.get(str(d), ("?", "?"))
            line += f"{sr + '-' + ss:>16}"
        print(line)

    if derived:
        print(f"\nDERIVED: solar times taken from {proxy_year} for the same calendar")
        print("dates (< 1 min drift per year). Label as derived in the deliverable,")
        print("not as an observation for the travel year.")

    save({"proxy_year": proxy_year, "derived": derived, "places": out}, a.out)


if __name__ == "__main__":
    main()
