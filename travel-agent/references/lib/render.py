"""Standard table rendering, so every matrix presents the same field the same way.

Before this existed, each table was hand-written and they drifted: one showed
hours as seven lines and another omitted them, one bolded place names (which
broke the map-link injector outright), one printed `JPY 1000` and another `¥1,000`.

A column defined once here appears identically everywhere it is used.

    from lib import render, money
    render.venues("<caption>", rows, places, kind="food")
"""
import re, urllib.parse
from . import humanize as H
from . import money as M

# The standard column set for a venue matrix. Order is fixed by matrices.md:
# identity, the normalized comparator, then detail. Changing it here changes it
# in every report.
VENUE_COLUMNS = ["Place", "What", "Hours", "Typical spend", "Rating",
                 "Step-free", "Payment", "Verdict"]

LODGING_COLUMNS = ["Property", "Per person / night", "Book", "Stay total",
                   "Bed configuration", "Rating", "Step-free", "Payment",
                   "Still open?", "Note"]


def maps_url(name=None, place_id=None, lat=None, lon=None):
    """Canonical Google Maps link. Prefer place_id: a name-only query resolves
    to whichever branch Google likes, which has already put the wrong branch of
    a chain and a cafe in the wrong neighbourhood into a published report."""
    base = "https://www.google.com/maps/search/?api=1&query="
    if place_id and name:
        return (base + urllib.parse.quote(name)
                + "&query_place_id=" + urllib.parse.quote(place_id))
    if lat is not None and lon is not None:
        return base + f"{lat},{lon}"
    if name:
        return base + urllib.parse.quote(name)
    return ""


MAPS_PATTERN = r'google\.com/maps|maps\.google\.com'


def place_link(rec, display=None):
    """A place name, linked, and deliberately NOT bolded.

    The link is the emphasis. Bolding defeated the link injector -- `<b>Name</b>`
    never matched -- and whole sections shipped with no map links while every
    check reported clean. In an identity column a place name is a link and
    nothing else.
    """
    label = display or (rec or {}).get("name", "") or ""
    url = (rec or {}).get("maps_url") or maps_url(name=label)
    return f'<a href="{url}">{label}</a>' if url else label


def spend(rec):
    """Typical spend. Real figure in both currencies first; the ordinal band is
    a genuine last resort and never appears beside a number."""
    raw = (rec.get("price") or "").strip()
    lvl = (rec.get("price_level") or "").strip()
    if raw.startswith("PRICE_LEVEL_"):      # tolerate pre-upgrade data files
        lvl, raw = raw, ""
    if raw and any(c.isdigit() for c in raw):
        nums = M.parse(raw)
        if nums:
            return M.pair(nums[0], nums[1])
        return raw
    b = H.band(lvl)
    return f'{b}<br>{H.unv("band only — no figure published")}' if b else H.UNKNOWN


def scroll(table_html):
    """Every matrix in its own horizontal scroller; the page body never scrolls
    sideways."""
    return f'<div class="scroll">\n{table_html}\n</div>'


def _table(cls, caption, headers, rows, attrs=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                     for r in rows)
    n = len(headers)
    for i, r in enumerate(rows):
        if len(r) != n:
            raise ValueError(f"row {i} has {len(r)} cells, header has {n}: {r[:2]}")
    return (f'<table class="{cls}"{attrs}>\n<caption>{caption}</caption>\n'
            f'<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>')


def venues(caption, rows, places, kind="food"):
    """rows: (place_key, what, verdict, action_link).

    `kind` decides the last column only: food tables close with "Still open?",
    everything else with the action link, per the required-matrix markers.
    """
    last = "Still open?" if kind == "food" else "Official page"
    out = []
    for key, what, verdict, action in rows:
        r = places.get(key)
        if not r:
            out.append([key, what] + [H.UNKNOWN] * 5 + [verdict, action or H.UNKNOWN])
            continue
        tail = H.status(r.get("status")) if kind == "food" else (action or H.status(r.get("status")))
        out.append([
            place_link(r), what, H.hours(r.get("hours")), spend(r),
            H.rating(r.get("rating"), r.get("reviews")), H.access(r.get("access")),
            H.payment(r.get("cash_only"), r.get("cards")), verdict, tail,
        ])
    return scroll(_table("t-food", caption, VENUE_COLUMNS + [last], out))


