# agent-skills-claude

Skills for [Claude Code](https://claude.com/claude-code).

A skill is a packaged set of instructions Claude loads when a task matches its description — a workflow, a house style, a checklist. This repo holds skills that are substantial enough to need their own reference files and research process.

## Contents

```
skills/
├── LICENSE
├── README.md                          ← you are here
├── .gitignore                         Excludes traveler-profile.md (personal data)
└── travel-agent/                      Full-service travel planning
    ├── README.md                      Full docs: install, requirements, usage
    ├── SKILL.md                        Entry point — the phased flow, dispatch, model policy
    ├── traveler-profile.md            Your stored preferences (gitignored, local only)
    └── references/
        ├── research-rules.md          The standard all research is held to
        ├── source-map.md              Where to look, what blocks, which APIs to use
        ├── agent-briefs.md            Per-track briefs, incl. Phase 3 recon and safety
        ├── matrices.md                Exact column specs for every comparison table
        ├── deliverable.md             Location-grouped section set, structure, publishing
        ├── api-compatibility.md       Where a provider is known to fail, by destination, dated
        ├── profile-template.md        Schema for traveler-profile.md
        ├── templates/report.html      Page shell and stylesheet
        ├── lib/                       Imported. Shared by every script
        │   ├── common.py              HTTP with backoff, keys, paths, locations
        │   ├── money.py               Currency symbols, dated FX, both-currencies rule
        │   ├── humanize.py            Machine values → reader-facing text
        │   ├── render.py              Standard tables, map links, link injector
        │   └── report.py              Report builder — owns headings, rail, mobile menu
        ├── tests/                     Unit tests offline, API checks live
        │   ├── test_money.py          Currency formatting
        │   ├── test_humanize.py       No machine value reaches a reader
        │   ├── test_render.py         Tables, map links, link injection
        │   ├── test_report.py         Heading ownership, structure, navigation
        │   └── test_live_apis.py      Endpoint reachability + destination probe
        └── scripts/                   Run. Destination passed at runtime
            ├── run_tests.py           ← run this FIRST, every run
            ├── build_report.py        Build a deliverable from a spec
            ├── extract_sections.py    Migrate an existing report into fragments + spec
            ├── check_report.py        Pre-publish structure, arithmetic, machine-output
            ├── climate.py             Conditions over the real window + grid-snap check
            ├── daylight.py            Sunrise/sunset per base
            ├── fx.py                  Dated FX with provider fallback
            └── places.py              Venue status, hours, spend, access, Maps link
```

**Start every run with the test suite.** Offline it takes about a second; with `--live` it confirms every endpoint is reachable *today*; with a destination it confirms a keyed provider gives the right answer *there*.

```bash
python references/scripts/run_tests.py --live \
  --country "<Country>" --address "<real address in the local script>" \
  --bbox <S> <W> <N> <E>
```

**`lib/` is imported, `scripts/` is run.** Anything two scripts need lives in `lib/`, because the alternative is copies that drift — the currency symbol map once existed in two files and printed two different things for the same price.

**Reports are built, not hand-assembled:** content in HTML fragments, structure in a spec, `build_report.py` puts them together. The builder owns every heading, which is what stops the same heading shipping twice.

## What's here

**[`travel-agent/`](travel-agent/)** — plans a trip the way a good human agent does: researches everything live from operators and from people who have actually been there, then lays the options side by side as a decision document rather than a brochure.

It runs in **phases, cheapest first**: a broad recon pass plus a safety check, then a published outline and a gate where you narrow the trip, and only then the deep research. That ordering is not politeness — on a live run the skill researched an entire region in depth before the user cancelled it, and dismissed in one line a city that later became a two-night base.

Output is a published, navigable artifact **grouped by place**: each location carries its own transport, lodging, food, things to do and day trips, with country-wide research after them. Plus a day-by-day itinerary, a booking checklist ordered by deadline, and a critical-and-time-sensitive panel at the very top.

> **Requires three agents** from [agents-claude](https://github.com/wrobelsec/agents-claude) — `travel-recon`, `travel-researcher` and `travel-scout`. The skill dispatches them by name and will not work without them. See [`travel-agent/README.md`](travel-agent/README.md).

## Install

```bash
git clone https://github.com/wrobelsec/agent-skills-claude.git ~/.claude/skills
```

Or copy a single skill into an existing setup:

```bash
cp -r travel-agent ~/.claude/skills/
```

Then install the required agents:

```bash
git clone https://github.com/wrobelsec/agents-claude.git ~/.claude/agents
```

## Related

- **[agents-claude](https://github.com/wrobelsec/agents-claude)** — the subagent definitions these skills dispatch.

## Licence

See [LICENSE](LICENSE).
