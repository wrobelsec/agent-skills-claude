"""The one Open-Meteo client. Climate and daylight both come through here.

Two scripts were calling this host independently, each with its own copy of the
endpoint and its own idea of how to back off. That is the arrangement that lets
a provider's behaviour change and get fixed in one caller but not the other --
and it means no single place knows how much traffic the skill is actually
sending, which makes any budget report a partial description at best.

THE HORIZON TRAP, which has bitten this project once and is easy to hit again:
the FORECAST endpoint returns HTTP 400 for dates beyond roughly 16 days out. A
trip is usually planned months ahead, so for anything outside that horizon use
the ARCHIVE endpoint against the same calendar dates a year earlier. Solar times
for a fixed date move by under a minute year to year, so the answer is sound --
but it is DERIVED, not observed, and `derived` in the returned dict says so.
Label it that way in the deliverable.

Keyless, so nothing here spends a quota. It is still metered: the archive
returns 429 under rapid sequential calls, so every request is spaced by
lib.quota, and every request is counted so the run report can show the real
traffic rather than only the keyed part.
"""
import datetime

from .common import get
from . import quota

PROVIDER = "OPENMETEO"
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
FORECAST = "https://api.open-meteo.com/v1/forecast"

# Beyond this many days out the forecast endpoint 400s rather than degrading.
FORECAST_HORIZON_DAYS = 16


def within_forecast_horizon(date_str, today=None):
    d = datetime.date.fromisoformat(date_str)
    today = today or datetime.date.today()
    return 0 <= (d - today).days <= FORECAST_HORIZON_DAYS


def _call(url, params):
    quota.spend(PROVIDER, 1)
    q = "&".join(f"{k}={v}" for k, v in params.items())
    return get(f"{url}?{q}")


def archive(lat, lon, start, end, daily=None, hourly=None, timezone="auto"):
    """Observed history. The right endpoint for anything not in the next fortnight."""
    p = {"latitude": lat, "longitude": lon, "start_date": start,
         "end_date": end, "timezone": timezone}
    if daily:
        p["daily"] = ",".join(daily) if isinstance(daily, (list, tuple)) else daily
    if hourly:
        p["hourly"] = ",".join(hourly) if isinstance(hourly, (list, tuple)) else hourly
    return _call(ARCHIVE, p)


def forecast(lat, lon, start, end, daily=None, timezone="auto"):
    p = {"latitude": lat, "longitude": lon, "start_date": start,
         "end_date": end, "timezone": timezone}
    if daily:
        p["daily"] = ",".join(daily) if isinstance(daily, (list, tuple)) else daily
    return _call(FORECAST, p)


def solar(lat, lon, dates, timezone="auto"):
    """Sunrise and sunset for specific dates, choosing the endpoint by horizon.

    Returns {date: {"sunrise":…, "sunset":…, "derived": bool}}. `derived` is True
    where the answer came from the same date a year earlier because the date sits
    beyond the forecast horizon -- the caller must surface that, not bury it.
    """
    out = {}
    for d in dates:
        live = within_forecast_horizon(d)
        if live:
            j = forecast(lat, lon, d, d, daily=["sunrise", "sunset"],
                         timezone=timezone)
            key = d
        else:
            back = datetime.date.fromisoformat(d).replace(
                year=datetime.date.fromisoformat(d).year - 1).isoformat()
            j = archive(lat, lon, back, back, daily=["sunrise", "sunset"],
                        timezone=timezone)
            key = back
        day = (j.get("daily") or {})
        rise = (day.get("sunrise") or [None])[0]
        setn = (day.get("sunset") or [None])[0]
        out[d] = {"sunrise": rise, "sunset": setn, "derived": not live,
                  "source_date": key}
    return out


def grid_elevation(j):
    """What the model actually snapped to. A valley base and the ridge above it
    can sit in the same cell, and the difference is several degrees -- so the
    elevation the provider used is part of the answer, not a footnote."""
    return j.get("elevation")
