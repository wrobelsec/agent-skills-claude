"""Know what a key has left BEFORE spending it, and refuse to overspend.

Every keyed provider this skill uses is metered, and the meters are invisible
until they run out. The failure that follows is the expensive kind: a run gets
part-way through a lodging sweep, the quota ends mid-wave, and the remaining
agents return blanks that look exactly like "nothing found" rather than "you ran
out". A report then ships with real gaps that nobody knows are artificial.

So quota is checked at the START of a run, enforced on every call, and reported
in the same breath as the result.

TWO SOURCES OF TRUTH, in this order:

  PROVIDER   Some providers publish what is left. That number is authoritative
             and free to read -- SerpApi's /account does not itself consume a
             search. Always prefer it.

  LOCAL      Most do not. Google Places, Geoapify and the rest bill rather than
             meter, so there is nothing to ask. For those, this module counts
             what WE spent, per calendar month, on disk, against a ceiling the
             operator sets. A local count cannot see usage from another machine
             or another tool, so it is a floor on real usage, never a
             measurement -- it is labelled as such wherever it is printed.

CEILINGS ARE CONFIGURATION, NOT CONSTANTS. Any provider's limit is set with an
environment variable -- `<PROVIDER>_MONTHLY_LIMIT` -- because plans differ per
user and a number hardcoded here would be wrong for everyone but its author.
Absent a setting, an unmeasurable provider is UNLIMITED and says so, rather than
inventing a ceiling and blocking work that was actually permitted.
"""
import datetime, json, os, threading, time

from .common import out_dir

_LOCK = threading.Lock()

# Providers whose remaining quota can be READ from the provider itself.
# Anything not listed here is counted locally.
PROVIDER_METERED = {"SERPAPI"}


class QuotaExceeded(RuntimeError):
    """Raised instead of making a call that would exceed a configured ceiling."""


def _period():
    return datetime.date.today().strftime("%Y-%m")


def _store_path():
    return out_dir() / "quota.json"


def _load():
    p = _store_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(d):
    _store_path().write_text(json.dumps(d, indent=1), encoding="utf-8")


def limit(provider):
    """Configured ceiling for a provider this month, or None for unlimited."""
    raw = os.environ.get(f"{provider}_MONTHLY_LIMIT", "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def used(provider):
    """Calls WE have recorded this calendar month. A floor, not a measurement."""
    return _load().get(_period(), {}).get(provider, 0)


def record(provider, n=1):
    """Count calls actually made. Cheap, and the only thing that makes the
    local ceiling mean anything."""
    with _LOCK:
        d = _load()
        d.setdefault(_period(), {})
        d[_period()][provider] = d[_period()].get(provider, 0) + n
        _save(d)


def remaining(provider, ask=None):
    """What is left, and where the number came from.

    `ask` is an optional zero-cost callable returning the provider's own count,
    used for metered providers. Returns a dict that always has `source`, so a
    caller can print an authoritative figure differently from an estimate.
    """
    if provider in PROVIDER_METERED and ask:
        live = ask()
        if live and live.get("left") is not None:
            return {"left": live["left"], "used": live.get("used"),
                    "limit": None, "source": "provider", "plan": live.get("plan")}
    lim, u = limit(provider), used(provider)
    if lim is None:
        return {"left": None, "used": u, "limit": None, "source": "local-unlimited"}
    return {"left": max(0, lim - u), "used": u, "limit": lim, "source": "local"}


def check(provider, need=1, ask=None):
    """Refuse a call that would exceed the ceiling. Returns the quota state.

    Raising here rather than letting the provider reject is deliberate: a
    provider's own refusal arrives as an error mid-sweep and looks like a
    transport failure, while this names the real cause before anything is spent.
    """
    r = remaining(provider, ask=ask)
    if r["left"] is not None and r["left"] < need:
        raise QuotaExceeded(
            f"{provider}: {r['left']} left this month but {need} needed"
            + (f" (ceiling {r['limit']} from {provider}_MONTHLY_LIMIT)"
               if r["source"] == "local" else "")
            + ". Raise the limit, wait for the reset, or run without this provider "
              "— every track degrades rather than failing when a key is absent.")
    return r


def line(provider, r):
    """One printable line, honest about which kind of number it is."""
    if r["source"] == "provider":
        return (f"  {provider:<16} {r['left']} left this month"
                + (f" · {r['plan']}" if r.get("plan") else "")
                + "  [provider]")
    if r["source"] == "local":
        return (f"  {provider:<16} {r['left']} left of {r['limit']} "
                f"({r['used']} used)  [local count — this machine only]")
    return (f"  {provider:<16} no ceiling set · {r['used']} used here this month  "
            f"[set {provider}_MONTHLY_LIMIT to cap]")


# --------------------------------------------------------------- rate limits
#
# A keyless provider has no monthly quota to exhaust, but it will still refuse
# you. Open-Meteo returns 429 under rapid sequential calls; Nominatim asks for
# roughly one request a second and means it. Those are the SAME class of problem
# as a spent key -- work stops part-way and the gap looks like absent data -- so
# they belong here rather than in each caller.
#
# Spacing is per provider and configurable with <PROVIDER>_MIN_INTERVAL, in
# seconds. A provider with no configured interval is not throttled.
_LAST_CALL = {}
_RATE_LOCK = threading.Lock()

DEFAULT_INTERVAL = {
    "NOMINATIM": 1.1,      # their usage policy asks for ~1 req/sec
    "OPENMETEO": 0.25,     # observed 429s on bursts; this stays comfortably under
}


def min_interval(provider):
    raw = os.environ.get(f"{provider}_MIN_INTERVAL", "").strip()
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_INTERVAL.get(provider, 0.0)


def throttle(provider):
    """Block until enough time has passed since this provider's last call.

    Called by the provider clients, never by a script. Backing off AFTER a 429
    still costs the failed request and, in a fan-out, several more behind it;
    spacing the calls in the first place costs nothing but wall time.
    """
    gap = min_interval(provider)
    if not gap:
        return
    with _RATE_LOCK:
        last = _LAST_CALL.get(provider)
        now = time.monotonic()
        if last is not None:
            wait = gap - (now - last)
            if wait > 0:
                time.sleep(wait)
                now = time.monotonic()
        _LAST_CALL[provider] = now


def spend(provider, n=1, ask=None):
    """The one call every provider client makes: check, throttle, then count.

    Keeping check/throttle/record together is the point -- when they were the
    caller's job, one call site did all three, another did none, and the budget
    report silently described only part of the traffic.
    """
    state = check(provider, need=n, ask=ask)
    throttle(provider)
    record(provider, n)
    return state
