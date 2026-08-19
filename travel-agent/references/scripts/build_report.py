"""Build a deliverable from a spec. Run this instead of writing assembly code.

    python scripts/build_report.py --spec trip.json --out report.html

The spec holds STRUCTURE; the HTML fragments hold CONTENT. That split is the
point: structure is the part that has repeatedly gone wrong by hand -- a
duplicated heading, a section missing from the rail, a location group short of
its core subsections -- and it is now declared once and enforced by lib/report.py.

Spec shape:

{
  "title":    "<Trip name>",
  "subtitle": "<one line: the shape of the trip>",
  "kicker":   "Trip research &amp; itinerary · <compiled date>",
  "facts":    {"Dates": "<range>", "Party": "<n> adults"},
  "fx":       {"file": "fx.json"},
  "places":   ["places.json", "places2.json"],
  "aliases":  {"<name as written in a table>": "<name it was verified under>"},
  "groups": [
    {"name": "Start here", "sections": [
        {"id": "critical", "label": "Critical &amp; time-sensitive",
         "file": "frag/critical.html"}
    ]},
    {"name": "<City>", "place": "<City>, <Country>", "sections": [
        {"id": "<city-slug>-food", "label": "Eating &amp; drinking",
         "title": "Eating and drinking — <City>", "file": "frag/<city>-food.html"}
    ]},
    {"name": "Trip-wide", "sections": [
        {"id": "entry", "label": "Entry", "raw": "frag/entry-section.html"}
    ]},
    {"name": "Honesty", "sections": ["..."]}
  ]
}

Group order is fixed: "Start here" first, one group per location in itinerary
order, then "Trip-wide" and "Honesty". The builder enforces it.

Per section, exactly one content source:
  "file"  path to an HTML fragment -- WITHOUT its own <h2>, the builder adds it
  "html"  the same thing inline
  "raw"   a complete <section>...</section> block, spliced verbatim (for
          preserved blocks carried over from an earlier build)

`aliases` exists because a table says what a reader would say -- "Thornbury" -- while
the pin has to be verified under something findable, "Thornbury Castle". Without it
the cell simply goes unlinked, silently. Both sides are trip data and live in the
spec, never in this file.

Two names never become linkable venues: the trip's own bases, and anything the
verification pass resolved to something else. The first is derived from the group
names (see `base_names`) because a base already carries its link once in its
first heading; the second is the drift guard in `load_places`.

Paths in the spec are resolved relative to the spec file, so a trip directory
can be moved without editing it.
"""
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lib import money, render
from lib.report import Report


def base_names(spec):
    """Names that must never become linkable venues: the trip's own bases.

    A base city already carries its map link once, in the first heading of its
    group. Letting it also sit in the places dict put that link in every section
    of the group instead -- five links to one base city in five of its own headings.
    Splitting on " and " matters because a group is often named for two places
    ("Lakes and Highlands") and both halves are bases.

    Derived from the spec's own group names, so it holds for any trip.
    """
    out = set()
    for g in spec.get("groups", []):
        n = g.get("name", "")
        out.add(n)
        out.update(p.strip() for p in n.split(" and "))
        if g.get("place"):
            out.add(g["place"].split(",")[0].strip())
    return {x for x in out if x}


def load_places(paths, base, aliases=None, exclude=()):
    """Merge verification output, keyed by resolved name and query name.

    Drops results that DRIFTED -- where the resolved name has nothing in common
    with what was asked for. Querying a day-trip town with the BASE city as its
    hint resolves to the base city, because the hint outweighs the name; admitting
    those makes the base city itself a linkable "venue", which then put a map
    link in every one of that city's headings rather than only the first.

    The city hint's own words do NOT count as evidence of a match. "Thornbury
    Lodge" resolved to "Thornbury House" -- a different hotel in a different
    village -- and the shared word "Thornbury" was enough to wave it through.
    Every property in a spa town shares the town's name, so matching on it means
    matching on nothing.

    `aliases` maps a name as written in the report to the key a place was
    verified under, so a table can say "Thornbury" while the pin resolves from
    "Thornbury Castle". Passed in from the spec at run time, never hardcoded.

    Non-ASCII queries skip the guard: a local-script name legitimately resolves
    to its romanization, and comparing across scripts rejects correct matches.
    """
    out, dropped = {}, []
    for p in paths:
        for r in json.loads((base / p).read_text(encoding="utf-8")):
            name = r.get("name")
            if not name:
                continue
            q = r.get("query", "")
            asked = q.split("|")[0].strip()
            hint = q.split("|")[1].strip().lower() if "|" in q else ""
            if asked and asked.isascii():
                a, g = asked.lower(), name.lower()
                toks = {t for t in a.split() if len(t) > 3 and t not in hint}
                if not (a in g or g in a or any(t in g for t in toks)):
                    dropped.append(f"{asked} -> {name}")
                    continue
            if name in exclude or asked in exclude:
                continue
            out.setdefault(name, r)
            if asked:
                out.setdefault(asked, r)
    for shown, verified in (aliases or {}).items():
        if verified in out:
            out.setdefault(shown, out[verified])
        else:
            print(f'  alias "{shown}" -> "{verified}": no such verified place')
    if dropped:
        print(f"  dropped {len(dropped)} drifted match(es): {'; '.join(dropped[:4])}"
              + (" ..." if len(dropped) > 4 else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", help="override references/templates/report.html")
    a = ap.parse_args()

    spec_path = pathlib.Path(a.spec).resolve()
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    if spec.get("fx"):
        fx = spec["fx"]
        if fx.get("file"):
            d = money.load_rate(base / fx["file"])
            print(f"  FX: {money.rate_note()}  [{d.get('source','')}]")
        else:
            money.set_rate(fx["rate"], fx["local"], fx.get("home", "USD"),
                           fx.get("date", ""))
            print(f"  FX: {money.rate_note()}")
    else:
        print("  FX: none configured — prices will print in local currency only")

    bases = base_names(spec)
    places = load_places(spec.get("places", []), base, spec.get("aliases"), bases)
    print(f"  places: {len(places)} keys from {len(spec.get('places', []))} file(s)")

    r = Report(spec["title"], spec.get("subtitle", ""), spec.get("facts"),
               spec.get("kicker"), places, a.template)

    for g in spec["groups"]:
        r.group(g["name"], g.get("place"))
        for s in g["sections"]:
            src = [k for k in ("file", "html", "raw") if s.get(k)]
            if len(src) != 1:
                raise SystemExit(f'section "{s.get("id")}": give exactly one of '
                                 f'file/html/raw, got {src or "none"}')
            if s.get("raw"):
                r.raw_section((base / s["raw"]).read_text(encoding="utf-8"))
            else:
                body = (s["html"] if s.get("html")
                        else (base / s["file"]).read_text(encoding="utf-8"))
                r.section(s["id"], s["label"], body, s.get("title"))

    r.write(a.out)
    print("  now run: python scripts/check_report.py " + a.out)


if __name__ == "__main__":
    main()
