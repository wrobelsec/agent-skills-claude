"""Machine values in, reader-facing text out.

This exists because a published report shipped eighteen cells reading
`PRICE_LEVEL_MODERATE`. Nothing was factually wrong -- an API enum had simply
been printed straight into a human document. That is a class of defect: it looks
fine to whoever wrote the code and broken to whoever reads the page.

Every translation lives here so there is one answer per value, and
scripts/check_report.py fails the build if an untranslated one reaches the page.
"""
import re

# ---------------------------------------------------------------- price bands
# Google's priceLevel is ORDINAL and LOCALE-RELATIVE. Measured over one run's
# verified venues, MODERATE alone spanned an 8x range in local currency, and
# one INEXPENSIVE venue shared a band with sixteen MODERATE ones -- so it
# never converts to money and is never shown beside a real figure. A relative
# label in one market is also not comparable to the same label in another.
BAND = {
    "PRICE_LEVEL_FREE":           ("Free", "c-ok"),
    "PRICE_LEVEL_INEXPENSIVE":    ("LOW",  "c-ok"),
    "PRICE_LEVEL_MODERATE":       ("MID",  "c-warn"),
    "PRICE_LEVEL_EXPENSIVE":      ("HIGH", "c-flag"),
    "PRICE_LEVEL_VERY_EXPENSIVE": ("TOP",  "c-flag"),
}

# ------------------------------------------------------------ business status
STATUS = {
    "OPERATIONAL":        ("Open", "c-ok"),
    "CLOSED_TEMPORARILY": ("Temporarily closed", "c-warn"),
    "CLOSED_PERMANENTLY": ("Permanently closed", "c-flag"),
    "NO_MATCH":           ("Could not be found", "c-flag"),
    "?":                  ("Area, not a business", "c-ok"),
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday"]

UNKNOWN = '<span class="unv">UNVERIFIED</span>'


def chip(text, cls="c-ok"):
    return f'<span class="chip {cls}">{text}</span>'


def unv(text):
    return f'<span class="unv">{text}</span>'


def value(v, unknown="not stated"):
    """Never let None/True/False reach a reader. Python's None printed into a
    document reads as a bug, and 'True' is not an answer to a yes/no question."""
    if v is None or v == "":
        return unv(unknown)
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v)


def band(price_level):
    """Ordinal price band as a coloured chip, or '' when unknown."""
    if price_level in BAND:
        label, cls = BAND[price_level]
        return chip(label, cls)
    return ""


def status(code):
    code = (code or "?").strip()
    if code.startswith("LOOKUP_FAILED"):
        return chip("Lookup failed", "c-warn")
    label, cls = STATUS.get(code, (code.replace("_", " ").capitalize(), "c-flag"))
    return chip(label, cls)


def hours(weekday_descriptions):
    """Seven lines of opening hours compressed to what a planner needs: the
    typical window, and the closed days. Closure days matter most -- a Tuesday
    closure has ruined more itineraries than any other single fact."""
    h = weekday_descriptions or []
    if not h:
        return UNKNOWN
    closed = [d[:3] for d in DAYS
              if any(x.startswith(d) and "Closed" in x for x in h)]
    windows = []
    for x in h:
        body = x.split(": ", 1)[1] if ": " in x else ""
        if body and "Closed" not in body:
            windows.append(re.sub(r"[  ]", " ", body))
    typical = max(set(windows), key=windows.count) if windows else ""
    typical = typical.replace(" AM", "am").replace(" PM", "pm")
    out = typical or unv("hours UNVERIFIED")
    if closed:
        out += f'<br><b>Closed {", ".join(closed)}</b>'
    elif windows and len(set(windows)) == 1:
        out = "Daily " + out
    return out


def access(text):
    """Step-free access, phrased for the person deciding whether someone in the
    party can get in -- never as API field names."""
    a = (text or "").strip()
    if not a:
        return UNKNOWN
    if a.startswith("no "):
        return chip(f"No step-free {a[3:]}", "c-flag")
    if a.startswith("step-free: "):
        return chip(f"Step-free {a[11:]}", "c-ok")
    return chip(a, "c-ok")


def payment(cash_only, cards=None):
    if cash_only:
        return chip("Cash only", "c-warn")
    if cards:
        return chip("Cards accepted", "c-ok")
    return UNKNOWN


def rating(score, count):
    if not score:
        return unv("—")
    return f"{score} {unv(f'({count:,})')}" if count else str(score)


def scrub(html):
    """Last-resort pass over generated markup for machine values that escaped.

    Preserved blocks from earlier runs carry whatever the API handed them, so
    this catches enums and nulls that never went through the helpers above.
    """
    from . import money
    subs = [
        (r'(<td[^>]*>)\s*(?:None|null|NaN|undefined)\s*(</td>)',
         r'\1<span class="unv">not stated</span>\2'),
        (r'\bCLOSED_PERMANENTLY\b', 'Permanently closed'),
        (r'\bCLOSED_TEMPORARILY\b', 'Temporarily closed'),
        (r'(?<![\w-])OPERATIONAL(?![\w-])', 'Open'),
    ]
    for pat, rep in subs:
        html = re.sub(pat, rep, html)
    # Every ISO code money.py knows, not an arbitrary handful. An earlier version
    # listed five by hand, so a trip in any other currency silently shipped the
    # bare code where a reader expects the symbol.
    for code, symbol in money.SYMBOL.items():
        html = re.sub(r'\b' + code + r'\s*(?=[\d])', symbol, html)
    return html
