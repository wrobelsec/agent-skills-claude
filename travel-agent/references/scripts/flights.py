"""Live fares for real dates, through the same client as everything else.

    python flights.py --from IAD --to HND --depart 2027-03-14 [--return 2027-03-28]
    python flights.py --from IAD --to HND --depart 2027-03-14 --adults 4 --cabin business

This is the script that closed the longest-standing gap in this skill. Fares are
the most heavily defended data on the web -- every airline and OTA runs bot
protection over its pricing, which is exactly why a fetch-only agent spent four
separate passes on one trip and never returned a figure. Google Flights through
SerpApi takes the route and dates as parameters instead of hiding them behind a
rendered calendar.

WHAT IT DOES NOT DO, and both matter:
  * It prices ONE journey at a time. A multi-city or open-jaw itinerary is
    several searches, and on a small plan that is a real cost -- so the script
    tells you what a query will spend before it spends it.
  * A fare seen here is an advertised fare, not a held one. It moves between the
    search and the booking, and it is not a quote. Say so in the deliverable
    rather than presenting it as settled.

Requires SERPAPI_API_KEY. Degrades to a clean exit when absent. The key is never
printed, every response is cached, and a repeat query costs nothing.
"""
import argparse, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib import serpapi
from lib.common import save
from lib.money import sym as _sym

CABIN = {"economy": 1, "premium": 2, "business": 3, "first": 4}


def rows(data):
    """Flatten both itinerary buckets into comparable rows.

    Google splits results into `best_flights` and `other_flights`; taking only
    the first hides cheaper-but-slower options, which is precisely the trade a
    traveller wants to see.
    """
    out = []
    for bucket, items in (("best", data.get("best_flights") or []),
                          ("other", data.get("other_flights") or [])):
        for it in items:
            legs = it.get("flights") or []
            carriers = sorted({l.get("airline") for l in legs if l.get("airline")})
            out.append({
                "bucket": bucket,
                "price": it.get("price"),
                "total_minutes": it.get("total_duration"),
                "stops": max(0, len(legs) - 1),
                "carriers": carriers,
                "layovers": [f"{l.get('name')} {l.get('duration')}m"
                             for l in (it.get("layovers") or [])],
                "departure": legs[0].get("departure_airport", {}).get("time")
                             if legs else None,
                "arrival": legs[-1].get("arrival_airport", {}).get("time")
                           if legs else None,
                "aircraft": sorted({l.get("airplane") for l in legs if l.get("airplane")}),
                "legroom": sorted({l.get("legroom") for l in legs if l.get("legroom")}),
                "overnight": any(l.get("overnight") for l in legs),
                "often_delayed": any(l.get("often_delayed_by_over_30_min") for l in legs),
            })
    return out


def hhmm(mins):
    return f"{mins // 60}h{mins % 60:02d}" if mins else "—"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="origin", required=True, help="IATA code")
    ap.add_argument("--to", dest="dest", required=True, help="IATA code")
    ap.add_argument("--depart", required=True, metavar="YYYY-MM-DD")
    ap.add_argument("--return", dest="ret", metavar="YYYY-MM-DD",
                    help="omit for one-way")
    ap.add_argument("--adults", type=int, default=1)
    ap.add_argument("--children", type=int, default=0)
    ap.add_argument("--cabin", choices=list(CABIN), default="economy")
    ap.add_argument("--currency", default="USD")
    ap.add_argument("--out", default="flights.json")
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()

    b = serpapi.budget()
    if b is None:
        print("SERPAPI_API_KEY not set — no live fares. "
              "Mark every fare UNVERIFIED; the rest of the run is unaffected.")
        return 0
    print(f"  budget: {b['left']} search(es) left this month ({b['plan']})")

    params = {"departure_id": a.origin.upper(), "arrival_id": a.dest.upper(),
              "outbound_date": a.depart, "currency": a.currency,
              "adults": str(a.adults), "travel_class": str(CABIN[a.cabin]),
              "type": "1" if a.ret else "2", "hl": "en", "gl": "us"}
    if a.ret:
        params["return_date"] = a.ret
    if a.children:
        params["children"] = str(a.children)

    try:
        data, meta = serpapi.search("google_flights", refresh=a.refresh, **params)
    except RuntimeError as e:
        print(f"  {e}")
        print("  Mark the fare UNVERIFIED rather than substituting an estimate.")
        return 1

    got = rows(data)
    if not got:
        print(f"  no itineraries returned for {a.origin}->{a.dest} on {a.depart}. "
              f"That is a finding: check the route exists on this date.")
        return 0

    s = _sym(a.currency)
    src = f"cached, {meta['age']}" if meta["cached"] else "fetched now"
    trip = "return" if a.ret else "one-way"
    print(f"  {len(got)} itinerar(ies) · {trip} · {a.adults} adult(s) · "
          f"{a.cabin} · {src}")
    print()
    print(f"{'price':>10}  {'dur':>7} {'stops':>5}  {'carriers':<26} notes")
    for r in sorted(got, key=lambda x: (x["price"] is None, x["price"] or 0)):
        notes = []
        if r["overnight"]:
            notes.append("overnight")
        if r["often_delayed"]:
            notes.append("often delayed 30m+")
        if r["layovers"]:
            notes.append("via " + ", ".join(r["layovers"]))
        p = f"{s}{r['price']:,}" if r["price"] is not None else "—"
        print(f"{p:>10}  {hhmm(r['total_minutes']):>7} {r['stops']:>5}  "
              f"{', '.join(r['carriers'])[:25]:<26} {'; '.join(notes)[:60]}")

    save({"query": {"origin": a.origin.upper(), "dest": a.dest.upper(),
                    "depart": a.depart, "return": a.ret, "adults": a.adults,
                    "cabin": a.cabin, "currency": a.currency},
          "cached": meta["cached"], "itineraries": got}, a.out)

    print("\n  Advertised fares, not held quotes — they move between this search "
          "and the booking page. A multi-city or open-jaw trip is one search per "
          "leg; price the legs separately and say so.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
