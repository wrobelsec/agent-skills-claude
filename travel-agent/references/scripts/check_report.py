"""Pre-publish checks from deliverable.md — structure, then arithmetic.

    python check_report.py path/to/report.html

Exit code is the number of failures. Warnings don't fail; they need a human.
Adapt CANON, MUST_TABLE, MATRICES and NIGHTS per trip; the rest is generic.

Two false positives this produced on its first run, kept because they are a
better warning than any comment about care:

  * It read paired cells — "6.4 °C / 28.6 °C<br>43.5 °F / 83.5 °F" — as a single
    conversion, and confidently flagged five *correct* cells as wrong. A checker
    that handles only the shape you first thought of will condemn the rest.
  * It read a nightly rate sitting in an all-in column as a miscounted night.
    That one was a real defect, but of a different kind than the check was
    testing, so it now reports separately rather than as bad arithmetic.

Both looked exactly like report bugs. Verify a failure against the source before
"fixing" the document to satisfy the script.
"""
import re, sys

sys.stdout.reconfigure(encoding='utf-8')
PATH = sys.argv[1] if len(sys.argv) > 1 else 'report.html'
s = open(PATH, encoding='utf-8').read()
fails, warns = [], []

def strip(x):
    return re.sub(r'<[^>]+>', ' ', x).replace('&amp;', '&').replace('&nbsp;', ' ').strip()

MINUS = '−'
def f2(x):
    return float(x.replace(MINUS, '-').replace(',', ''))

# ---------------------------------------------------------------- structure
print('=' * 62)
print('STRUCTURE')
print('=' * 62)

for tag in ['section', 'table', 'thead', 'tbody', 'tr', 'div', 'main', 'caption']:
    o = len(re.findall(r'<' + tag + r'[ >]', s))
    c = len(re.findall(r'</' + tag + r'>', s))
    if o != c:
        fails.append(f'tag imbalance <{tag}>: {o} open, {c} close')
print(f'  tag balance ......................... {"FAIL" if fails else "ok"}')

ids = re.findall(r'<section id="([^"]+)"', s)
nav = re.findall(r'href="#([^"]+)"', s[s.index('<nav'):s.index('</nav>')])
orphan_nav = [n for n in nav if n not in ids]
unlinked = [i for i in ids if i not in nav]
if orphan_nav:
    fails.append(f'rail points at missing sections: {orphan_nav}')
if unlinked:
    fails.append(f'sections absent from the rail: {unlinked}')
print(f'  rail <-> sections ................... {"FAIL" if orphan_nav or unlinked else "ok"}  ({len(ids)} sections)')

# Canonical set from deliverable.md.
#
# The seven GROUP names are canonical and fixed. The section ids inside them are
# trip-specific: a trip with no fork has no "fork" section, and a route change
# renames half of them. Hardcoding ids made this script unrunnable the first time
# the itinerary changed shape, which is the opposite of what a pre-publish check
# is for. So the groups are asserted, the ids are read from the report's own rail,
# and only the sections every trip must answer are required by name.
# The deliverable is grouped by PLACE. Fixed groups top and tail it; between them
# sits one group per location, in itinerary order, each carrying the same core
# subsections. Location names are trip-specific, so they are read from the rail
# rather than declared here — but their *uniformity* is asserted, because a
# location silently missing "Where to stay" is the location-grouped version of
# the missing-section failure this script exists to catch.
FIXED_HEAD = 'Start here'
FIXED_TAIL = ['Trip-wide', 'Honesty']

# core subsection kinds every location group must carry
LOCATION_CORE = ['getting-around', 'lodging', 'todo', 'food']

# Options per category, per location. Five is a hard floor: below that the
# section is whatever the agent happened to find rather than a comparison the
# reader can choose from. Ten is a soft cap — a couple of extras that genuinely
# came up during a sweep are worth keeping, a list of thirty is not.
MIN_OPTIONS, SOFT_CAP = 5, 10

# Google Maps links come in more than one shape and a detector that knows only
# one is worse than none, because it reports "missing" against links that are
# fine. Two forms in use:
#   https://www.google.com/maps/search/?api=1&query=...   (constructed)
#   https://maps.google.com/?cid=...                      (googleMapsUri)
# Matching only the first made every canonical cid link invisible and produced
# 15 false failures. Same shape of mistake as matching a bare <table> and
# silently skipping every <table class="...">.
MAPS_LINK = r'google\.com/maps|maps\.google\.com'

