"""One SerpApi client, shared by every script that needs live prices.

Google's own Places API returns place metadata and nothing date-aware -- no
rate, no availability, no occupancy. Anything that has to answer "what does this
cost on these dates for this many people" goes through here instead.

THE BUDGET IS THE DESIGN CONSTRAINT. The free plan allows 250 searches a MONTH,
shared across every engine and every run. A lodging sweep over six properties and
a flight matrix over four routes is 10 searches; doing that carelessly twice a
week exhausts the month. So:

  * every response is cached on disk, keyed by the exact query
  * a repeat of an identical query costs nothing and says so
  * `--refresh` is the only way to spend a search on something already held
  * `budget()` reports what is left, and does not itself consume a search

Cached prices go stale, which matters more for fares than for anything else.
`age_note()` returns how old a cached answer is so a caller can print it beside
the figure rather than passing off last week's fare as today's.

The key is read through common.key() and never printed, logged, or written into
a cache filename -- cache keys hash the parameters with the key removed.
"""
import hashlib, json, os, pathlib, time, urllib.parse

from .common import key, get
from . import quota

PROVIDER = "SERPAPI"

ENDPOINT = "https://serpapi.com/search"
ACCOUNT = "https://serpapi.com/account"


def _cache_dir():
    """A STABLE home, deliberately not the output directory.

    This first followed `out_dir()`, which defaults to the working directory --
    so the cache landed wherever the script happened to be run from. Two
    consequences, both bad: it wrote scratch files into the skill's own folder,
    and running the same sweep from a different directory missed the cache
    entirely and silently re-bought every search. A cache that only works when
    you stand in the right place is worse than none, because it looks like it is
    saving you money.

    `TRIP_CACHE` overrides; otherwise a per-user cache directory.
    """
    env = os.environ.get("TRIP_CACHE")
    if env:
        d = pathlib.Path(env).expanduser()
    else:
        base = os.environ.get("XDG_CACHE_HOME") or os.environ.get("LOCALAPPDATA")
        d = (pathlib.Path(base).expanduser() if base
             else pathlib.Path.home() / ".cache") / "travel-agent"
    d = d / "serpapi-cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cache_key(params):
    """Hash the query, with the credential removed before hashing."""
    clean = {k: v for k, v in sorted(params.items()) if k != "api_key"}
    blob = json.dumps(clean, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def age_note(entry):
    """How old a cached answer is, in words a reader can act on."""
    secs = time.time() - entry.get("fetched_at", 0)
    if secs < 3600:
        return "just now"
    if secs < 86400:
        return f"{int(secs // 3600)}h old"
    return f"{int(secs // 86400)}d old"


def budget():
    """Searches left this month. Does not consume one.

    Returns None when the key is absent -- a missing key is a quality reduction,
    never an error, and every caller degrades rather than failing.
    """
    k = key("SERPAPI_API_KEY")
    if not k:
        return None
    try:
        j = get(ACCOUNT + "?api_key=" + urllib.parse.quote(k))
        return {"left": j.get("total_searches_left"),
                "used": j.get("this_month_usage"),
                "plan": j.get("plan_name")}
    except Exception:
        return None


def search(engine, refresh=False, **params):
    """One SerpApi search, cached. Returns (data, meta).

    meta carries `cached`, `age` and `spent` so a caller can tell the reader
    whether a figure was fetched now or recalled, and so a script can report
    what a sweep actually cost.

    Raises RuntimeError with SerpApi's own message on an API-level error --
    those arrive as HTTP 200 with an "error" field, so they must be checked
    explicitly or a failed search looks like an empty result.
    """
    k = key("SERPAPI_API_KEY")
    if not k:
        return None, {"cached": False, "spent": 0, "reason": "no SERPAPI_API_KEY"}

    q = dict(params)
    q["engine"] = engine
    ck = _cache_key(q)
    path = _cache_dir() / f"{engine}-{ck}.json"

    if path.exists() and not refresh:
        entry = json.loads(path.read_text(encoding="utf-8"))
        return entry["data"], {"cached": True, "spent": 0,
                               "age": age_note(entry)}

    # Check BEFORE spending. A cache hit never reaches here, so a re-run of an
    # identical sweep costs no quota and is never blocked by the ceiling.
    quota.check(PROVIDER, need=1, ask=budget)

    q["api_key"] = k
    data = get(ENDPOINT + "?" + urllib.parse.urlencode(q))
    if data.get("error"):
        raise RuntimeError(f"SerpApi {engine}: {data['error']}")

    quota.record(PROVIDER, 1)
    path.write_text(json.dumps({"fetched_at": time.time(), "engine": engine,
                                "data": data}, ensure_ascii=False),
                    encoding="utf-8")
    return data, {"cached": False, "spent": 1, "age": "just now"}


def maps(query, hl="en", refresh=False):
    """Google Maps place lookup — the fallback path for venue resolution.

    Returns the single place when the query resolves to one, otherwise the first
    local result, otherwise None. Deliberately thin: the decision about WHEN to
    reach for this belongs in lib/venues.py, not here.
    """
    data, meta = search("google_maps", refresh=refresh, q=query,
                        type="search", hl=hl)
    if data is None:
        return None, meta
    r = data.get("place_results")
    if not r:
        locals_ = data.get("local_results") or []
        r = locals_[0] if locals_ else None
    return r, meta
