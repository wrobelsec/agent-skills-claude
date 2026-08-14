# travel-agent

Full-service travel planning for [Claude Code](https://claude.com/claude-code). It researches a trip live — flights, trains, lodging, food, excursions, entry rules, law, points — across operators' own sites, forums, and local-language sources, then builds comparison matrices and a day-by-day itinerary, and publishes the lot as a navigable artifact.

The output is a **decision document, not a brochure.** Every row carries the link you'd act on, every matrix ends with a pick and the reasoning, and anything that couldn't be confirmed says `UNVERIFIED` rather than quietly disappearing.

---

## ⚠️ Requires two agents

This skill does not work on its own. It dispatches two custom subagents by name for every research track:

- **`travel-researcher`** (Sonnet) — flights, lodging, food, day trips, entry and health, points, law, fare rules
- **`travel-scout`** (Haiku) — ground transport, experiences, community sentiment, language

Install them from **[agents-claude](https://github.com/wrobelsec/agents-claude)**:

```bash
git clone https://github.com/wrobelsec/agents-claude.git ~/.claude/agents
```

Then start Claude Code and confirm both appear in the available agent list. They carry the anti-fabrication rules, blocked-source ladder, API-first source list, budget-triage protocol, and the **gather-don't-compute boundary** that the research depends on — the skill's briefs assume those are already in force and don't restate them.

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
- **The two agents above.** Non-negotiable.
- **`WebSearch` and `WebFetch`** in the session.
- **Browser tools** optional but genuinely useful — many booking engines and some official sites are JS-rendered and return nothing to a plain fetcher.
- **No API keys needed to start.** The skill uses free keyless endpoints for commodity facts (geocoding, daylight, holidays, weather, FX) and works fully without any signup.

### Optional API keys

Four country-agnostic keyed APIs meaningfully improve two things scraping handles badly — **flight fares** (meta-search often refuses multi-city queries outright) and **venue hours and closure status** (the commonest way a food or excursion pick goes stale). Setup instructions, the free-tier caveats, and the security tradeoff are in **[agents-claude → travel/README.md](https://github.com/wrobelsec/agents-claude/blob/main/travel/README.md#optional-api-keys)**, since the agents are what actually call them.

Short version: Amadeus for fares, Google Places for venue data, Geoapify or LocationIQ for geocoding at volume, Sherpa as an entry-requirements cross-check. Keys go in the `env` block of `~/.claude/settings.json`. **Every one is optional and a missing key degrades gracefully** — the affected track falls back to normal research and says so in its findings.

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
| **`references/deliverable.md`** | The **canonical section set and rail grouping**, the map of which track fills which section, the report structure section by section, and the publishing rules — navigation, wide-table layout, theme handling, the pre-publish arithmetic check, what must never be silently dropped. |
| **`references/profile-template.md`** | Schema for `traveler-profile.md`, and the rules for maintaining it. |
| **`traveler-profile.md`** | **Your** stored preferences — home airports, passport, loyalty programs, sleeping arrangements, standing preferences, model assignment, trip history. Written on first run, updated after. **Gitignored** — it's personal and stays local. |

---

## How a run goes

1. **Intake.** One gate round (intake style, research depth, model assignment), then trip essentials. Asks about **date flexibility**, **sleeping arrangements**, and **what you specifically want to do** — because broad interest categories never surface the things with the longest lead times.
2. **API discovery.** Scouts what structured data exists for this destination, fetches current rate limits live, and asks whether you want to supply keys, stay keyless, or consider paid options.
3. **Pre-fetch.** Anything knowable before dispatch — fares for the routes in scope, entry rules, coordinates, holidays, climate normals, the dated FX rate — is fetched and folded into the briefs as results, with caveats intact.
4. **Research fan-out.** Twelve tracks dispatched to the two agents **in waves of 4–6**, ordered so air and entry/health land first. Each brief names **where its findings land** in the finished report.
5. **Verification.** What the agents found gets machine-checked — every coordinate geocoded, every venue's `business_status` and hours confirmed. One consistent standard rather than twelve, and **the point where a fabricated row gets caught**: a venue name that won't resolve is the tell.
6. **Computation.** The figures nobody publishes in the form the trip needs get derived here — conditions over the exact travel dates rather than the calendar month, event frequencies rather than averages, daylight at each base, pass break-evens against the real itinerary. Agents have no shell, so this is orchestrator work by construction.
7. **Synthesis.** Matrices built to spec, contradictions between tracks surfaced rather than averaged away, every matrix closed with a pick. Derived arithmetic is recomputed and checked against a set of invariants before anything ships.
8. **Deliverable.** Published as an artifact with a sticky section rail, wide scrolling matrices, a risk register, a booking checklist ordered by deadline, and an explicit list of what couldn't be verified.

## Usage tips

- **Choose `exhaustive` depth for multi-city trips.** It splits tracks per city, which is where per-destination detail actually comes from.
- **Answer the sleeping-arrangements question carefully.** A group of adults is not couples unless you say so, and it decides the entire lodging budget — most markets sell "two rooms for four people" as two rooms with one bed each.
- **Name specific events you care about.** Sports fixtures, tournaments, concerts, festivals and classes have the earliest deadlines of anything in a trip and no interest category implies them.
- **Expect `UNVERIFIED` cells and read them as signal.** They mark where a source was blocked and where five minutes of your own time is worth spending. A blank column would hide the same gap.
- **Re-running research updates the same artifact.** It won't mint a second link for the same trip.
- **The skill researches and prepares — it does not buy.** No purchases, payment details, account logins, or point transfers. Those stay with you.

## Design decisions worth knowing

A few things in here are deliberate and look odd without the reasoning:

- **Waves, not one big fan-out.** The `WebSearch` budget is shared across sibling agents. Dispatching seventeen at once exhausted it in four minutes and killed fourteen of them.
- **Food runs on the expensive model.** It looks like list-building; it fails by fabricating. Any track emitting links and addresses at volume gets the careful tier.
- **Agents never hold an API key, and never compute.** The orchestrator calls and passes results down, so no credential reaches a subagent prompt or the transcript. The same boundary covers arithmetic: agents have no shell, so anything aggregated over many records is orchestrator work. Agents return *where the raw series lives*; the synthesis derives the number and publishes the method.
- **Statistics are computed over the trip window, not the calendar month.** Published normals, price bands and crowd levels are binned by month, and a trip rarely occupies one. On the run this rule came from, monthly climate normals overstated the actual dates by 2.4–3.2 °C across three cities — an error no amount of better searching would have caught, because nobody publishes the number the trip needs.
- **Medians and tail frequencies, not means.** For anything with rare extreme events, the average describes no actual year. "One year in five loses a day to unusable weather" is something you can plan against; an average rainfall figure isn't.
- **Rejected options stay visible, struck through.** Silently deleting one means you rediscover it on a booking site later with no idea it was already ruled out.
- **Every matrix column renders, even when empty.** A dropped column and an empty one look identical to the writer and completely different to the reader — one hides that nobody checked, the other says so.
- **Every deliverable section is named in advance, and every track has a destination.** Sections invented per-run are sections that can quietly fail to exist — which is exactly how a weather section shipped as three rows and an entry table never shipped at all.
- **The profile stores lessons, not just preferences.** A "booking rules learned the hard way" section carries cross-trip corrections — the kind of mistake that is obvious in hindsight and invisible the next time without a note.

---

## Related

- **[agents-claude](https://github.com/wrobelsec/agents-claude)** — the required `travel-researcher` and `travel-scout` agents.
- **[agent-skills-claude](https://github.com/wrobelsec/agent-skills-claude)** — this repo's root.
