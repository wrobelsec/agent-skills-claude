"""Assemble a deliverable. Call this instead of writing assembly code per trip.

The structural rules from deliverable.md are enforced here rather than
remembered: the location grouping, the rail, the mobile menu, the city link once
per group, and -- the reason this class exists -- **the builder owns every
heading**.

A section is added as `section(id, title, body)` and the builder emits the
`<h2>`. A body that carries its own `<h2>` raises. That is not fussiness: a
published report shipped one section's heading twice, because the body and the
assembly each believed they owned it and neither could see the other. Ownership
has to sit in exactly one place.

    from lib.report import Report
    from lib import money

    money.load_rate("fx.json")
    r = Report("<Trip name>", "<one-line subtitle>",
               facts={"Dates": "<range>", "Party": "<n> adults"})
    r.group("Start here")
    r.section("critical", "Critical &amp; time-sensitive", body_html)
    r.group("<First city>", place="<First city>, <Country>")
    r.section("<slug>-food", "Eating &amp; drinking", table_html)
    r.write("<trip>.html")
"""
import pathlib, re, urllib.parse
from . import render, humanize

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "report.html"

FIXED_HEAD = "Start here"
FIXED_TAIL = ["Trip-wide", "Honesty"]


class Report:
    def __init__(self, title, subtitle="", facts=None, kicker=None,
                 places=None, template=None):
        self.title = title
        self.subtitle = subtitle
        self.facts = facts or {}
        self.kicker = kicker or "Trip research &amp; itinerary"
        self.places = places or {}
        self.template = pathlib.Path(template) if template else TEMPLATE
        self._groups = []          # [(name, place_or_None, [(id, label, html)])]

    # ------------------------------------------------------------- structure
    def group(self, name, place=None):
        """Start a rail group. `place` makes the group's name a map link, once,
        on its first section -- repeating it in every subsection is noise."""
        self._groups.append((name, place, []))
        return self

    def section(self, sid, label, body, title=None):
        """Add a section. The builder emits the <h2>; `body` must not contain one."""
        if not self._groups:
            raise ValueError("call group() before section()")
        if re.search(r'<h2[\s>]', body):
            raise ValueError(
                f'section "{sid}": body contains its own <h2>. The builder owns '
                f'headings -- pass the text as `label`/`title`, not markup. '
                f'(This check exists because a heading shipped twice.)')
        self._groups[-1][2].append((sid, label, title or label, body.strip()))
        return self

    def raw_section(self, html):
        """Splice a preserved <section>...</section> verbatim, for blocks
        carried over from an earlier build."""
        m = re.search(r'<section id="([^"]+)"', html)
        if not m:
            raise ValueError("raw_section needs a <section id=...>")
        sid = m.group(1)
        h2 = re.search(r'<h2>(.*?)</h2>', html, re.S)
        label = re.sub(r'<[^>]+>', '', h2.group(1)) if h2 else sid
        self._groups[-1][2].append((sid, label, label, html))
        return self

    # ---------------------------------------------------------------- render
    def _decorate(self, sid, title, body, group_name, place, first):
        """Wrap a section: heading, then the standard passes over its content."""
        head = f"<h2>{title}</h2>"
        if first and place:
            url = ("https://www.google.com/maps/search/?api=1&query="
                   + urllib.parse.quote(place))
            linked = title
            for word in sorted({group_name, group_name.split(" and ")[0]},
                               key=len, reverse=True):
                if word in title:
                    linked = title.replace(word, f'<a href="{url}">{word}</a>', 1)
                    break
            else:
                linked = f'{title} <a href="{url}">{group_name}</a>'
            head = f"<h2>{linked}</h2>"
        inner = f"{head}\n{body}"
        if self.places:
            inner = render.inject_links(render.unbold_identity(inner), self.places)
        return f'<section id="{sid}">\n{humanize.scrub(inner)}\n</section>'

    def _nav(self):
        rail, mob = [], []
        for name, _place, items in self._groups:
            rail.append(f'  <div class="grp">{name}</div>')
            mob.append(f'  <div class="grp">{name}</div>')
            for sid, label, _t, _b in items:
                rail.append(f'  <a href="#{sid}">{label}</a>')
                mob.append(f'  <a href="#{sid}">{label}</a>')
        return "\n".join(rail), "\n".join(mob)

    def validate(self):
        """Cheap structural assertions, raised before anything is written."""
        names = [g[0] for g in self._groups]
        if not names:
            raise ValueError("report has no groups")
        if names[0] != FIXED_HEAD:
            raise ValueError(f'first group must be "{FIXED_HEAD}", got "{names[0]}"')
        if names[-len(FIXED_TAIL):] != FIXED_TAIL:
            raise ValueError(f"last groups must be {FIXED_TAIL}, got {names[-2:]}")
        ids = [s[0] for g in self._groups for s in g[2]]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"duplicate section ids: {sorted(dupes)}")
        if ids and ids[0] != "critical":
            raise ValueError(f'first section must be "critical", got "{ids[0]}"')
        return self

    def html(self):
        self.validate()
        rail, mob = self._nav()
        body = []
        for name, place, items in self._groups:
            for i, (sid, _label, title, content) in enumerate(items):
                body.append(
                    content if content.lstrip().startswith("<section")
                    else self._decorate(sid, title, content, name, place, i == 0))

        facts = "\n".join(
            f'    <div class="fact"><dt>{k}</dt><dd>{v}</dd></div>'
            for k, v in self.facts.items())
        shell = self.template.read_text(encoding="utf-8")
        return (shell
                .replace("{{TITLE}}", self.title)
                .replace("{{KICKER}}", self.kicker)
                .replace("{{SUBTITLE}}", self.subtitle)
                .replace("{{FACTS}}", facts)
                .replace("{{RAIL}}", rail)
                .replace("{{MOBNAV}}", mob)
                .replace("{{BODY}}", "\n\n".join(body)))

    def write(self, path):
        out = self.html()
        pathlib.Path(path).write_text(out, encoding="utf-8")
        n_sec = len(re.findall(r'<section id=', out))
        n_map = len(re.findall(render.MAPS_PATTERN, out))
        print(f"wrote {path}: {len(out):,} chars, {n_sec} sections, {n_map} map links")
        return out