REQUIRED_IDS = {
    'critical': FIXED_HEAD, 'status': FIXED_HEAD, 'itinerary': FIXED_HEAD,
    'flights': 'Trip-wide', 'ground': 'Trip-wide', 'rights': 'Trip-wide',
    'entry': 'Trip-wide', 'money': 'Trip-wide', 'health': 'Trip-wide',
    'climate': 'Trip-wide', 'language': 'Trip-wide', 'law': 'Trip-wide',
    'budget': 'Trip-wide', 'points': 'Trip-wide',
    'risk': 'Honesty', 'gaps': 'Honesty', 'sources': 'Honesty',
}

rail = s[s.index('<nav'):s.index('</nav>')]
groups_present = re.findall(r'<div class="grp">([^<]+)</div>', rail)

# which group does each rail link sit under, and in what order?
group_of, order, cur = {}, [], None
for m in re.finditer(r'<div class="grp">([^<]+)</div>|href="#([^"]+)"', rail):
    if m.group(1):
        cur = m.group(1)
    else:
        group_of[m.group(2)] = cur
        order.append(m.group(2))

structural = []
if not groups_present or groups_present[0] != FIXED_HEAD:
    structural.append(f'first rail group must be "{FIXED_HEAD}", got '
                      f'{groups_present[:1] or ["none"]}')
if groups_present[-len(FIXED_TAIL):] != FIXED_TAIL:
    structural.append(f'last rail groups must be {FIXED_TAIL}, got '
                      f'{groups_present[-len(FIXED_TAIL):]}')

# everything between head and tail is a location group
location_groups = [g for g in groups_present[1:-len(FIXED_TAIL)]] if len(
    groups_present) > len(FIXED_TAIL) else []

# Critical must be first in the rail AND first in the document. A deadline
# section halfway down is a deadline section nobody reaches in time.
if order and order[0] != 'critical':
    structural.append(f'first rail entry must be "critical", got "{order[0]}"')
if ids and ids[0] != 'critical':
    structural.append(f'first section in the document must be "critical", got "{ids[0]}"')

# location sections: id must be {slug}-{kind}, and every location needs the core set
def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

loc_report = []
for g in location_groups:
    slug = slugify(g)
    mine = [i for i in ids if i.startswith(slug + '-')]
    kinds = {i[len(slug) + 1:] for i in mine}
    absent = [k for k in LOCATION_CORE if k not in kinds]
    if not mine:
        structural.append(f'location group "{g}" has no sections with the "{slug}-" prefix')
    elif absent:
        structural.append(f'location "{g}" missing core subsection(s): {absent}')
    for sid in mine:
        i0 = s.index(f'<section id="{sid}"')
        i1 = s.index('</section>', i0)
        seg = s[i0:i1]
        # a location section must carry at least one map link — otherwise nothing
        # in it was made findable, which is the whole point of grouping by place
        if not re.search(MAPS_LINK, seg):
            structural.append(f'location section "{sid}" has no Google Maps link')
        # 5 options is a hard floor per category, 10 a soft cap. Below five the
        # section is a list of what someone happened to find rather than a
        # comparison; above ten it stops being scannable. Transport sections are
        # exempt — the number of ways to reach a place is what it is.
        if not sid.endswith('getting-around'):
            # Count the LARGEST table, not the section total. Summing let a
            # two-row decision table pass by sitting beside a four-row and a
            # two-row sibling: 2+4+2 cleared a floor of five while the table a
            # reader actually compares offered two choices. The biggest table in
            # a section is the comparison; the rest support it.
            # `<tbody ...>` and `<tr ...>` count — matching the bare tags skipped
            # every table carrying a class, the same failure that once made the
            # column check skip every `<table class=...>`.
            per_table = [len(re.findall(r'<tr[ >]', tb)) for tb in
                         re.findall(r'<tbody[^>]*>(.*?)</tbody>', seg, re.S)]
            n = max(per_table, default=0)
            if 0 < n < MIN_OPTIONS:
                structural.append(f'"{sid}" compares {n} option(s) in its largest '
                                  f'table; {MIN_OPTIONS} is the minimum per '
                                  f'category (tables: {per_table})')
            elif n > SOFT_CAP + 2:
                warns.append(f'"{sid}" lists {n} options against a soft cap of '
                             f'{SOFT_CAP} — trim to the ones that earn a row')
    loc_report.append((g, len(mine)))

