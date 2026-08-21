"""Live lodging rates for real dates and a real party size.

    python hotels.py --where "<city or area>" --in 2027-03-14 --out-date 2027-03-17 \
                     --adults 4 [--currency JPY] [--children 2 --ages 7,9]
    python hotels.py --token <property_token> --in ... --out-date ...   # one property

This is the script that answers the question Google Places cannot. Places returns
metadata -- name, hours, rating, an ordinal price band -- and has no concept of a
date or an occupancy, so every lodging rate in a report used to read UNVERIFIED
while a booking engine either blocked the fetcher or rendered its calendar in
JavaScript. This queries Google Hotels through SerpApi instead, which takes the
dates and the guest count as parameters and returns what the room actually costs.

WHAT IT CANNOT TELL YOU, and this matters more than it sounds: the engine takes
guest COUNTS, not room counts or bed layout. It will price four adults; it will
not tell you whether those four get four beds or two. On a live trip that exact
distinction eliminated several properties and put the leading candidate in doubt,
so treat the rate as settled and the bedding as an open question -- the property's
own page or a phone call, every time.

Rates are per ROOM for the occupancy asked. The per-person figure a lodging
matrix wants is derived here rather than by hand, because dividing a stay total
by people and nights is exactly the arithmetic that has gone wrong before.

Requires SERPAPI_API_KEY. Degrades to a clean exit when absent -- a missing key
is a quality reduction, never an error. The key is never printed. Every response
is cached; a repeat query costs nothing against the monthly search budget.
"""
import argparse, datetime, re, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib import serpapi
from lib.common import save
from lib.money import sym as _sym


