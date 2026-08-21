"""The one Google Places client. Venue verification and geocoding both use it.

The endpoint and the field mask lived in a script, which meant the live test
suite kept its own copy of both -- two places to update, and nothing to notice
when only one of them was. The field mask especially: it is the difference
between a row that can state opening hours and one that cannot, and it should
not depend on which caller you came through.

Keyed and metered, so every call is checked and counted through lib.quota before
it is made. The key is read per call and never printed.
"""
from .common import key, post
from . import quota

PROVIDER = "GOOGLE_PLACES"
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

FIELDS = ",".join("places." + f for f in [
    "id", "displayName", "formattedAddress", "businessStatus",
    "regularOpeningHours.weekdayDescriptions", "rating", "userRatingCount",
    "primaryTypeDisplayName", "location", "websiteUri", "googleMapsUri",
    "priceLevel", "priceRange", "editorialSummary", "paymentOptions",
    "accessibilityOptions", "reservable", "goodForGroups",
    "servesVegetarianFood", "takeout", "dineIn", "reviews",
])


def available():
    """True when a key is configured. A missing key is a quality reduction --
    every caller degrades to UNVERIFIED rather than failing."""
    return bool(key("GOOGLE_PLACES_API_KEY"))


def reserve(n):
    """Check a whole batch before spending any of it.

    A sweep that stops half-way leaves unverified rows indistinguishable from
    venues that genuinely failed to resolve, and that difference decides whether
    a row ships.
    """
    return quota.check(PROVIDER, need=n)


def search_text(query, lang="en", max_results=1, fields=None):
    """One text search. Returns the first place dict, or None for no match."""
    k = key("GOOGLE_PLACES_API_KEY")
    if not k:
        return None
    quota.spend(PROVIDER, 1)
    j = post(ENDPOINT,
             {"textQuery": query, "languageCode": lang,
              "maxResultCount": max_results},
             headers={"X-Goog-Api-Key": k, "X-Goog-FieldMask": fields or FIELDS})
    return (j.get("places") or [None])[0]