misfiled = [f'{x} under "{group_of.get(x)}", expected "{g}"'
            for x, g in REQUIRED_IDS.items()
            if x in group_of and group_of[x] != g]
missing = [x for x in REQUIRED_IDS if x not in ids]
if missing:
    structural.append(f'required sections missing: {missing}')
if misfiled:
    structural.append(f'sections under the wrong rail group: {misfiled}')
fails.extend(structural)

print(f'  canonical section set ............... {"FAIL" if structural else "ok"}'
      f'  ({len(location_groups)} location(s), {len(groups_present)} groups)')
for g, n in loc_report:
    print(f'      {g}: {n} section(s)')
if missing:
    print(f'      missing: {", ".join(missing)}')

# sections whose columns are specified must contain a table
MUST_TABLE = ['entry', 'money', 'health', 'climate', 'language', 'law', 'rights']
for sid in MUST_TABLE:
    if sid not in ids:
        continue
    i = s.index(f'<section id="{sid}"')
    j = s.index('</section>', i)
    # Match <table> AND <table class="...">. Matching only the bare tag meant
    # every classed table in the document was silently skipped by this check and
    # by the column/caption checks below — they reported "ok" against tables they
    # had never looked at.
    if not re.search(r'<table[ >]', s[i:j]):
        fails.append(f'section "{sid}" is specced as a table and has none')
print(f'  specced sections print tables ....... '
      f'{"FAIL" if any("specced as a table" in f for f in fails) else "ok"}')

# required matrices from matrices.md, mapped to the section that should hold them.
# Value None means "legitimately skippable — but the report must say so".
# Required matrices. Presence is proved by a *distinguishing column header*, not by
# the section existing — a section can exist and still not contain its matrix, which
# is exactly how three went missing while every section check passed.
# None means "legitimately skippable, but the report must say so".
MATRICES = {
    'Flight options':             ('flights',  r'Book direct|All-in price'),
    'Budget scenarios':           ('budget',   r'Per person per day|Shoestring'),
    'Points and booking channel': ('points',   r'Cents<br>per point|Cents per point'),
    'Climate and daylight':       ('climate',  r'Washout risk'),
    'Mode comparison':            None,
    'Whole-path':                 None,
    'Best time to visit':         None,
}

# Location-scoped matrices are checked once PER LOCATION, keyed by id suffix.
# Checking them globally would let one city carry the lodging table for four,
# which is exactly the thinning-out the location grouping exists to prevent.
PER_LOCATION_MATRICES = {
    'lodging':        r'Bed configuration',
    'food':           r'Still open\?',
    'todo':           r'Official page|Book direct',
    'daytrips':       r'Worth-it verdict|Depart by',
    'getting-around': r'Realistic time',
}
SKIP_MARKER = re.compile(r'deliberately skipped|not built|skipped because|does not apply', re.I)
missing_mx, undocumented = [], []
for name, spec in MATRICES.items():
    if spec is None:
        near = [m.start() for m in re.finditer(re.escape(name), s, re.I)]
        if not any(SKIP_MARKER.search(s[max(0, p - 400):p + 400]) for p in near):
            undocumented.append(name)
        continue
    sid, marker = spec
    if sid not in ids:
        missing_mx.append(f'{name} (no section "{sid}")')
        continue
    i0 = s.index(f'<section id="{sid}"'); i1 = s.index('</section>', i0)
    if not re.search(marker, s[i0:i1]):
        missing_mx.append(f'{name} (section "{sid}" exists but has no "{marker.split("|")[0]}" column)')
