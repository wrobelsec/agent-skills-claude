"""Climate over the ACTUAL travel window, with the grid-snap check built in.

    python climate.py --places places.json --start <MM-DD> --end <MM-DD> \
                      --years <FIRST> <LAST> [--out climate.json]

Why not just quote monthly normals: published figures are binned to the
publisher's calendar month, and a trip rarely occupies one. On a live run,
monthly normals overstated the actual travel window by 2.4-3.2 C across three
cities -- an error no amount of better searching would have caught, because
nobody publishes the number the trip needs. This computes it from daily records.

Medians and tail frequencies, not means. "One year in five loses a day to
unusable weather" is something a traveller can plan against; an average
rainfall figure describes no actual year.

THE SNAP CHECK IS NOT OPTIONAL and is why it lives in this script rather than a
separate one. Reanalysis cells are ~25 km, so a mountain base can resolve onto a
coastal cell and come back several degrees too mild with nothing in the response
saying so. Supplying `elev_m` per place in the places file turns that from an
invisible error into a printed delta.

Window may cross a year boundary (--start 12-28 --end 01-04) and is handled.
Nothing here is destination-specific; all of it comes from the arguments.
"""
import argparse, os, statistics as st, sys, datetime as dt, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib.common import save, load_places
from lib import openmeteo


def md(s):
    m, d = s.split("-")
    return int(m), int(d)


def in_window(date, start, end):
    """True if date's (month, day) falls in [start, end], inclusive, wrapping
    across the new year when end < start."""
    x = (date.month, date.day)
    return start <= x <= end if start <= end else (x >= start or x <= end)


def pct(sorted_vals, p):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, int(p * len(sorted_vals)))
    return sorted_vals[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--places", required=True,
                    help="JSON of {name: [lat, lon]} or {name: {lat, lon, elev_m}}")
    ap.add_argument("--start", required=True, help="window start as MM-DD")
    ap.add_argument("--end", required=True, help="window end as MM-DD")
    ap.add_argument("--years", nargs=2, type=int, default=[2010, 2025],
                    metavar=("FIRST", "LAST"))
    ap.add_argument("--wet-mm", type=float, default=1.0,
                    help="daily precip counting as a wet day (default 1.0)")
    ap.add_argument("--washout-mm", type=float, default=10.0,
                    help="daily precip counting as a washout (default 10.0)")
    ap.add_argument("--out", default="climate.json")
    a = ap.parse_args()

    places = load_places(a.places)
    start, end = md(a.start), md(a.end)
    y0, y1 = a.years
    # fetch generously and filter locally; cheaper than one call per year
    fetch_start = f"{y0}-01-01" if start > end else f"{y0}-{a.start}"
    fetch_end = f"{y1 + (1 if start > end else 0)}-12-31" if start > end else f"{y1}-{a.end}"

    rows, snap = [], []
    for name, (lat, lon, elev) in places.items():
        d = openmeteo.archive(lat, lon, fetch_start, fetch_end,
                              daily=["temperature_2m_max", "temperature_2m_min",
                                     "precipitation_sum"])
        grid_elev = d.get("elevation")
        snap.append({
            "place": name, "asked": [lat, lon],
            "grid": [d.get("latitude"), d.get("longitude")],
            "grid_elev_m": grid_elev, "true_elev_m": elev,
            "delta_m": (grid_elev - elev) if (elev is not None and grid_elev is not None) else None,
        })

        dd = d["daily"]
        hi, lo, pr, by_year = [], [], [], {}
        for i, ds in enumerate(dd["time"]):
            date = dt.date.fromisoformat(ds)
            if not in_window(date, start, end):
                continue
            if dd["temperature_2m_max"][i] is None:
                continue
            # group by the year the window *starts* in, so a wrapped window
            # counts as one season rather than two
            season = date.year - (1 if start > end and (date.month, date.day) <= end else 0)
            # A wrapped window has to be fetched wider than the requested years
            # (Jan of y0 belongs to season y0-1), so trim back to what was asked
            # for. Without this, --years 2015 2024 silently reported 12 seasons
            # including two partial ones at the edges.
            if not (y0 <= season <= y1):
                continue
            hi.append(dd["temperature_2m_max"][i])
            lo.append(dd["temperature_2m_min"][i])
            p = dd["precipitation_sum"][i] or 0.0
            pr.append(p)
            by_year.setdefault(season, []).append(p)

        if not hi:
            print(f"  {name}: no data in window", file=sys.stderr)
            continue
        n = len(pr)
        shi, slo = sorted(hi), sorted(lo)
        rows.append({
            "place": name, "days": n, "seasons": len(by_year),
            "hi_median": round(st.median(hi), 1), "hi_mean": round(st.mean(hi), 1),
            "lo_median": round(st.median(lo), 1),
            "hi_p10": round(pct(shi, .10), 1), "hi_p90": round(pct(shi, .90), 1),
            "lo_min": round(min(lo), 1),
            "wet_pct": round(100 * sum(1 for p in pr if p >= a.wet_mm) / n),
            "washout_pct": round(100 * sum(1 for p in pr if p >= a.washout_mm) / n),
            "seasons_with_washout":
                f"{sum(1 for v in by_year.values() if any(p >= a.washout_mm for p in v))}"
                f"/{len(by_year)}",
        })

    print(f"\nWindow {a.start} to {a.end}, {y0}-{y1}  "
          f"(wet >= {a.wet_mm}mm, washout >= {a.washout_mm}mm)")
    print(f"{'Place':<24}{'days':>6}{'hi med':>8}{'lo med':>8}{'hi p10':>8}"
          f"{'hi p90':>8}{'lo min':>8}{'wet%':>6}{'wash%':>7}{'seasons':>9}")
    for r in rows:
        print(f"{r['place']:<24}{r['days']:>6}{r['hi_median']:>8}{r['lo_median']:>8}"
              f"{r['hi_p10']:>8}{r['hi_p90']:>8}{r['lo_min']:>8}"
              f"{r['wet_pct']:>6}{r['washout_pct']:>7}{r['seasons_with_washout']:>9}")

    print(f"\nGrid snap check  (a large delta means the reading describes "
          f"somewhere other than the place you named)")
    print(f"{'Place':<24}{'grid elev':>11}{'true elev':>11}{'delta':>8}")
    for s in snap:
        t = "?" if s["true_elev_m"] is None else f"{s['true_elev_m']:.0f}"
        dl = "n/a" if s["delta_m"] is None else f"{s['delta_m']:+.0f}"
        flag = ""
        if s["delta_m"] is not None and abs(s["delta_m"]) > 150:
            flag = "   *** resolved far from the named place ***"
        print(f"{s['place']:<24}{s['grid_elev_m']:>11}{t:>11}{dl:>8}{flag}")
    if any(s["true_elev_m"] is None for s in snap):
        print("\n  note: places without elev_m could not be snap-checked. Supply it.")

    save({"window": [a.start, a.end], "years": [y0, y1],
          "thresholds": {"wet_mm": a.wet_mm, "washout_mm": a.washout_mm},
          "rows": rows, "snap_check": snap}, a.out)


if __name__ == "__main__":
    main()