def lodging(caption, rows, places, nights, people):
    """rows: (place_key, per_person, total, beds, note).

    `data-nights` / `data-people` are emitted so the arithmetic invariant can
    run. They used to be a hardcoded map of one trip's headings, which meant the
    check silently stopped the moment a heading was reworded.
    """
    out = []
    for key, pp, total, beds, note in rows:
        r = places.get(key, {})
        site = r.get("site", "")
        book = f'<a href="{site}">Official site</a>' if site else H.UNKNOWN
        out.append([
            place_link(r, key if not r else None), pp, book, total, beds,
            H.rating(r.get("rating"), r.get("reviews")), H.access(r.get("access")),
            H.payment(r.get("cash_only"), r.get("cards")),
            H.status(r.get("status")), note,
        ])
    return scroll(_table("t-lodging", caption, LODGING_COLUMNS, out,
                         attrs=f' data-nights="{nights}" data-people="{people}"'))


def table(caption, headers, rows, cls="t-dist"):
    """Escape hatch for matrices with their own columns -- transport legs,
    climate, budget. Still goes through the same caption/scroll/column-count
    discipline as the standard ones."""
    return scroll(_table(cls, caption, headers, rows))


# ------------------------------------------------------------- link injection
def unbold_identity(html):
    """Strip bold from the first cell of each row, BEFORE linking.

    Order matters: unbolding afterwards leaves <b><a>...</a></b>, with the bold
    still competing with the link. Bold in later cells carries a finding -- a
    closure day, a cash-only warning -- and stays.

    Both `<tr>` and `<tr class=...>` count, and both <b> and <strong> count.
    The first version matched a literal `<tr>` and stripped only `<b>`, so every
    row carrying an attribute and every name written with <strong> kept its bold
    -- 40 of them shipped while this reported success. A rule that recognises
    one spelling of the thing it forbids is worse than no rule, because the
    report passes.
    """
    def fix(m):
        return re.sub(r'(<td[^>]*>)\s*<(b|strong)>(.*?)</\2>', r'\1\3',
                      m.group(0), count=1, flags=re.S)
    return re.sub(r'<tr[ >].*?</tr>', fix, html, flags=re.S)


def inject_links(html, places, names=None):
    """Link the first mention of each known place inside one section.

    Scoped per section: linking only the first occurrence document-wide leaves
    later sections with no map link at all, which is how whole sections once
    shipped unlinked.
    """
    protected = []
    def stash(m):
        protected.append(m.group(0))
        return f"\x00{len(protected)-1}\x00"
    # Headings are protected too. The section heading already carries the city
    # link where one belongs -- once per group -- and letting the injector reach
    # it repeated that link in every heading of the group instead of the first.
    html = re.sub(r'<a\b.*?</a>|<caption>.*?</caption>|<th[^>]*>.*?</th>'
                  r'|<h[1-3][^>]*>.*?</h[1-3]>',
                  stash, html, flags=re.S)
    for n in sorted(names or places, key=len, reverse=True):
        r = places.get(n)
        if not r or not r.get("maps_url"):
            continue
        # plain word boundaries only -- excluding '<' and '>' meant the
        # commonest case, <b>Name</b>, could never match
        m = re.search(r'(?<!\w)' + re.escape(n) + r'(?!\w)', html)
        if m:
            # Stash the anchor we just made, exactly like a pre-existing one.
            # Without this the loop could link INSIDE its own output: names run
            # longest-first, so "<Venue> Hotel" was linked and then the shorter
            # "<Venue>" matched inside that anchor's text, producing nested <a>
            # tags -- invalid HTML that browsers resolve by closing the outer
            # link early, so half the name stopped being clickable. Only the
            # anchors present at entry were protected; the ones created here
            # were not.
            protected.append(place_link(r, n))
            html = html[:m.start()] + f"\x00{len(protected)-1}\x00" + html[m.end():]
    return re.sub(r'\x00(\d+)\x00', lambda m: protected[int(m.group(1))], html)