# now the per-location ones, once for each location group
for g in location_groups:
    slug = slugify(g)
    for kind, marker in PER_LOCATION_MATRICES.items():
        sid = f'{slug}-{kind}'
        if sid not in ids:
            continue  # absence of the section is reported by the structural check
        i0 = s.index(f'<section id="{sid}"'); i1 = s.index('</section>', i0)
        seg = s[i0:i1]
        if not re.search(marker, seg) and not SKIP_MARKER.search(seg):
            missing_mx.append(f'{g} / {kind} (no "{marker.split("|")[0]}" column)')

if missing_mx:
    fails.append(f'required matrices absent: {missing_mx}')
if undocumented:
    warns.append(f'skippable matrices not documented as skipped: {undocumented}')
print(f'  required matrices ................... {"FAIL" if missing_mx else "ok"}'
      f'  ({len(MATRICES)} global + {len(PER_LOCATION_MATRICES)}x{len(location_groups)} local)')

# gaps list must not contradict the body, and must not repeat itself
if 'id="gaps"' in s:
    gi = s.index('id="gaps"'); gj = s.index('</section>', gi)
    gaps_html = s[gi:gj]
    body = s[:gi]
    raw_entries = re.findall(r'<li>(.*?)</li>', gaps_html, re.S)
    entries = [strip(x) for x in raw_entries]
    # An entry already struck through has been reconciled by the convention in
    # deliverable.md — it states the answer rather than posing an open question,
    # so it is not a contradiction and must not keep firing.
    open_entries = [strip(x) for x in raw_entries if '<s>' not in x]
    seen = {}
    for e in entries:
        k = e[:45].lower()
        seen[k] = seen.get(k, 0) + 1
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        fails.append(f'duplicate gaps entries: {dupes}')
    # A gaps entry is suspect when a *distinctive* token from it appears in the body
    # close to a resolution marker. Distinctive = capitalised, 5+ chars, not a
    # sentence-opener. Matching on common words produces noise, not findings.
    # 'chip c-ok' was in this list and had to come out: the same green chip marks
    # "venue is OPERATIONAL", so every verified venue name sitting near a gap
    # entry fired a false resolution. A marker that means two things cannot be
    # evidence for either.
    # The bare word "resolved" was in here and had to be qualified for the same
    # reason 'chip c-ok' was removed: it means two things. A caption reading
    # "coordinates resolved via Google Places" is describing geocoding, not a
    # closed gap, and it sat near enough to a gap token to fire a false warning.
    # Only phrasings that can ONLY mean "this gap is now closed" count.
    RESOLVED = re.compile(r'\bnow resolved\b|\bsince resolved\b|\bgap closed\b'
                          r'|now solved|<s>', re.I)
    # Tokens with no identifying power. Place names belong here because they
    # appear all over their own report -- but they are DERIVED from this report's
    # location groups rather than hardcoded, since a fixed list of one trip's
    # cities is useless on the next trip and silently stops filtering anything.
    STOP = {'These', 'Their', 'There', 'Where', 'Which', 'While', 'Every',
            'Whether', 'Single', 'Concert', 'Points', 'Only', 'Live', 'Two',
            # sentence-openers, seasons, weekdays and bare quantities
            'Still', 'Three', 'Several', 'About', 'After', 'Before', 'Between',
            'During', 'Under', 'Above', 'Spring', 'Summer', 'Autumn', 'Winter',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday'}
    for _g in location_groups:                       # multi-word names too
        STOP.update(w for w in re.split(r'\W+', _g) if w)
    body_txt = body
    suspects = []
    def norm(t):
        t = t.strip('.,—:;’\'"()')
        for suf in ("’s", "'s"):
            if t.endswith(suf):
                t = t[:-len(suf)]
        return t

    for e in open_entries:
        distinctive = [t for t in map(norm, e.split())
                       if len(t) >= 5 and t[:1].isupper() and t not in STOP and t.isalpha()]
        for tok in distinctive[:4]:
            # A token that appears all over the body carries no signal — a base
            # city's name sits near a green chip somewhere no matter what.
            # Only rare tokens localise to the passage they came from.
            occurrences = list(re.finditer(r'\b' + re.escape(tok) + r'\b', body_txt))
            if not occurrences or len(occurrences) > 12:
                continue
            if any(RESOLVED.search(body_txt[max(0, m.start() - 200):m.start() + 200])
                   for m in occurrences):
                suspects.append(f'"{tok}" — {e[:62]}')
                break
    if suspects:
        warns.append('gaps entries that look resolved in the body — reconcile or strike:\n        '
                     + '\n        '.join(sorted(set(suspects))[:8]))
    print(f'  gaps list self-consistent ........... {"FAIL" if dupes else "ok"}  ({len(entries)} entries)')

# ---- machine output must never reach the reader ----
#
# This check exists because a published report shipped 18 cells reading
# "PRICE_LEVEL_MODERATE". Nothing was factually wrong; an API enum had simply
# been printed straight into a human document. That is a whole class of defect,
# not one bug, and every member of it looks fine to the writer and like a broken
# page to the reader.
#
# Everything here is checked against the *visible text* with <script> and <style>
# stripped, because those legitimately contain camelCase and enums.
visible = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S)
visible = strip(visible)

