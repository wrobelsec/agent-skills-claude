"""Verify venues against Google Places (New) -- existence, status, hours,
address, and a ready-made Google Maps link.

    python places.py venues.txt [--out places.json] [--lang en]

venues.txt: one venue per line, "Name | City". The city is not just a search hint
-- it is ASSERTED against the resolved address, and a mismatch is reported.

    python places.py venues.txt --expect "<region or city>"

Why that matters: on a live run, thirteen restaurants from one city shipped
inside another city's section of a report. A combined food track had returned
one table covering three cities and the split at synthesis went by row order
rather than by where each venue actually is. Nothing caught it, because every
row was individually true -- only its filing was wrong.

Worse, the mis-filing then poisoned the lookup: appending the WRONG city to a
query drags the geocoder toward that city, so a wrong section produces a wrong
pin. The city hint has to be the venue's OWN city, never the section it is being
filed under. Passing --expect makes that an assertion for the whole batch.

This is the step that catches fabricated and stale rows, and it has earned its
place twice on real runs: one venue resolved CLOSED_PERMANENTLY at the address a
research agent had confidently recommended, and another name would not resolve at
all because it did not exist. A name that will not resolve is the tell.

It also emits the Maps URL per venue, using `place_id` rather than the name.
That matters: a name-only Maps query resolves to whichever branch Google prefers,
which has already put the wrong branch of a four-branch restaurant and a cafe in
the wrong neighbourhood into a published report.

Requires GOOGLE_PLACES_API_KEY. Degrades to a clean exit when absent -- a
missing key is a quality reduction, never an error. The key is never printed.
"""
import argparse, sys, pathlib, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib.common import key, post, save
from lib.money import sym as _sym
from lib import humanize as H
from lib.render import maps_url

API = "https://places.googleapis.com/v1/places:searchText"

# This API answers far more than "does it exist". Every field below has been
# confirmed to return live, and several replace research that was previously
# left UNVERIFIED:
#
#   priceRange           real amounts in the local currency, not a $$ enum
#   paymentOptions       acceptsCashOnly — independently confirms cash-only venues
#   accessibilityOptions wheelchair entrance/restroom/seating, which is the data
#                        the per-traveller mobility record actually needs
#   googleMapsUri        Google's own canonical link — prefer it over a
#                        hand-constructed search URL
#   editorialSummary     Google's one-line description
#   reviews              up to 5 full review texts
FIELDS = ",".join("places." + f for f in [
    "id", "displayName", "formattedAddress", "businessStatus",
    "regularOpeningHours.weekdayDescriptions", "rating", "userRatingCount",
    "primaryTypeDisplayName", "location", "websiteUri", "googleMapsUri",
    "priceLevel", "priceRange", "editorialSummary", "paymentOptions",
    "accessibilityOptions", "reservable", "goodForGroups",
    "servesVegetarianFood", "takeout", "dineIn", "reviews",
])

# priceLevel is ORDINAL AND LOCALE-RELATIVE. It does not convert to money, and
# Google documents no mapping to currency. Measured over one run's verified
# venues, in local-currency units:
#
#   INEXPENSIVE     1 - 2,000          (and it OVERLAPS moderate)
#   MODERATE        1,000 - 8,000      (an 8x spread across 22 venues)
#   VERY_EXPENSIVE  10,000
#
# Two conclusions the labels encode. The bands are not disjoint -- one
# INEXPENSIVE venue sat in the same band as sixteen MODERATE ones -- and they
# are not comparable across countries: in a second, cheaper market the same run
# saw EXPENSIVE come back below the top of MODERATE in the first.
#
# So the fallback renders a RELATIVE label, never a currency symbol. Writing "$$"
# invites a reader to treat it as a price, which is the one thing it is not.
def price_text(p):
    """The real currency range, symbolized, or '' when the API has none.

    `priceRange.startPrice` is inclusive and `endPrice` is EXCLUSIVE, so a
    reported 1,000-2,000 means "at least 1,000, under 2,000".

    This deliberately does NOT fall back to the price enum. The enum is ordinal
    and locale-relative; rendering it here would put a non-price in a column
    headed by money. It is returned separately as `price_band`.
    """
    pr = p.get("priceRange") or {}
    lo, hi = pr.get("startPrice") or {}, pr.get("endPrice") or {}
    if not (lo.get("units") or hi.get("units")):
        return ""
    cur = lo.get("currencyCode") or hi.get("currencyCode") or ""
    sym = _sym(cur)
    a, b = lo.get("units"), hi.get("units")
    if a and b:
        return f"{sym}{int(a):,}–{int(b):,}"
    return f"{sym}{int(a or b):,}+"


def access_text(p):
    """Compact accessibility summary, or '' when the API knows nothing."""
    a = p.get("accessibilityOptions") or {}
    if not a:
        return ""
    # Field names are machine tokens; the output here is read by a person
    # deciding whether someone in the party can get in.
    yes = [lbl for fld, lbl in [
        ("wheelchairAccessibleEntrance", "entrance"),
        ("wheelchairAccessibleRestroom", "restroom"),
        ("wheelchairAccessibleSeating", "seating"),
        ("wheelchairAccessibleParking", "parking")] if a.get(fld)]
    no = [lbl for fld, lbl in [
        ("wheelchairAccessibleEntrance", "entrance"),
        ("wheelchairAccessibleRestroom", "restroom")] if a.get(fld) is False]
    out = ("step-free: " + ", ".join(yes)) if yes else ""
    if no:
        out += ("; no " + ", ".join(no)) if out else "no " + ", ".join(no)
    return out


