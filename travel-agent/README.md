# travel-agent

Full-service travel planning for [Claude Code](https://claude.com/claude-code). It researches a trip live — flights, trains, lodging, food, excursions, entry rules, law, points — across operators' own sites, forums, and local-language sources, then builds comparison matrices and a day-by-day itinerary, and publishes the lot as a navigable artifact.

The output is a **decision document, not a brochure.** Every row carries the link you'd act on, every matrix ends with a pick and the reasoning, and anything that couldn't be confirmed says `UNVERIFIED` rather than quietly disappearing.

---

## ⚠️ Requires three agents

This skill does not work on its own. It dispatches three custom subagents by name:

- **`travel-recon`** (Sonnet) — the Phase 3 breadth pass, one per destination. Its standing rules are the *inverse* of the others': stop at the first good answer, bands not figures, never chase fine print
- **`travel-researcher`** (Sonnet) — the safety check, then flights, lodging, food, day trips, entry and health, points, law, fare rules
- **`travel-scout`** (Haiku) — ground transport, experiences, community sentiment, language

Install them from **[agents-claude](https://github.com/wrobelsec/agents-claude)**:

```bash
git clone https://github.com/wrobelsec/agents-claude.git ~/.claude/agents
```

Then start Claude Code and confirm all three appear in the available agent list. They carry the anti-fabrication rules, blocked-source ladder, API-first source list, budget-triage protocol, and the **gather-don't-compute boundary** that the research depends on — the skill's briefs assume those are already in force and don't restate them.

**Why recon is its own agent type rather than a briefed researcher:** every other agent here is built to chase detail, and one merely *told* to be shallow drifts back into fare conditions and opening hours because that is what it is for. The rules that keep the phase cheap belong in the agent definition, the same way the anti-fabrication rules do.

---

## Install

```bash
git clone https://github.com/wrobelsec/agent-skills-claude.git ~/.claude/skills
```

Or copy just this skill:

```bash
cp -r travel-agent ~/.claude/skills/
```

Invoke with `/travel-agent`, or just describe a trip — the skill triggers on planning a trip, comparing destinations or routes, asking where to stay or eat or fly, weighing layovers, working out points versus cash, or asking for an itinerary.

## Requirements

- **Claude Code** with subagent support.
- **The three agents above.** Non-negotiable.
- **`WebSearch` and `WebFetch`** in the session.
- **Browser tools** optional but genuinely useful — many booking engines and some official sites are JS-rendered and return nothing to a plain fetcher.
- **No API keys needed to start.** The skill uses free keyless endpoints for commodity facts (geocoding, daylight, holidays, weather, FX) and works fully without any signup.

### Optional API keys

Four country-agnostic keyed APIs meaningfully improve two things scraping handles badly — **flight fares** (meta-search often refuses multi-city queries outright) and **venue hours and closure status** (the commonest way a food or excursion pick goes stale). Setup instructions, the free-tier caveats, and the security tradeoff are in **[agents-claude → travel/README.md](https://github.com/wrobelsec/agents-claude/blob/main/travel/README.md#optional-api-keys)**, since the agents are what actually call them.

Short version: **SerpApi's Google Flights** for multi-city and open-jaw fares, **Google Places** for venue status and hours, **Geoapify or LocationIQ** for geocoding at volume, **Sherpa** as an entry-requirements cross-check. Keys go in the `env` block of `~/.claude/settings.json`, and the scaffold ships with **empty strings** — falsy, so every call site degrades cleanly, where a `your-key-here` placeholder would look set and fail confusingly at the API. **Every one is optional and a missing key degrades gracefully** — the affected track falls back to normal research and says so in its findings.

**The scaffold, ready to paste into `~/.claude/settings.json`:**

```json
{
  "env": {
    "SERPAPI_API_KEY": "",
    "GOOGLE_PLACES_API_KEY": "",
    "GEOAPIFY_API_KEY": "",
    "SHERPA_API_KEY": ""
  }
}
```

Merge that `env` block into whatever is already in the file. Leave any key you don't have as an **empty string** rather than deleting the line or writing a placeholder — empty is falsy, so every call site degrades cleanly and says it did, whereas `your-key-here` passes a presence check and then fails at the API with a confusing error.

Two warnings that are cheap to inherit and expensive to rediscover: **Amadeus Self-Service, which this list used to recommend, was decommissioned on 17 July 2026** — so re-check any provider before relying on it, which is what the skill's discovery step is for. And **at least one geocoder returns confidently wrong coordinates for non-Latin addresses** — on one run, three probes in three cities each resolved to a different wrong country, while the keyless fallback returned honest empties for the same queries. The dated per-provider record is in `references/api-compatibility.md`.

Destination-specific APIs — national transit open-data programmes, tourism boards, municipal portals — are **discovered per trip** by the skill's API-discovery step rather than configured permanently, since what exists varies by country and free tiers change.

---

## Files

| File | What it's for |
|---|---|
| **`SKILL.md`** | The entry point Claude reads. Intake and the gate round, the API-discovery step, research depth levels, **dispatch rules** (waves, concurrency cap, search budgets), the model policy, and the traveler-profile contract. Start here to understand the flow. |
| **`references/research-rules.md`** | The standard every agent's findings are held to — sourcing, money, time, health and safety, legal exposure, transport, and how findings get reported. Read before dispatching, and again during synthesis when a finding looks too clean. |
| **`references/source-map.md`** | Where to look, per domain. Also: **which sources block automated access and what to do about each**, and **which free keyless APIs to query instead of scraping**. |
| **`references/agent-briefs.md`** | The per-track brief for each of the twelve research tracks (A–L), with the exact table each must return. |
| **`references/matrices.md`** | Exact column specifications for every comparison table — flights, lodging, food, day trips, distances, budget, points, discounts, **climate and daylight**. **The columns here are the columns that must appear in the deliverable.** Also names the seven sections whose columns live in the briefs instead, so they can't quietly become prose. |
| **`references/deliverable.md`** | The **location-grouped section set**, the *Critical and time-sensitive* spec, the map of which track fills which section, and the publishing rules — desktop rail, **mobile floating menu**, wide-table layout, theme handling, the pre-publish arithmetic check, what must never be silently dropped. |
| **`references/lib/`** | The shared helpers every script imports. `money.py` owns currency — symbols, the dated rate, the both-currencies rule. `humanize.py` turns API values into text a person reads. `render.py` owns table columns and map links. `report.py` is the builder. **Anything two scripts need lives here**, because the alternative is copies that drift: the currency symbol map once existed twice and printed two different things for the same price. |
| **`references/scripts/hotels.py`** | **Live lodging rates for real dates and a real party size** — the question Google Places cannot answer, since it has no concept of a date or an occupancy. Returns per-night and stay-total figures, derives the per-person number a matrix publishes, and reports properties with **no** rate as sold out rather than as missing data. It does **not** return bed configuration: it will price four adults and stay silent on whether they get four beds. |
| **`references/lib/quota.py`** | **What every key has left, checked before a run and enforced on every call.** Metered providers are read from the provider itself; the rest are counted locally against `<PROVIDER>_MONTHLY_LIMIT`, and the two are labelled differently because a local count cannot see another machine. Refuses a batch that would run out part-way — a half-finished sweep leaves unverified rows indistinguishable from genuine failures. |
| **`references/lib/serpapi.py`** | The single client for live prices. Every response is cached and keyed by the exact query, so a repeat sweep costs nothing; `--refresh` is the only way to re-buy. The credential is hashed out of cache keys and never printed. |
| **`references/tests/`** | The test suite. **Unit tests run offline** against fabricated fixtures and guard the transformations that have broken in published output — currency formatting, machine-value translation, link injection, heading ownership. **Live tests** confirm every endpoint is reachable today and that a keyed provider answers correctly *for this destination*. Every case is a defect that actually shipped. |
| **`references/scripts/`** | The runnable tools — **`run_tests.py` first**, then `build_report.py`, `check_report.py`, plus fetch-and-compute for climate, daylight, FX and venue verification. **None hardcodes a destination, currency, date or path**; all of it is passed at run time, so the same scripts serve any trip. |
| **`references/templates/report.html`** | The page shell and stylesheet — theme tokens, wide-table scrollers, the sticky rail, the mobile menu. |
| **`references/profile-template.md`** | Schema for `traveler-profile.md`, including **per-traveller records** and the activities list. |
| **`traveler-profile.md`** | **Your** stored preferences — a record per traveller (referenced by nickname), home airports, loyalty programs, activities you enjoy, standing preferences, model assignment, trip history. Written on first run, updated after. **Gitignored** — it's personal and stays local. |

---

## How a run goes

0. **Test suite.** `run_tests.py --live` before anything else — about a second offline, plus a reachability check on every endpoint the skill depends on. This exists because providers break silently: over this skill's life an FX host started returning 403s mid-run, a daylight API began refusing fetchers, a flight API was decommissioned between runs, and a climate endpoint began rate-limiting under ordinary use. None announced it; each surfaced as a confusing failure inside unrelated work. Missing keys **skip**, not fail — the skill degrades to keyless research rather than stopping.
1. **Intake.** One gate round (intake style, model assignment), then trip essentials — **date flexibility**, **sleeping arrangements**, and **a short record per traveller**: a nickname, age range, mobility, health concerns, dietary needs, passport. It offers to save each person, asked individually, so a later run can open with *"same four as last time?"* rather than twenty-four questions. Those fields do real work: age gates passes and discounts, mobility gates lodging and day trips, health gates the air-quality and street-food verdicts, and passport drives one entry row per nationality.
2. **API discovery, then the destination probe.** Scouts what structured data exists for this destination, fetches current rate limits live, and asks whether you want to supply keys, stay keyless, or consider paid options. Then re-runs the suite with `--country/--address/--bbox` to **test the configured keys against this specific country before any research starts** — a key that authenticates is not a key that works here. One provider returns coordinates in the wrong *country* for non-Latin addresses without erroring, which is only catchable by checking an answer you already know. Results are recorded, dated, in `references/api-compatibility.md`, and stale exclusions get re-tested rather than inherited forever.
3. **Recon, and a safety check.** One `travel-recon` agent per destination — how you reach it, how it connects onward, what is worth doing, and what lies in between — plus one safety agent covering advisories with their *actual reasoning*, instability, crime aimed at visitors, outbreaks with case numbers, and **natural-disaster and severe-weather seasons**. Deliberately shallow: bands not fares, names not opening hours. **Skipped entirely if you arrive with a set itinerary**, since there is nothing left to decide.
4. **Outline, publish, and a gate.** A rough trip shape is published as the artifact right away — critical deadlines already on top — and you narrow it: which places stay, how long in each, dates. **Nothing expensive runs until you answer.** This is the phase that exists because a live run researched a whole region in depth and then had it cancelled.
5. **Preferences.** Now that the destinations are real, it asks what you actually want to *do* — fixtures, festivals, classes, courses, circuits, markets — and saves it to the profile. **Anything you name as a must-see becomes its own section** in the report rather than three rows inside a table.
6. **Pre-fetch.** Anything knowable before dispatch — fares for the routes in scope, entry rules, coordinates, holidays, climate over the actual travel window, the dated FX rate — is fetched and folded into the briefs as results, with caveats intact.
7. **Deep research.** You pick the split, and it shows the real agent count for *your* trip before you choose: Quick, Standard, or Exhaustive. Lodging, food, things to do, sentiment and day trips are dispatched **once per location**; flights, entry/health, points, law, fare rules and language run once for the trip. Waves of 4–6, ordered so air and entry/health land first.
8. **Verification.** What the agents found gets machine-checked, and this pass now returns most of a table's columns rather than just a pass/fail: `business_status`, **opening hours with closure days**, a **real price band in local currency**, rating with review count, **step-free access**, whether the place is **cash-only**, and a Maps link built from the resolved `place_id`. One consistent standard rather than twelve, and **the point where a fabricated row gets caught** — a venue name that won't resolve is the tell.
9. **Computation.** The figures nobody publishes in the form the trip needs get derived here — conditions over the exact travel dates rather than the calendar month, event frequencies rather than averages, daylight at each base, pass break-evens against the real itinerary. Agents have no shell, so this is orchestrator work by construction.
10. **Synthesis.** Matrices built to spec, contradictions between tracks surfaced rather than averaged away, every matrix closed with a pick. Then `references/scripts/check_report.py` runs: tag balance, the section set, **every location carrying its core subsections**, **every required matrix present per location or documented as skipped**, table column counts, captions, **a gaps list that doesn't contradict the body**, and every derived figure recomputed against a set of invariants.
11. **Deliverable.** **Built, not hand-assembled** — content goes into HTML fragments, structure into a spec, and `build_report.py` puts them together:

    ```bash
    python references/scripts/build_report.py --spec trip.spec.json --out report.html
    python references/scripts/check_report.py report.html
    ```

    The builder owns every heading, strips bold from identity cells, and injects the map links, so those rules hold without being remembered. The spec's `aliases` map lets a table say what a reader would say — "Thornbury" — while the pin resolves from the name it was verified under, "Thornbury Castle"; without it the cell just goes unlinked. Base-city names are excluded from linkable places automatically, since a base already carries its link once in its group's first heading.

    Published as an artifact **grouped by location**, with a sticky rail on desktop and a floating menu on mobile, wide scrolling matrices, a critical-and-time-sensitive panel on top, a booking checklist ordered by deadline, and an explicit list of what couldn't be verified.

## Usage tips

- **Use the gate.** The outline you get at Phase 4 is cheap to change and expensive to change later. Drop places, add places, move days — that is what it is for.
- **Say so if your itinerary is already fixed.** The recon phase is skipped entirely and you go straight to preferences, which saves a wave of agents.
- **Pick the split with the agent count in front of you.** Exhaustive on a four-city trip is twenty-seven tracks across five waves. Sometimes that's right; it should be a decision rather than a default.
- **Answer the sleeping-arrangements question carefully.** A group of adults is not couples unless you say so, and it decides the entire lodging budget — most markets sell "two rooms for four people" as two rooms with one bed each.
- **Name specific events you care about.** Sports fixtures, tournaments, concerts, festivals and classes have the earliest deadlines of anything in a trip and no interest category implies them — and anything you name by name gets its own section.
- **Expect `UNVERIFIED` cells and read them as signal.** They mark where a source was blocked and where five minutes of your own time is worth spending. A blank column would hide the same gap.
- **Re-running research updates the same artifact.** It won't mint a second link for the same trip.
- **The skill researches and prepares — it does not buy.** No purchases, payment details, account logins, or point transfers. Those stay with you.

## Design decisions worth knowing

A few things in here are deliberate and look odd without the reasoning:

- **Cheap research runs before expensive research, with a gate between them.** The recon phase costs a fraction of a full fan-out and answers the only question that matters early: is this the right shape? On the run this came from, a whole region was researched in depth and then cancelled, while a city dismissed in a single line later became a two-night base. Neither reversal was avoidable by researching *better* — only by researching *later*.
- **The deliverable is grouped by place, not by discipline.** Planning tomorrow in one city used to mean jumping between five discipline sections. Now each location carries its own transport, rooms, food and things to do, and country-wide material sits after them.
- **Every place name is its own map link, built from a `place_id`.** A name-only Maps query resolves to whichever branch Google prefers — which has already put the wrong branch of a four-branch restaurant and a café in the wrong neighbourhood into a published report. The map link and the booking link are different links and both are required.
- **Place names are never bolded in a matrix, and that is a bug fix rather than a style rule.** Written as `<b>Name</b>`, they defeated the link-injection pass entirely and whole sections shipped with no map links while every check reported clean. The link is the emphasis; bold is for the finding inside the cell.
- **Five options minimum per category, ten as a soft cap.** Four options is not a comparison — one closure leaves three. The cap is soft so a genuinely good find from a sweep isn't discarded to satisfy a number.
- **The venue check pulls far more than existence.** Opening hours with closure days, a real price band in local currency, rating with review count, step-free access, and whether a place is cash-only all come from the same pass — so they are columns rather than research debt. Accessibility in particular is the first source that answers the mobility question with anything but a guess.
- **Scripts are tested against a second, unrelated destination.** Passing for the trip in hand proves nothing about generality; it's the exact condition under which a hardcoded assumption survives. A control on another continent with a December-to-January window caught a year-range bug that silently returned twelve seasons when ten were asked for — and later caught an exonym bug, where a venue whose address carried its local-language city name was flagged against a hint written in English.
- **The report builder owns every heading, and that is load-bearing.** A content fragment that carries its own `<h2>` raises rather than rendering. This exists because a published report shipped the same heading twice: the content and the assembly each believed they owned it, and neither could see the other. Ownership has to sit in exactly one place — and when the guard was added, the very first build failed on exactly that section.
- **`lib/` is imported, `scripts/` is run.** Shared logic lives in one module rather than being copied between tools. The currency symbol map had already existed in two files printing two different things for the same price, which is the whole argument.
- **No machine output reaches the reader.** API enums, field names, status codes, nulls and ISO currency codes are all translated, and `check_report.py` fails the build on a hit. A published report once shipped eighteen cells reading `PRICE_LEVEL_MODERATE` — nothing factually wrong, just an enum printed into a human document.
- **The test suite is a regression log, not a formality.** Every case in it is a defect that shipped: a currency range printed with mixed precision, a bolded name that defeated the map-link injector, a section heading emitted twice, an ISO code where a symbol belonged. Tests written *after* a bug is found are the ones that stay true, because each one has a real failure behind it rather than a guess about what might break.
- **Waves, not one big fan-out.** The `WebSearch` budget is shared across sibling agents. Dispatching seventeen at once exhausted it in four minutes and killed fourteen of them.
- **Food runs on the expensive model.** It looks like list-building; it fails by fabricating. Any track emitting links and addresses at volume gets the careful tier.
- **Agents never hold an API key, and never compute.** The orchestrator calls and passes results down, so no credential reaches a subagent prompt or the transcript. The same boundary covers arithmetic: agents have no shell, so anything aggregated over many records is orchestrator work. Agents return *where the raw series lives*; the synthesis derives the number and publishes the method.
- **Statistics are computed over the trip window, not the calendar month.** Published normals, price bands and crowd levels are binned by month, and a trip rarely occupies one. On the run this rule came from, monthly climate normals overstated the actual dates by 2.4–3.2 °C across three cities — an error no amount of better searching would have caught, because nobody publishes the number the trip needs.
- **Medians and tail frequencies, not means.** For anything with rare extreme events, the average describes no actual year. "One year in five loses a day to unusable weather" is something you can plan against; an average rainfall figure isn't.
- **Rejected options stay visible, struck through.** Silently deleting one means you rediscover it on a booking site later with no idea it was already ruled out.
- **Every matrix column renders, even when empty.** A dropped column and an empty one look identical to the writer and completely different to the reader — one hides that nobody checked, the other says so.
- **Every deliverable section is named in advance, and every track has a destination.** Sections invented per-run are sections that can quietly fail to exist — which is exactly how a weather section shipped as three rows and an entry table never shipped at all.
- **The profile stores lessons, not just preferences.** A "booking rules learned the hard way" section carries cross-trip corrections — the kind of mistake that is obvious in hindsight and invisible the next time without a note.
- **Token discipline is written down because the costs are invisible.** Three rules, all from measurement rather than intuition: **read only the track's own brief** (`agent-briefs.md` is ~19k tokens; one brief is under 2k), **never read the finished report whole** (a real one is ~57k tokens — query it with a script instead), and **cap what agents return** (one run's returns ran 80k–120k tokens each, much of it notes restating the table above them).
- **The verification script ships with the skill.** `references/scripts/check_report.py` implements the pre-publish checks rather than leaving them aspirational — and its own failures are kept in the header as a warning. It once confidently flagged five correct cells as wrong, so **verify a failure against the source before "fixing" the document to satisfy the script.** It also spent most of its life matching a literal `<table>`, which meant **every table with a `class` attribute was silently skipped** while the checks reported `ok`. A check that passes because it never ran is worse than no check, because it gets trusted.
- **The compute scripts take their destination at run time.** Nothing in `references/scripts/` hardcodes a place, a currency, a date window or a path — a script you have to edit to point at a new country is not reusable, and this skill's whole premise is that it works anywhere. The same rule caught a shipped file with a full home directory baked into it, which would have failed for every other user and leaked a username into a public repo.
- **A dead agent gets resumed, not re-dispatched.** It picks up from its own transcript with partial findings intact. On one run all four died at once and two were holding real work; re-dispatching would have paid for the same research twice.

---

## Related

- **[agents-claude](https://github.com/wrobelsec/agents-claude)** — the required `travel-researcher` and `travel-scout` agents.
- **[agent-skills-claude](https://github.com/wrobelsec/agent-skills-claude)** — this repo's root.
