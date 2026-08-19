"""Currency: symbols, dated FX, and the both-currencies rule in one place.

Every price in a deliverable must appear in the local currency AND the
traveller's, against a dated rate. That rule was previously implemented three
times -- in the places verifier, in the table renderer, and by hand in prose --
and the copies drifted: one printed `JPY 1000`, one printed `¥1,000`, and one
printed `$6.29–$13` with mixed precision and a repeated symbol.

One module, one behaviour.

    from lib import money
    money.set_rate(<rate>, "<LOCAL>", "<HOME>", "<YYYY-MM-DD>")
    money.pair(1000, 2000)      -> local range, home range beneath it
    money.local(1370)           -> the figure in the destination's currency
    money.convert(1370)         -> the same figure for the traveller

Every value above is supplied at call time. Nothing here knows or assumes a
country: the rate, both currency codes and the date all arrive from the caller,
because the same module has to serve a trip anywhere.
"""

# ISO codes are for machines. Readers get the symbol they'd see on a menu.
SYMBOL = {
    "JPY": "¥", "USD": "$", "EUR": "€", "GBP": "£", "KRW": "₩", "CNY": "CN¥",
    "TWD": "NT$", "THB": "฿", "VND": "₫", "INR": "₹", "PHP": "₱", "IDR": "Rp",
    "AUD": "A$", "CAD": "C$", "NZD": "NZ$", "SGD": "S$", "HKD": "HK$",
    "MXN": "MX$", "BRL": "R$", "TRY": "₺", "PLN": "zł", "CZK": "Kč",
    "SEK": "kr", "NOK": "kr", "DKK": "kr", "CHF": "CHF", "ILS": "₪", "ZAR": "R",
    "MYR": "RM", "AED": "AED", "SAR": "SAR", "EGP": "E£", "ARS": "AR$",
    "CLP": "CL$", "COP": "CO$", "PEN": "S/", "RUB": "₽", "UAH": "₴",
}

_STATE = {"rate": None, "local": "", "home": "USD", "date": ""}


def sym(code):
    """Symbol for an ISO code, falling back to the code plus a space. Falling
    back is deliberate -- an unfamiliar code beats a dropped currency."""
    return SYMBOL.get((code or "").upper(), (code or "").upper() + " ")


def set_rate(rate, local_code, home_code="USD", date=""):
    """rate = units of LOCAL currency per 1 unit of the traveller's currency."""
    _STATE.update(rate=float(rate), local=local_code.upper(),
                  home=home_code.upper(), date=date)


def load_rate(path="fx.json"):
    """Configure from the JSON that scripts/fx.py writes."""
    import json, pathlib
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    set_rate(d["rate"], d["quote"], d["base"], d.get("date", ""))
    return d


def rate_note():
    """One line for the top of a report, so a rate is never undated."""
    if not _STATE["rate"]:
        return "no exchange rate configured"
    return (f"{sym(_STATE['home'])}1 = {sym(_STATE['local'])}"
            f"{_STATE['rate']:,.2f} · {_STATE['date'] or 'undated'}")


def _fmt(lo, hi, symbol):
    """Precision decided ONCE for the whole range, symbol printed ONCE.

    Two things a reader reads as sloppiness and which had both shipped:
    mixed precision across one range (`6.29–13` rather than `6.29–12.58`), and a
    symbol repeated on the upper bound when the local-currency side prints it
    once.
    """
    vals = [v for v in (lo, hi) if v is not None]
    dp = 2 if min(vals) < 10 else 0
    f = lambda x: f"{x:,.{dp}f}"
    return f"{symbol}{f(lo)}–{f(hi)}" if hi is not None else f"{symbol}{f(lo)}+"


def local(lo, hi=None):
    return _fmt(lo, hi, sym(_STATE["local"]))


def convert(lo, hi=None):
    """The traveller's currency, or '' when no rate is configured -- callers
    must degrade to local-only rather than inventing a conversion."""
    r = _STATE["rate"]
    if not r:
        return ""
    return _fmt(lo / r, (hi / r) if hi is not None else None, sym(_STATE["home"]))


def pair(lo, hi=None, sep="<br>"):
    """Both currencies, the standard presentation for any money in a matrix.
    Degrades to local-only when the FX step failed, and says nothing false."""
    a = local(lo, hi)
    b = convert(lo, hi)
    return f'{a}{sep}<span class="unv">{b}</span>' if b else a


def parse(text):
    """Pull the numbers out of a formatted range like 'JPY 1,000–2,000'."""
    import re
    n = [int(x.replace(",", "")) for x in re.findall(r"[\d,]+", text or "")]
    if not n:
        return None
    return (n[0], n[-1] if len(n) > 1 else None)
