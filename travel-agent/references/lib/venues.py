"""Resolve a venue to a verified place, with a fallback when the first fails.

Two providers can answer "where is this and is it real", and they are not
equivalent. This module owns the POLICY -- which to try, in what order, and what
to admit afterwards -- while each provider client stays a thin transport.

  GOOGLE PLACES is primary and richer. It alone returns business status, opening
  hours, accessibility, payment options and a price band. Business status is the
  one that has actually saved a report: a venue an agent confidently recommended
  came back CLOSED_PERMANENTLY, and nothing else in the pipeline would have
  caught it.

  SERPAPI google_maps is the fallback. It resolves the same places and returns
  name, address, coordinates, rating, review count, website and phone -- but NOT
  status, hours, accessibility or payment. A row resolved this way is a row that
  cannot state whether the place is open today.

That asymmetry is the whole reason `source` and `partial` are returned with every
result. A fallback row is not a worse-looking row; it is a row with a different
warranty, and the deliverable has to say so rather than letting a pin imply a
verification that never happened.

WHY NOT USE THE FALLBACK EVERYWHERE: it is metered far more tightly. Places bills
per call against a large allowance; SerpApi's free plan is 250 searches a MONTH
across flights, hotels and maps together. Spending that budget on venue lookups
that Places would have answered is how a lodging sweep later finds nothing left.
"""
from . import gplaces, serpapi, quota

SOURCE_PLACES = "google-places"
SOURCE_SERPAPI = "serpapi-maps"

# Fields only the primary provider can supply. Named here so a caller can say
# precisely what a fallback row is missing instead of guessing.
PRIMARY_ONLY = ("business status", "opening hours", "accessibility",
                "payment options", "price band")


def _from_places(p):
    return {
        "source": SOURCE_PLACES, "partial": False,
        "name": (p.get("displayName") or {}).get("text"),
        "address": p.get("formattedAddress"),
        "status": p.get("businessStatus"),
        "rating": p.get("rating"), "reviews": p.get("userRatingCount"),
        "coords": p.get("location"),
        "maps_url": p.get("googleMapsUri"),
        "website": p.get("websiteUri"),
        "hours": (p.get("regularOpeningHours") or {}).get("weekdayDescriptions"),
        "raw": p,
    }


def _from_serpapi(r):
    gps = r.get("gps_coordinates") or {}
    return {
        "source": SOURCE_SERPAPI, "partial": True,
        "missing": list(PRIMARY_ONLY),
        "name": r.get("title"),
        "address": r.get("address"),
        # No status field exists here. Leaving it None rather than assuming
        # "open" is the point: an absent check must never read as a passed one.
        "status": None,
        "rating": r.get("rating"), "reviews": r.get("reviews"),
        "coords": {"latitude": gps.get("latitude"),
                   "longitude": gps.get("longitude")},
        "maps_url": (f"https://www.google.com/maps/search/?api=1&query_place_id="
                     f"{r['place_id']}&query=" + (r.get("title") or "").replace(" ", "+")
                     if r.get("place_id") else None),
        "website": r.get("website"),
        "hours": None,
        "raw": r,
    }


def resolve(query, lang="en", allow_fallback=True, on_note=None):
    """Try the primary, fall back only when it genuinely cannot answer.

    Falls back when: no Places key is configured, the Places quota is spent, or
    Places returns no match. It does NOT fall back on a successful lookup that
    simply lacks a field -- a second provider would not know that field either,
    and the call would be spent for nothing.
    """
    note = on_note or (lambda m: None)

    if gplaces.available():
        try:
            p = gplaces.search_text(query, lang=lang)
            if p:
                return _from_places(p)
            note(f'"{query}": no match in Places')
        except quota.QuotaExceeded as e:
            note(f"Places quota spent ({e}) — falling back")
        except Exception as e:
            note(f'"{query}": Places failed ({type(e).__name__}) — falling back')
    else:
        note("no GOOGLE_PLACES_API_KEY — falling back")

    if not allow_fallback:
        return None

    r, _meta = serpapi.maps(query, hl=lang)
    if not r:
        return None
    out = _from_serpapi(r)
    note(f'"{query}": resolved via fallback — no {", ".join(PRIMARY_ONLY[:2])}')
    return out