MACHINE_PATTERNS = [
    (r'\b(PRICE_LEVEL|BUSINESS_STATUS|CLOSED_PERMANENTLY|CLOSED_TEMPORARILY|'
     r'OPERATIONAL|NO_MATCH|LOOKUP_FAILED|UNSPECIFIED)\w*',
     'raw API enum — map it to a phrase a reader understands'),
    (r'(?<![\w$])(?:JPY|USD|EUR|GBP|KRW|CNY|THB|VND|INR|TWD|SGD|HKD|AUD|CAD)\s*[\d]',
     'ISO currency code before a number — use the symbol (¥, $, €) instead'),
    (r'\bwheelchairAccessible\w+|\bprimaryType\w*|\buserRatingCount\b|'
     r'\bformattedAddress\b|\bdisplayName\b|\bgoogleMapsUri\b',
     'raw API field name'),
    # "None" is BOTH a Python null and an ordinary English word — "None
    # required", "None. Just a surprise on the meter" are correct prose. Flagging
    # it at the prose level produced three false positives against perfectly good
    # sentences, so it is checked at markup level instead (below), where a cell
    # containing nothing but the literal is unambiguous. null/NaN/undefined have
    # no English meaning, so those stay here.
    (r'(?<![\w>])(NaN|undefined|null)(?![\w<])',
     "a null rendered as text — say 'not stated' rather than leaking the value"),
    (r'\b\w*(?:TypeError|ValueError|KeyError|Exception|Traceback)\b',
     'an error type leaked into the document'),
    (r'\[\{|\}\]|\{\x27|\x27:\s',
     'raw dict/list syntax'),
]
machine_hits = []
for pat, why in MACHINE_PATTERNS:
    found = sorted(set(m.group(0).strip() for m in re.finditer(pat, visible)))
    # a few tokens are legitimately discussed as configuration, not emitted as data
    found = [f for f in found if f not in ('SERPAPI_API_KEY',)]
    if found:
        machine_hits.append((why, found[:6]))
# A table cell whose ENTIRE content is a null literal. Unambiguous, unlike the
# same word inside a sentence.
null_cells = re.findall(r'<td[^>]*>\s*(?:None|null|NaN|undefined)\s*</td>', s)
if null_cells:
    machine_hits.append((f'{len(null_cells)} table cell(s) contain only a null '
                         f'literal — render "not stated"', ['<td>None</td>']))

if machine_hits:
    for why, ex in machine_hits:
        fails.append(f'machine output visible to the reader — {why}: {ex}')
print(f'  no machine output in prose ........... {"FAIL" if machine_hits else "ok"}')

# every table: header count == every body row count, and has a caption
bad_cols, no_cap = [], []
for m in re.finditer(r'<table[ >].*?</table>', s, re.S):
    t = m.group(0)
    if '<caption' not in t:
        no_cap.append(strip(t[:80])[:40])
    head = t[:t.index('</thead>')] if '</thead>' in t else ''
    nh = len(re.findall(r'<th[ >]', head))
    # `<tbody ...>` counts. Testing for the bare tag skipped the column check on
    # every table that carried a class — and skipping is silent, so those tables
    # reported "ok" without ever being examined.
    tb = re.search(r'<tbody[^>]*>', t)
    if not tb:
        continue
    for r in re.findall(r'<tr[ >](.*?)</tr>', t[tb.start():], re.S):
        # count colspan, so full-width divider rows inside a table are legal
        n = 0
        for cell in re.findall(r'<td([^>]*)>', r):
            m = re.search(r'colspan\s*=\s*"?(\d+)', cell)
            n += int(m.group(1)) if m else 1
        if n and n != nh:
            bad_cols.append((strip(r.split('</td>')[0])[:30], n, nh))