def nights_between(a, b):
    d = (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days
    if d < 1:
        raise SystemExit(f"check-out {b} is not after check-in {a}")
    return d


def rows(data, nights, people):
    """Flatten properties into the fields a lodging matrix actually needs."""
    out = []
    for p in data.get("properties", []):
        per_night = (p.get("rate_per_night") or {}).get("extracted_lowest")
        total = (p.get("total_rate") or {}).get("extracted_lowest")
        # Derive the missing side rather than leaving a hole. A property with a
        # nightly rate but no stay total is common, and the report needs both.
        if total is None and per_night is not None:
            total = per_night * nights
        if per_night is None and total is not None:
            per_night = round(total / nights)
        out.append({
            "name": p.get("name"),
            "token": p.get("property_token"),
            "link": p.get("link"),
            "coords": p.get("gps_coordinates"),
            "per_night_room": per_night,
            "total_stay_room": total,
            "per_person_night": (round(total / (people * nights))
                                 if total else None),
            "hotel_class": p.get("extracted_hotel_class"),
            "rating": p.get("overall_rating"),
            "reviews": p.get("reviews"),
            "amenities": p.get("amenities") or [],
            "check_in_time": p.get("check_in_time"),
            "check_out_time": p.get("check_out_time"),
            "deal": p.get("deal_description"),
            # availability is what the absence of a rate actually means here
            "priced": per_night is not None,
        })
    return out


def best_match(want, props):
    """Pick the returned property that is actually the one asked for.

    A name query returns a neighbourhood's worth of hotels, and the first result
    is frequently a different property that merely shares a word -- "Hotel",
    the city name, the district. Accepting it silently is how a report ends up
    quoting one hotel's rate under another hotel's name. So a match must share a
    DISTINCTIVE token: one that is not the city, not a generic hospitality word,
    and longer than three characters.
    """
    GENERIC = {"hotel", "hotels", "inn", "ryokan", "resort", "the", "and",
               "house", "guest", "guesthouse", "tokyo", "osaka", "hiroshima",
               "hakone", "grand", "royal", "plaza", "tower", "station"}
    toks = {w for w in re.findall(r"[a-z0-9]+", want.lower())
            if len(w) > 3 and w not in GENERIC}
    for p in props:
        n = (p.get("name") or "").lower()
        if want.lower() in n or n in want.lower():
            return p, "exact"
        if toks and any(tk in n for tk in toks):
            return p, "token"
    return None, "no-match"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--where", help="city, area, or property name to search")
    ap.add_argument("--each", help="file of property names, one per line — price "
                                   "each individually. Costs one search per name, "
                                   "so it reports the total before spending it")
    ap.add_argument("--token", help="a specific property_token from an earlier run")
    ap.add_argument("--in", dest="checkin", required=True, metavar="YYYY-MM-DD")
    ap.add_argument("--out-date", dest="checkout", required=True, metavar="YYYY-MM-DD")
    ap.add_argument("--adults", type=int, default=2)
    ap.add_argument("--children", type=int, default=0)
    ap.add_argument("--ages", help="comma-separated child ages, e.g. 7,9")
    ap.add_argument("--currency", default="USD", help="ISO code for the rates")
    ap.add_argument("--gl", default="us", help="country of the search")
    ap.add_argument("--hl", default="en", help="language of the search")
    ap.add_argument("--out", default="hotels.json")
    ap.add_argument("--refresh", action="store_true",
                    help="spend a search re-fetching something already cached")
    a = ap.parse_args()

    if not a.where and not a.token and not a.each:
        raise SystemExit("give --where, --token or --each")

    nights = nights_between(a.checkin, a.checkout)
    people = a.adults + a.children

    b = serpapi.budget()
    if b is None:
        print("SERPAPI_API_KEY not set — no live rates. "
              "Lodging will stay UNVERIFIED; everything else still runs.")
        return 0
    print(f"  budget: {b['left']} search(es) left this month ({b['plan']})")

    if a.each:
        return price_each(a, nights, people)

    params = {"check_in_date": a.checkin, "check_out_date": a.checkout,
              "adults": str(a.adults), "currency": a.currency,
              "gl": a.gl, "hl": a.hl}
    if a.children:
        params["children"] = str(a.children)
        if a.ages:
            params["children_ages"] = a.ages
    if a.token:
        params["property_token"] = a.token
    else:
        params["q"] = a.where

    data, meta = serpapi.search("google_hotels", refresh=a.refresh, **params)
    if data is None:
        print("no key — nothing fetched")
        return 0

    got = rows(data, nights, people)
    s = _sym(a.currency)
    src = f"cached, {meta['age']}" if meta["cached"] else "fetched now"
    print(f"  {len(got)} propert(ies) · {nights} night(s) · {people} guest(s) · {src}")
    print()
    print(f"{'property':<34} {'per night':>12} {'stay total':>13} "
          f"{'pp/night':>10}  rating")
    for r in sorted(got, key=lambda x: (x["per_person_night"] is None,
                                        x["per_person_night"] or 0)):
        if not r["priced"]:
            print(f"{(r['name'] or '')[:33]:<34} {'no rate — sold out or unlisted':>38}")
            continue
        print(f"{(r['name'] or '')[:33]:<34} {s}{r['per_night_room']:>11,} "
              f"{s}{r['total_stay_room']:>12,} {s}{r['per_person_night']:>9,}  "
              f"{r['rating'] or '—'} ({r['reviews'] or 0})")

    save({"query": {"where": a.where, "token": a.token, "checkin": a.checkin,
                    "checkout": a.checkout, "nights": nights, "adults": a.adults,
                    "children": a.children, "currency": a.currency},
          "cached": meta["cached"], "properties": got}, a.out)

    unpriced = [r["name"] for r in got if not r["priced"]]
    if unpriced:
        print(f"\n  {len(unpriced)} without a rate — that is a real finding: on these "
              f"dates they are sold out or not sold through Google.")
    print("\n  Rates are per ROOM at the occupancy asked. BED CONFIGURATION IS NOT "
          "IN THIS DATA — confirm four sleepers means four beds before booking.")
    return 0


def price_each(a, nights, people):
    """Price a named list of properties, one search each."""
    names = [l.strip() for l in open(a.each, encoding="utf-8")
             if l.strip() and not l.startswith("#")]
    from lib import quota
    quota.check("SERPAPI", need=len(names), ask=serpapi.budget)
    print(f"  pricing {len(names)} propert(ies) individually — up to "
          f"{len(names)} search(es), cached ones cost nothing")
    s = _sym(a.currency)
    print()
    print(f"{'asked for':<38} {'resolved':<30} {'per night':>11} {'pp/night':>10}")
    out = []
    for want in names:
        base = {"check_in_date": a.checkin, "check_out_date": a.checkout,
                "adults": str(a.adults), "currency": a.currency,
                "gl": a.gl, "hl": a.hl, "q": want}
        try:
            data, meta = serpapi.search("google_hotels", refresh=a.refresh, **base)
        except RuntimeError as e:
            print(f"{want[:37]:<38} {'SEARCH FAILED':<30} {str(e)[:28]}")
            continue
        got = rows(data or {}, nights, people)
        m, how = best_match(want, got)
        if not m:
            print(f"{want[:37]:<38} {'— no match on these dates':<30}")
            out.append({"asked": want, "status": "NO_MATCH_OR_SOLD_OUT"})
            continue
        if not m["priced"]:
            print(f"{want[:37]:<38} {(m['name'] or '')[:29]:<30} "
                  f"{'no rate — sold out':>22}")
            out.append({"asked": want, "name": m["name"], "status": "NO_RATE"})
            continue
        print(f"{want[:37]:<38} {(m['name'] or '')[:29]:<30} "
              f"{s}{m['per_night_room']:>10,} {s}{m['per_person_night']:>9,}"
              + ("" if how == "exact" else "   (token match — check)"))
        m["asked"] = want
        m["match"] = how
        out.append(m)
    save({"query": {"each": a.each, "checkin": a.checkin, "checkout": a.checkout,
                    "nights": nights, "adults": a.adults,
                    "currency": a.currency}, "properties": out}, a.out)
    print()
    print("  Rates are per ROOM at the occupancy asked. Bed configuration "
          "is not in this data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