def human(v, unknown="not stated"):
    """Render a value for a person. Never let None/True/False reach a reader.

    Python's None printed straight into a document reads as a bug to anyone who
    sees it, and 'True' is not an answer to a yes/no question a human asked."""
    if v is None or v == "":
        return unknown
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default="venues.txt")
    ap.add_argument("--out", default="places.json")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--expect", help="region/city every result must resolve inside; "
                                     "mismatches are reported and counted")
    a = ap.parse_args()

    k = key("GOOGLE_PLACES_API_KEY")
    if not k:
        print("GOOGLE_PLACES_API_KEY not set — cannot verify.")
        print("Mark every venue row UNVERIFIED and say so in the deliverable.")
        return 0

    queries = [l.strip() for l in open(a.file, encoding="utf-8")
               if l.strip() and not l.startswith("#")]
    out, misfiled = [], []
    for q in queries:
        try:
            j = post(API, {"textQuery": q, "languageCode": a.lang,
                           "maxResultCount": 1},
                     headers={"X-Goog-Api-Key": k, "X-Goog-FieldMask": FIELDS})
            p = (j.get("places") or [None])[0]
        except Exception as e:
            out.append({"query": q, "status": f"LOOKUP_FAILED {type(e).__name__}"})
            print(f"{q[:38]:<40} LOOKUP_FAILED")
            continue

        if not p:
            out.append({"query": q, "status": "NO_MATCH"})
            print(f"{q[:38]:<40} *** NO MATCH — treat as fabricated until proven ***")
            continue

        name = p.get("displayName", {}).get("text", "")
        loc = p.get("location", {})
        pay = p.get("paymentOptions") or {}
        rec = {
            "query": q, "name": name, "place_id": p.get("id", ""),
            "status": p.get("businessStatus", "?"),
            "address": p.get("formattedAddress", ""),
            "rating": p.get("rating"), "reviews": p.get("userRatingCount"),
            "type": p.get("primaryTypeDisplayName", {}).get("text", ""),
            "hours": p.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
            "site": p.get("websiteUri", ""),
            "price": price_text(p), "price_level": p.get("priceLevel", ""),
            "price_band": H.BAND.get(p.get("priceLevel", ""), ("", ""))[0],
            "summary": (p.get("editorialSummary") or {}).get("text", ""),
            "cash_only": pay.get("acceptsCashOnly"),
            "cards": pay.get("acceptsCreditCards"),
            "access": access_text(p),
            "reservable": p.get("reservable"), "groups": p.get("goodForGroups"),
            "veg": p.get("servesVegetarianFood"),
            "lat": loc.get("latitude"), "lon": loc.get("longitude"),
            # Google's own canonical link beats a constructed search URL
            "maps_url": p.get("googleMapsUri") or maps_url(
                name=name, place_id=p.get("id"),
                lat=loc.get("latitude"), lon=loc.get("longitude")),
            "review_texts": [r.get("text", {}).get("text", "")[:400]
                             for r in (p.get("reviews") or [])[:3]],
        }
        # Placement check. The city on the line, and --expect, are assertions:
        # a venue that resolves outside the region it was filed under is
        # mis-filed, and mis-filing is invisible in review because every row is
        # individually true.
        addr = rec["address"]
        hint = q.split("|", 1)[1].strip() if "|" in q else ""
        region = a.expect or ""
        mismatch = ""
        if region:
            # --expect is the explicit assertion and it is authoritative. When it
            # is satisfied, do NOT then second-guess it with the weaker city
            # hint: that produced false positives on EXONYMS, flagging venues
            # whose address carries the local-language city name against a hint
            # written in English. Many major cities are spelled nothing like
            # their English name in their own language, and no amount of string
            # matching bridges that.
            if region.lower() not in addr.lower():
                mismatch = f"  *** resolves OUTSIDE {region}: {addr[:44]} ***"
                rec["region_mismatch"] = region
                misfiled.append((q, addr))
        elif hint and hint.isascii() and hint.lower() not in addr.lower():
            # Advisory only, for the same exonym reason -- printed so a human
            # looks, but not counted as a failure. Pass --expect for an assertion.
            mismatch = f"  ?  check placement — hint '{hint}' not in {addr[:36]}"
            rec["placement_note"] = hint

        out.append(rec)
        flag = "" if rec["status"] == "OPERATIONAL" else f"  *** {rec['status']} ***"
        cash = " CASH-ONLY" if rec["cash_only"] else ""
        print(f"{q[:34]:<36} {name[:28]:<30} {str(rec['rating'] or ''):<5}"
              f"{str(rec['reviews'] or ''):<7}{rec['price'][:14]:<15}{cash}{flag}{mismatch}")
        time.sleep(0.25)

    save(out, a.out)
    bad = [r for r in out if r.get("status") != "OPERATIONAL"]
    print(f"\n{len(out)} looked up, {len(bad)} need attention")
    if misfiled:
        print(f"\n*** {len(misfiled)} venue(s) resolved outside the region they were "
              f"filed under ***")
        for q, addr in misfiled:
            print(f"    {q}  ->  {addr[:60]}")
        print("  Move them to the right location section BEFORE re-querying: a\n"
              "  wrong city hint drags the geocoder, so a mis-filed venue also\n"
              "  gets a mis-placed pin.")
    print("\nEvery row's `maps_url` is ready to paste — the place NAME is the link.")
    return len(misfiled)


if __name__ == "__main__":
    sys.exit(main())