if bad_cols:
    fails.append(f'{len(bad_cols)} row(s) with wrong column count: {bad_cols[:4]}')
print(f'  table column counts ................. {"FAIL" if bad_cols else "ok"}')
if no_cap:
    warns.append(f'{len(no_cap)} table(s) with no caption — the caption carries the method')
print(f'  captions present .................... {"warn" if no_cap else "ok"}')

# identity cells carry a link, never bold. Bold competes with the link for the
# eye and, before the injector ran last, actively defeated it. render.py strips
# this at build time; the check is here because that strip silently missed
# <strong> and every `<tr class=...>` row, and 40 bolded names shipped anyway.
bolded = [strip(m.group(3))[:34] for m in
          re.finditer(r'<tr[ >][^>]*>\s*(<td[^>]*>)\s*<(b|strong)>(.*?)</\2>', s, re.S)]
if bolded:
    fails.append(f'{len(bolded)} identity cell(s) still bolded — the name is the '
                 f'link, not a heading: {bolded[:4]}')
print(f'  identity cells unbolded ............. {"FAIL" if bolded else "ok"}')

# nested anchors are invalid HTML, and browsers resolve them by closing the outer
# link early -- so half a venue name silently stops being clickable. Seven shipped
# because the link injector linked inside its own output: names run longest-first,
# so "<Venue> Hotel" was linked and the shorter "<Venue>" then matched inside it.
nested = re.findall(r'<a\b[^>]*>(?:(?!</a>).)*?<a\b', s, re.S)
if nested:
    fails.append(f'{len(nested)} nested <a> tag(s) — a link inside a link; the '
                 f'outer one stops working where the inner one starts')
print(f'  no nested links ..................... {"FAIL" if nested else "ok"}')

# action links: every wide matrix row should offer somewhere to act.
# Note this is deliberately NOT satisfied by a Google Maps link — the map answers
# "where is this", the action link answers "how do I book it", and a table that
# only has the former sends the reader somewhere with nothing to do when they
# arrive.
_link_sections = ['flights'] + [f'{slugify(g)}-{k}' for g in location_groups
                                for k in ('lodging', 'food', 'todo', 'daytrips')]
for sid in _link_sections:
    if sid not in ids:
        continue
    i = s.index(f'<section id="{sid}"')
    j = s.index('</section>', i)
    seg = s[i:j]
    rows = len(re.findall(r'<tbody>', seg)) and len(re.findall(r'<tr>', seg))
    links = len(re.findall(r'href="http(?![^"]*google\.com/maps)', seg))
    if rows and links == 0:
        warns.append(f'section "{sid}" has {rows} table rows and no action links '
                     f'(map links do not count — they are not somewhere to book)')

# ---------------------------------------------------------------- arithmetic
print()
print('=' * 62)
print('ARITHMETIC')
print('=' * 62)

# cells hold either "X °C<br>Y °F" or the paired "A °C / B °C<br>P °F / Q °F"
NUM = rf'[{MINUS}-]?[0-9.]+'
bad_conv = n_conv = 0
for m in re.finditer(rf'((?:{NUM}\s*°C\s*/?\s*)+)<br>\s*((?:{NUM}\s*°F\s*/?\s*)+)', s):
    cs = [f2(x) for x in re.findall(NUM, m.group(1))]
    fs = [f2(x) for x in re.findall(NUM, m.group(2))]
    if len(cs) != len(fs):
        fails.append(f'temperature cell pairs {len(cs)} °C with {len(fs)} °F: {strip(m.group(0))}')
        continue
    for c, f in zip(cs, fs):
        n_conv += 1
        if abs((c * 9 / 5 + 32) - f) >= 0.06:
            bad_conv += 1
            fails.append(f'conversion wrong: {c} °C stated as {f} °F, should be {c * 9 / 5 + 32:.2f}')
print(f'  °C -> °F conversions ................ {"FAIL" if bad_conv else "ok"}  ({n_conv} checked)')

