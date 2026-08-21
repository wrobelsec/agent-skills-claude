"""The one FX client: a provider chain, tried in order, counted as it goes.

The chain is not decoration. One host began returning intermittent 403s partway
through a run, and a single-provider design would have failed the whole currency
layer at that moment -- every converted figure in the report becomes UNVERIFIED
because one server had a bad afternoon.

It lives in lib/ rather than in the script because the script is not the only
caller: the live test suite checks the same hosts, and when it kept its own copy
of the list the two could disagree about which providers this skill even uses.
One list, one order, one place to add the next fallback.

Every attempt is counted through lib.quota, including the ones that fail. A
provider that refuses you still costs a request, and a budget report that counts
only successes understates real traffic exactly when traffic is going wrong.
"""
from .common import get
from . import quota

PROVIDER = "FX"


def providers(base, quote, date=None):
    d = date or "latest"
    return [
        ("frankfurter.dev",
         f"https://api.frankfurter.dev/v1/{d}?base={base}&symbols={quote}",
         lambda j: (j["rates"][quote], j["date"])),
        ("frankfurter.app",
         f"https://api.frankfurter.app/{d}?from={base}&to={quote}",
         lambda j: (j["rates"][quote], j["date"])),
        ("open.er-api.com",
         f"https://open.er-api.com/v6/latest/{base}",
         lambda j: (j["rates"][quote], j.get("time_last_update_utc", "")[:16])),
        ("exchangerate.host",
         f"https://api.exchangerate.host/{d}?base={base}&symbols={quote}",
         lambda j: (j["rates"][quote], j.get("date", ""))),
    ]


def fetch(base, quote, date=None, on_fail=None):
    """First provider that answers wins. Returns a dict, or None if all refused.

    Never invents a rate. A currency layer that guesses is worse than one that
    admits it does not know, because every figure downstream inherits the guess
    without inheriting the doubt.
    """
    base, quote = base.upper(), quote.upper()
    for name, url, parse in providers(base, quote, date):
        try:
            quota.spend(PROVIDER, 1)
            rate, when = parse(get(url, tries=2))
            return {"base": base, "quote": quote, "rate": float(rate),
                    "date": when, "source": name}
        except Exception as e:
            if on_fail:
                on_fail(name, e)
    return None
