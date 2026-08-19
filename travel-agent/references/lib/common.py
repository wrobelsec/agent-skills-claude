"""Shared HTTP, credential and location layer for the trip-research scripts.

Why this exists: each of these endpoints has failed in a *different* way in
practice -- 429 from the Open-Meteo archive under rapid calls, 403 from
sunrise-sunset.org and intermittently from Frankfurter, 400 from the Open-Meteo
forecast API for dates past its ~16-day horizon. Retry-with-backoff plus an
explicit provider fallback list is the only thing that survives all four.

CONVENTIONS THESE SCRIPTS FOLLOW (see SKILL.md "Script conventions"):

  * No absolute path is ever hardcoded. Paths are relative by default and
    overridable by environment variable; "~" is expanded at runtime, never
    written into source.
  * No key value is ever hardcoded, and no key value is ever printed. Report
    "set" / "working" / "invalid" -- never the string itself.
  * No destination, coordinate, currency or date window appears in source.
    All of it is passed at run time, so the same script serves any trip.

    TRIP_OUT         directory for JSON output          (default: cwd)
    CLAUDE_SETTINGS  settings file holding the API keys (default:
                     ~/.claude/settings.json, expanded at runtime)
"""
import json, os, time, urllib.request, urllib.parse, urllib.error, pathlib

UA = "Mozilla/5.0 (compatible; trip-research/1.0)"


# --------------------------------------------------------------- paths, keys
def settings_path():
    return pathlib.Path(
        os.environ.get("CLAUDE_SETTINGS")
        or os.path.join("~", ".claude", "settings.json")
    ).expanduser()


def out_dir():
    d = pathlib.Path(os.environ.get("TRIP_OUT", "."))
    d.mkdir(parents=True, exist_ok=True)
    return d


def key(name):
    """Fetch an API key by env-var name. Returns '' when unset -- callers must
    treat that as 'degrade to keyless', never as an error. Never print the
    return value of this function."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        env = json.loads(settings_path().read_text(encoding="utf-8")).get("env", {})
        return env.get(name, "") or ""
    except Exception:
        return ""


# ---------------------------------------------------------------------- http
def get(url, tries=6, timeout=60, headers=None):
    """GET JSON with exponential backoff on rate limits and transport errors.

    Raises immediately on a 4xx that is not a rate limit -- a 400 means the
    request is wrong, and retrying it only burns the budget.
    """
    delay, err = 5, None
    h = {"User-Agent": UA, **(headers or {})}
    for _ in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h),
                                        timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (429, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 120)
                continue
            raise
        except Exception as e:
            err = e
            time.sleep(delay)
            delay = min(delay * 2, 120)
    raise err


def post(url, payload, headers=None, timeout=60):
    h = {"User-Agent": UA, "Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def save(obj, name):
    """Write JSON into TRIP_OUT (default cwd). `name` is a bare filename."""
    p = out_dir() / name
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  -> wrote {p}")
    return p


# ----------------------------------------------------------------- locations
def load_places(path):
    """Read the run's locations from a JSON file. Two accepted shapes:

        {"<place name>": [<lat>, <lon>]}
        {"<place name>": {"lat": <lat>, "lon": <lon>, "elev_m": <metres>}}

    `elev_m` is the published elevation of the real place. Supply it wherever
    you can: it is what lets the climate script prove a mountain base did not
    silently resolve onto a coastal grid cell, which is the failure mode that
    makes a highland reading several degrees too mild with nothing in the
    response to signal it.

    Returns {name: (lat, lon, elev_m_or_None)}.
    """
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    out = {}
    for name, v in raw.items():
        if isinstance(v, dict):
            out[name] = (float(v["lat"]), float(v["lon"]),
                         float(v["elev_m"]) if v.get("elev_m") is not None else None)
        else:
            out[name] = (float(v[0]), float(v[1]), None)
    if not out:
        raise SystemExit(f"{path}: no locations found")
    return out


# Map-link builders live in lib/render.py -- one definition, beside the
# rendering rules that depend on them.
