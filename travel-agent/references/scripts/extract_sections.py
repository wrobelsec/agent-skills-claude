"""Turn an existing report into fragments + a spec the builder can rebuild from.

    python scripts/extract_sections.py old-report.html --out trip/ --spec trip.json

Use this once, to migrate a report that was assembled by hand into the
content-plus-structure split that lib/report.py expects. After that, edit the
fragments and re-run scripts/build_report.py; never hand-assemble again.

What it does:
  * writes one HTML fragment per <section>, with the <h2> REMOVED -- the builder
    owns headings, and a fragment that keeps its own is how the same heading
    shipped twice
  * records the heading text as the section's `title`
  * emits a spec with the groups read from the report's own rail

The group names and section labels come out of the existing rail, so a report
that was already correct stays correct; one that was not shows up as a spec you
can edit in one place rather than hunting through markup.
"""
import argparse, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def strip_headings(html):
    """Remove EVERY <h2>, returning (first_heading_text, body).

    Every, not the first: real content has been found carrying two, which is the
    duplicate-heading bug itself. A one-shot strip carries the second through.
    """
    found = re.findall(r"<h2>(.*?)</h2>", html, re.S)
    body = re.sub(r"<h2>.*?</h2>\s*", "", html, flags=re.S).strip()
    if not found:
        return None, body
    if len(found) > 1:
        print(f"    note: {len(found)} headings in one section — kept the first")
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", found[0])).strip()
    return title, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--out", default="frag", help="directory for fragments")
    ap.add_argument("--spec", default="trip.spec.json")
    ap.add_argument("--title", default="Trip")
    a = ap.parse_args()

    s = pathlib.Path(a.report).read_text(encoding="utf-8")
    frag = pathlib.Path(a.out); frag.mkdir(parents=True, exist_ok=True)

    # group + label per section id, straight from the rail
    rail = s[s.index("<nav"):s.index("</nav>")]
    group_of, label_of, order, cur = {}, {}, [], None
    for m in re.finditer(r'<div class="grp">([^<]+)</div>|href="#([^"]+)">([^<]*)<', rail):
        if m.group(1):
            cur = m.group(1); order.append((cur, []))
        else:
            group_of[m.group(2)] = cur
            label_of[m.group(2)] = m.group(3)
            order[-1][1].append(m.group(2))

    for m in re.finditer(r'<section id="([^"]+)">(.*?)</section>', s, re.S):
        sid, inner = m.group(1), m.group(2)
        title, body = strip_headings(inner)
        (frag / f"{sid}.html").write_text(body, encoding="utf-8")
        label_of.setdefault(sid, sid)
        if title:
            label_of[sid + "::title"] = title

    spec = {"title": a.title, "subtitle": "", "facts": {},
            "fx": {"file": "fx.json"}, "places": [], "groups": []}
    for gname, ids in order:
        g = {"name": gname, "sections": []}
        for sid in ids:
            e = {"id": sid, "label": label_of.get(sid, sid),
                 "file": f"{a.out}/{sid}.html"}
            if label_of.get(sid + "::title"):
                e["title"] = label_of[sid + "::title"]
            g["sections"].append(e)
        spec["groups"].append(g)

    pathlib.Path(a.spec).write_text(json.dumps(spec, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    n = sum(len(g["sections"]) for g in spec["groups"])
    print(f"wrote {n} fragments to {a.out}/ and {a.spec}")
    print("edit the spec (facts, fx, places, group `place` links), then:")
    print(f"  python scripts/build_report.py --spec {a.spec} --out report.html")


if __name__ == "__main__":
    main()