# lodging: per-person-per-night x people x nights == all-in
#
# The night count and party size are read from the table itself:
#
#     <table class="t-lodging" data-nights="4" data-people="4">
#
# They used to be a hardcoded map of one trip's section headings, which meant the
# check silently stopped running the moment a heading was reworded — and reworded
# headings are exactly what happens when an itinerary changes. A table that
# declares its own basis can be checked on any trip, and a table that declares
# nothing is reported rather than skipped.
money = re.compile(r'\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)')
checked = bad_inv = 0
undeclared = 0
# A lodging table is one that DECLARES its basis, wherever the class sits. The
# class is often on the scrolling wrapper rather than the table, so requiring it
# on the <table> itself skipped real tables silently -- they were neither checked
# nor reported as undeclared, and the summary read "0 rows checked" as if that
# were a pass. The declaration is the attributes; the class only decides whether
# a table WITHOUT them is a lodging table that should have had them.
for tbl in re.finditer(r'<table[^>]*>.*?</table>', s, re.S):
    body = tbl.group(0)
    head = body[:body.index('>') + 1]
    mn = re.search(r'data-nights="(\d+)"', head)
    mp = re.search(r'data-people="(\d+)"', head)
    if not mn or not mp:
        if 't-lodging' in s[max(0, tbl.start() - 200):tbl.start()] + head:
            undeclared += 1
        continue
    nights, PEOPLE = int(mn.group(1)), int(mp.group(1))
    tb = re.search(r'<tbody[^>]*>', body)
    if not tb:
        continue
    # Find the two money columns BY HEADER, not by position. Fixed positions
    # assumed one column order, so a table that ordered its columns differently
    # had the invariant read its Area and Bed-configuration cells, find no money
    # in them, and skip every row -- while the summary still printed "ok". A
    # declared basis that cannot be located is reported, never passed over.
    ths = [strip(x).lower() for x in
           re.findall(r'<th[^>]*>(.*?)</th>', body[:tb.start()], re.S)]
    ipp = next((i for i, h in enumerate(ths) if 'per person' in h), None)
    itot = next((i for i, h in enumerate(ths)
                 if ('all-in' in h or 'total' in h) and 'per person' not in h), None)
    if ipp is None or itot is None:
        warns.append(f'a lodging table declares nights/people but has no '
                     f'"per person" and total column to check ({ths[:4]})')
        continue
    rows_seen = 0
    for r in re.findall(r'<tr[ >](.*?)</tr>', body[tb.start():], re.S):
        tds = re.findall(r'<td.*?>(.*?)</td>', r, re.S)
        if max(ipp, itot) >= len(tds):
            continue
        rows_seen += 1
        pp = [f2(x) for x in money.findall(strip(tds[ipp]))]
        tot = [f2(x) for x in money.findall(strip(tds[itot]))]
        if not pp or not tot:
            continue
        implied = tot[0] / (pp[0] * PEOPLE)
        # a row that states a nightly rate in the total column is a column-basis
        # mismatch, not an arithmetic error — flag it as its own thing
        if re.search(r'/\s*night|per night', strip(tds[itot]), re.I):
            warns.append(f'"{strip(tds[0])[:32]}" states a nightly rate in the all-in column '
                         f'— the column header promises the stay total')
            continue
        checked += 1
        if abs(implied - nights) > 0.12:
            bad_inv += 1
            fails.append(f'lodging invariant: {strip(tds[0])[:32]} implies '
                         f'{implied:.2f} nights, expected {nights}')
print(f'  per-person x people x nights = total  {"FAIL" if bad_inv else "ok"}'
      f'  ({checked} rows checked)')
if undeclared:
    warns.append(f'{undeclared} lodging table(s) carry no data-nights/data-people, '
                 f'so the arithmetic invariant could not run on them — add the '
                 f'attributes rather than leaving the check silently skipped')

# ---------------------------------------------------------------- verdict
print()
print('=' * 62)
for w in warns:
    print(f'  WARN  {w}')
for f in fails:
    print(f'  FAIL  {f}')
print('=' * 62)
print(f'{len(fails)} failure(s), {len(warns)} warning(s)')
sys.exit(len(fails))
