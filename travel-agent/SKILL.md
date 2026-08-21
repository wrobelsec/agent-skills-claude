---
name: travel-agent
description: Full-service travel planning — live-researches flights, trains, driving, lodging, excursions, food, festivals, and local spots across travel sites, Reddit/forums, blogs, and direct operator sites, then builds comparison matrices and a day-by-day itinerary. Use when the user is planning a trip, comparing destinations or routes, asking where to stay or eat or fly, weighing layovers or rail-vs-air, working out points versus cash, or wants an itinerary built.
---

# Travel agent

Plan trips the way a good human agent does: research everything live, from the actual operators and from people who have been there, then lay the options side by side so the user can decide. The output is a decision-making document, not a brochure.

The single biggest failure mode is answering from memory — everything in the deliverable traces to a page fetched **this session** (§2).

## The shape of a run

**Cheap and broad first, expensive and deep only after the user has narrowed it.** The phases below are ordered so that no expensive research commits to a destination the user has not yet confirmed.

```
0  Tool preflight + test suite   run_tests.py, before anything else
1  Intake                        incl. a record per traveller
2  API discovery + destination probe
3  Recon fan-out                 SKIPPED when the itinerary is already set
4  Outline → publish → gate      the artifact is minted here
5  Preferences round             what they enjoy → profile
6  Deep research                 location-scoped; the split is asked, not assumed
7  Synthesis → update the same artifact
```

**Phase 4 is a hard gate.** Nothing in Phase 6 dispatches until the user has confirmed which locations stay and roughly how long in each. This exists because a live run researched an entire region in depth — lodging, food, day trips, climate, passes — and the user then cancelled it outright, while a place that had been dismissed in one line became a two-night base. Both reversals were cheap to avoid and expensive to absorb.

## 0. Tool preflight and the test suite

`WebSearch` and `WebFetch` are frequently deferred. Load them before anything else:

```
ToolSearch(query: "select:WebSearch,WebFetch", max_results: 5)
```

When a site blocks plain fetches — Google Flights, many airline and OTA sites — fall back to `mcp__Claude_Browser__*` (`preview_start` with a `url`, then `get_page_text`). Use `mcp__claude-in-chrome__*` only when the user's own logged-in sessions are genuinely needed, and ask first.

### Then run the test suite

```bash
python references/scripts/run_tests.py --live
```

Offline it takes about a second and needs no key; `--live` adds a reachability check on every endpoint the skill depends on. **Do this at the start of every run.** The alternative is discovering a dead provider halfway through synthesis, after the budget is spent.

That is not hypothetical. Over this skill's life an FX host began returning 403s mid-run, a daylight API started refusing fetchers outright, a flight API was decommissioned between one run and the next, and a climate endpoint began rate-limiting under ordinary use. **None of them announced it** — each surfaced as a confusing failure inside unrelated work.

The suite also guards the transformations that have broken in published output: currency formatting, machine-value translation, link injection, and heading ownership. Those run offline against fabricated fixtures.

**Once the destination is known**, re-run it with the probe — §1's API-discovery step. Exit code is the number of failures, so it can gate a run.

**A skipped test is not a failed one.** Absent keys skip with an explanation, because this skill degrades to keyless research rather than stopping.

## 1. Intake

Read `traveler-profile.md` in this skill's directory first. If it does not exist, this is a **first run**.

Then ask **one gate round** via `AskUserQuestion` before any real questioning, so there is a single interruption before the path forks. Bundle:

1. **Intake style** — quick round (one batch of essentials, then straight to research) or in-depth interview (a few rounds covering everything first).
2. **Research depth** — quick / standard / exhaustive (see §3).
3. **Subagent model** — pre-filled from the profile. Asked fresh on a first run, and whenever the available model lineup has changed since the stored choice (see §4).

On a first run, follow the gate round with the two profile questions — loyalty programs and the destination wishlist (§6). On later runs, show the stored values back and ask only whether anything changed.

**Quick path** — one more batch: **how flexible the dates are** (see below), budget band and what it covers, **party size and sleeping arrangements**, pace and interests. Everything else comes from the profile or from a default, and every assumption gets stated in the deliverable with an offer to re-run that leg if it is wrong.

**Sleeping arrangements are a distinct question, and headcount does not answer it.** Ask how many separate beds the party needs and who, if anyone, shares. Four adults travelling together are not two couples unless they say so, and the answer decides the entire lodging budget — a "two rooms for four people" search returns rooms holding one bed each across most of the world. Missing this on a live run invalidated every lodging price in three cities, and the traveller caught it after the plan was published.

### Build a record for each traveller, not just a headcount

A party size tells you almost nothing about what is bookable, reachable, or safe. Ask, **per traveller**:

- **A first name or nickname** — the handle this person is referred to by from now on
- **Age or age range** — gates rail passes, discounts, licence minimums, and admission tiers
- **Mobility or disability considerations** — gates lodging (lifts, step-free access), day trips, and how much walking a day can hold
- **Health concerns** — gates the health section, the air-quality finding, the food verdict, and altitude
- **Dietary needs**
- **Passport nationality** — the entry table is one row per nationality × country and must never be generalized across a party

Then **offer to save each traveller to the profile, asked per person rather than as a blanket yes.** The handle is the point: a later run can open with *"same four as last time — Sam, Alex, Jo and Rae?"* instead of re-interrogating from scratch. Travellers are stored as reusable records and referenced by handle; the trip stores the list of handles it applies to.

Where a traveller declines to be stored, plan for them normally this run and keep nothing.

**What they want to *do* is asked later, in Phase 5** — not here. At intake the destinations are not yet settled, so the answers come back generic and have to be asked again. See §5.

**Date flexibility is a distinct question, always asked.** Not "what are your dates" but *how movable are they*, which changes what the research is for:

- **Locked to an event** — price ±1–2 days anyway, so the cost of the fixed dates is visible. Sometimes it is zero, which is worth knowing.
- **Flexible by days** — scan the surrounding window; report what the flexibility is worth in money and whether it dodges a holiday, closure, or festival crush.
- **Flexible by weeks, or open** — then **the best time to visit is part of the job, not a footnote.** Agent H builds a month-by-month picture (weather, seasonal pricing, crowds, what is only open or only happening then, and the months locals themselves name as best), and the deliverable leads with a dated recommended window compared against whatever the user originally proposed. A trip moved three weeks is often a materially better trip for less money — and that finding is worthless once the flights are booked.

**In-depth path** — a few rounds adding: destination shortlist or "surprise me", passport nationality per traveller, mobility and dietary needs, appetite for long layovers and multi-city routing, willingness to drive abroad, hotel vs. whole-home preference, trip themes, and hard avoids. Write the durable answers back to the profile.

**Currency** is asked once and stored. Every price appears in **both** the local and the user's preferred currency — `¥18,000 (~$118)` — with the FX rate and its lookup date stated once at the top. A rate quoted without a date is worthless a month later.

### API discovery — after intake, before the fan-out

Some of what this skill scrapes is structured data behind an API, and the API version cannot be misread or invented. **Which APIs exist is a per-destination question, not a fixed list** — hardcoding a national rail programme into a skill meant for anywhere is how a source list goes stale.

A short scouting pass, before any research agent is dispatched:

1. **Find what exists for this destination.** Aim at the categories scraping handles worst — **fares, lodging rates, place hours and status, transit timetables** — plus whatever the destination happens to run: a national rail open-data programme, a tourism-board API, a municipal open-data portal. The keyless commodity endpoints (geocoding, daylight, holidays, weather, FX) are already in [source-map.md](references/source-map.md) and need no discovery.
2. **Fetch each candidate's current rate limit and quota live.** Never carry these between runs. Free tiers get cut, endpoints move hosts, and services break — one planning pass found a currency API had changed host and a widely-recommended advisory API was serving a dead TLS certificate.
3. **Put it to the user in one round**, then
4. **Run the test suite against *this destination*, once, before any dispatch.** Run `references/scripts/run_tests.py` with a real address in the destination's own script and a bounding box. Check `references/api-compatibility.md` first — if the destination already has a dated row, use it and re-test only if it is stale.

   **A key that authenticates is not a key that works here.** The failure this catches is not an error: a geocoder returned HTTP 200 with coordinates in **the wrong country** for local-script addresses — three different wrong countries across three cities on one run — while a Latin-script control resolved within 0.006°. Nothing in the response flagged it. **A confident wrong answer survives review in a way a blank never does**, so the only way to catch it is to check the answer against something already known true — per destination, because that is the axis it varies on.

   **Record the outcome in `api-compatibility.md` with the date**, pass or fail. Then pass the working set into the briefs and note the excluded ones, so no agent leans on a provider already known to be wrong here.

5. **Pass the resolved list into every brief** — endpoint, auth shape, and the **live rate limit**, so agents pace against a real number instead of guessing. Same problem as the shared search budget, same treatment.

**The consent question — three tiers, with the reasoning stated rather than assumed:**

- **Keyless only** — no signup, works immediately. Covers the commodity layer; leaves fares, hours and timetables to scraping.
- **Free-tier keyed** — a signup or two, and this is where the expensive failures get fixed at the root. Name them concretely: on a live run, a multi-city fare **never resolved at all**, leaving a $2,287–$3,658 spread in the flight budget, and a food track **fabricated its sources** largely because there was no structured way to confirm an address or whether a venue had closed.
- **Paid too** — if they're open to spending, the same pass looks for commercial options and reports cost against what each unlocks.

**Flag the friction at ask time**, because it's what makes people abandon setup halfway: some free tiers **require billing details on file** even to use the free allowance, and some serve **test or cached data rather than live production data** — which trades one confidently-wrong number for another unless it's labelled.

**Keys** go in the `env` block of `~/.claude/settings.json`. That is a plain-text file on disk, the same caveat that governs the traveler profile.

### You make the keyed calls and the computations, not the agents

**Research agents never hold a credential.** They have no shell and no key, deliberately — a key passed into a subagent prompt lands in the transcript, and there is no reason to put it there. You hold the keys and call on their behalf, in three phases:

**Before dispatch — pre-fetch what is knowable in advance** and put the *results* into the briefs: fares for the routes in scope, entry requirements for the passport-and-destination pairs, coordinates for the cities and neighbourhoods, holidays, climate normals, the dated FX rate. Carry any caveat with the data rather than stripping it — free-tier flight data that is partly cached answers the structural question but not the exact fare, and an agent that isn't told that will quote it as gospel.

**After return — verify what the agents found.** Anything discovered mid-research can't be pre-fetched, so it gets checked during synthesis: geocode every coordinate, run `business_status` on every venue, confirm opening hours and closure days. This is better than having each agent verify its own work, for two reasons: it applies one consistent standard instead of twelve, and it is the point where a fabricated row actually gets caught — a venue name that won't resolve is the tell.

**Alongside both — compute what cannot be looked up.** Some of the most decision-relevant numbers in a plan are not published anywhere in the form the trip needs them: conditions over *these exact dates* rather than the calendar month, the frequency of a disruptive event rather than its average, daylight at the start and end of the stay, a pass break-even against this specific itinerary. These are statistics over bulk records, and **you have a shell where the agents do not.** Fetch the raw series, compute over it, and publish with the method in the caption.

A published summary is a fallback, not the goal. Where the underlying records are reachable, **derive the figure and say how** — it is scoped to the actual question, it carries its own method, and it cannot be mis-extracted from someone else's table. On a live run the published monthly climate normals overstated the trip's temperatures by 2.4–3.2 °C, and the corrected figures came from computing over daily records for the actual travel window; no amount of better searching would have found them, because nobody publishes that number.

Brief the agents accordingly: **return names and addresses exactly as the source gives them**, so a lookup can resolve them, and never invent a coordinate or an opening time, because those are the fields that get machine-checked. And where a track needs a statistic over bulk data, **the brief asks for the location of the raw series** — endpoint, parameters, coverage — rather than for a pre-computed summary. Identifying the source is agent work; the arithmetic is not.

**Record which APIs the user configured and which they declined** in `traveler-profile.md`, so later runs don't re-ask — the same re-confirm-don't-re-interrogate rule that already governs loyalty programs.

**Degrade gracefully, always.** Every API call site checks for its key and **falls back to the normal research path when it's absent**, noting in the findings that it did. The skill must work unchanged on a machine with no keys configured: a missing key is a quality reduction, never an error.

### Script conventions

The scripts in `references/scripts/` do the fetching and the arithmetic. Every rule below is written down because it has already gone wrong.

- **Never hardcode an absolute path.** Relative by default, an environment variable to override, and `~` expanded at runtime rather than written into source. `run_tests.py` shipped with a full home directory baked in — it would have failed for every other user on earth, and it put a username into a public repo.
- **Never hardcode a key value, and never print one.** Keys come from the environment or the settings file. Report `set` / `working` / `invalid` — never the string. A key echoed into a terminal is a key in a transcript.

- **Every provider gets exactly one client in `lib/`, and nothing calls a provider any other way** — keyed or keyless. `gplaces` · `serpapi` · `openmeteo` · `fxrates`, each declaring a `PROVIDER` tag that the counter and the ceiling key on. Two scripts once called the same host independently with their own endpoints and their own backoff; a change landed in one and not the other, and no single place knew how much traffic the skill sent. `tests/test_clients.py` fails the build if a script reintroduces a raw URL or imports `get`/`post`.

- **Keyless is not unmetered.** Open-Meteo 429s under rapid calls and Nominatim asks for about one request a second. Those stop work part-way exactly like a spent key, and a gap from a rate limit looks identical to absent data — so spacing lives in `quota.throttle`, keyed per provider by `<PROVIDER>_MIN_INTERVAL`. Backing off *after* a 429 still costs the failed request and several behind it in a fan-out; spacing them costs only wall time.

- **Keyed calls never bypass their client.** The client is where the quota check, the spend counter and the cache live, so a call that bypasses it is a call nobody is counting. This is not hypothetical: one exploratory query written as a raw `get()` spent real quota and stayed invisible to the local counter, which is exactly the drift that makes a budget report untrustworthy.

- **Check the meter before spending it, every run.** `run_tests.py` prints what each key has left before a single test runs. Metered providers are read from the provider itself — SerpApi's `/account` is free and authoritative. Unmetered ones are counted locally against `<PROVIDER>_MONTHLY_LIMIT`, and a local count is a floor on real usage, never a measurement: it cannot see another machine. Both are labelled so nobody mistakes one for the other.

- **Refuse a batch that would exceed the ceiling, before starting it.** A sweep that dies half-way is worse than one that never began — the unverified half looks identical to venues that genuinely failed to resolve, and that difference decides whether a row ships. `quota.check(provider, need=len(batch))` is called with the whole batch size for this reason.

- **A test suite must never consume metered quota.** Reading a meter is free; performing a search to prove searches work would exhaust a small plan in a handful of runs. The live tier reads `/account` and asserts headroom; it does not buy anything.
- **Inputs and outputs are country- and location-agnostic.** No coordinates, city names, currencies, or date windows in the source. All of it arrives at run time, as arguments or as a JSON file passed by path. **A script you have to edit to point at a new country is not reusable**, and this skill's entire premise is that it works anywhere.
- **Test every script against a second, unrelated destination — not just the one being researched.** Passing for the trip in hand proves nothing about generality; it is exactly the condition under which a hardcoded assumption survives unnoticed. Pick a control on another continent, in another currency, with a different alphabet, and where possible a window that crosses a year boundary. Doing this caught a year-range bug that silently returned twelve seasons when ten were requested, and it only appeared because the control used a December-to-January window.

### Which place names may appear in the skill at all

There is a real line here and it gets crossed in both directions.

**Not allowed — anything tied to one particular trip.** Worked examples, docstring samples, spec templates, stopword lists and the narrative evidence behind a rule all use **fabricated or generic placeholders**: `<City>`, `<Country>`, `<LOCAL>`, `<YYYY-MM-DD>`. A rule justified by *"monthly normals overstated the window by 2.4–3.2 °C across three cities"* keeps its measurement and drops the place — the number was the evidence; the city name never was.

Beyond tidiness, hardcoding one trip's places **breaks silently on the next trip**. A stopword list naming one country's cities filtered nothing at all once the destination changed, and a lodging check keyed to one itinerary's headings stopped running the moment a heading was reworded. Neither failed loudly.

**Allowed, and worth keeping — world knowledge that helps research anywhere.** `source-map.md` naming the dominant local review platform per country, the luggage-forwarding operators that exist in one market and not another, which countries restrict which medications, where short-term rentals are licensed, which languages carry a formality register. That is not an example of a trip; it is the reference data that lets an agent find *local* sources instead of defaulting to the international aggregator. Stripping it would make the skill worse at every destination, including the ones it names.

**The test:** *does this name appear because of the trip we happened to plan, or because a researcher going there needs to know it?* The first is a leak. The second is the point.

**Two files are exempt by design.** `api-compatibility.md` is a dated per-destination failure log — recording that a provider returns the wrong country for one language's addresses is its entire function. And `traveler-profile.md` holds the user's own trips and is gitignored.

### Keep the READMEs current

**Any material change to this skill or to the agents updates the READMEs in the same pass.** Four files: `skills/README.md`, `skills/travel-agent/README.md`, `agents/README.md`, `agents/travel/README.md`.

Material means: a new or removed agent, a change to the phase flow, a new script or reference file, a changed requirement or install step, a new API field the output depends on, or a rule a user would be surprised by. Cosmetic edits do not count.

This is written down because documentation drifts silently and the cost lands on someone else: a README promising two agents when the skill dispatches three sends a new user into a failure with no diagnosis. **The README is part of the change, not a follow-up to it.**

`TRIP_OUT` sets the output directory (default: cwd) and `CLAUDE_SETTINGS` the settings file. Locations are passed as a JSON file — `{"<place>": {"lat": …, "lon": …, "elev_m": …}}` — where `elev_m` is the published elevation of the real place, supplied so the climate script can prove a reading describes the place you named rather than a grid cell 25 km away.

## 2. Research rules

**Read [research-rules.md](references/research-rules.md) before spawning agents.** It holds the full standard — sourcing, money, time, health and safety, legal and cultural exposure, transport, and how findings get reported — and every agent brief is written against it. Re-read it during synthesis when a finding looks too clean.

Three that decide whether the whole thing is worth anything, so they live here too:

**Live only.** Every price, schedule, opening hour, and closure comes from a search or fetch performed **this session**, carried with its source URL and the date accessed. Never fill a gap from training data. A confidently stated stale price is worse than no price, because the user acts on it.

**`UNVERIFIED` is a valid answer and a guess never is.** Anything unconfirmed gets labeled with a note on what you tried. An honest hole tells the user where to spend their own five minutes; an invention costs them a booking. Never invent flight numbers, addresses, hours, or prices — and in the health, entry, and legal sections an invented fact is dangerous, not merely unhelpful.

**Authority hierarchy for anything with consequences.** Entry rules, vaccination requirements, transit legality, law: the destination government's own page is the authority, the traveller's foreign ministry is the cross-check. Never rest a consequential claim on a travel blog, and never trust a summary that does not name the nationality it applies to.

## 3. Recon, the gate, then depth

### Phase 3 — Recon fan-out

**Skip this phase entirely when the user arrives with a set itinerary.** If the destinations, their order and the dates are already decided, recon has nothing left to decide and its only effect is delay — go straight to Phase 5 and **say that recon was skipped and why**. Run it when the shape is open, partly specified, or when the user asks what else is worth adding.

Otherwise dispatch, in one wave:

- **One `travel-recon` agent per named destination.** Each covers how to reach that place from the origin and from it to every other named destination, a ranked list of top things to do, and what lies nearby or in between. **Bands not fares, names not opening hours, no fine print.**
- **One `travel-researcher` as the safety agent**, once for the whole trip. It stays on the careful tier because advisories, outbreaks and law are consequence-bearing, and a confidently wrong answer here is dangerous rather than merely slow. It covers advisories with their **actual reasoning** and whether they apply to the itinerary or a region nobody will see; instability, conflict and charged dates; crime aimed at visitors; **disease outbreaks with case numbers, region and date**; **natural-disaster and severe-weather seasons** — hurricane, typhoon, tornado, monsoon, wildfire, flood, earthquake, volcanic — and whether the window sits inside one; plus announced strikes.

Recon does **not** touch lodging, food depth, health beyond outbreaks, points, fare rules, language, or law. Those are Phase 6 and only for the places that survive.

`travel-recon` exists as its own agent type rather than a briefed `travel-researcher` for a specific reason: **every other agent here is built to chase detail, and one told to be shallow will drift back into it.** The standing rules that make recon cheap — stop at the first good answer, bands not figures, hard row caps — belong in the agent definition, the same way the anti-fabrication rules do.

### Phase 4 — Outline, publish, and the gate

Build a rough outline: the shape, plausible days per location, how the legs connect, what recon suggests adding or dropping. **Publish it as the artifact immediately**, with the *Critical and time-sensitive* section already on top, and **update that same URL for the rest of the trip**.

Then put it back to the user: which locations stay, which drop, how long in each, dates narrowed.

**Nothing in Phase 6 dispatches until that is answered.** This is the whole point of the phase ordering; running lodging research against an unconfirmed destination list is exactly the waste this structure exists to prevent.

### Phase 5 — Preferences

Now ask what they actually want to **do** — after the destinations are settled, so the answers are about real places.

Broad interest categories never surface the things that need booking months ahead. A traveller who ticks "cities and modern culture" may also want a **sports fixture, a concert, a festival, a cooking class, a distillery tour, a market at dawn, a museum exhibition, a track day, a tee time** — and none of that follows from the category. On a live run the traveller had to name sumo, baseball and concerts explicitly after research was underway; it then turned out the autumn sumo tour passed through their base city on two days of their stay and a home playoff game was twenty minutes away. Both ticket windows had already opened.

Ask directly — *is there anything specific you want to see or do?* — then check the window for those categories whether or not they name any, since a fixture list is cheap to check and impossible to recover once sold out.

**Write the answers to `traveler-profile.md`** under *Activities and experiences*, so later runs start from them. **Anything named as a must-see gets its own subsection in the deliverable**, however small — a named must-see buried in a general table is the failure this prevents.

### Phase 6 — Deep research

**Ask which split to run, every time. Do not infer it from a stored depth.** Present the three shapes with their real agent counts against *this* trip's location count, because the count is the decision the user is actually making:

| Split | Per location | Global | Example at 4 locations |
|---|---|---|---|
| **Quick** | 1 place agent | A, H, J | 4 + 3 = **7 tracks** |
| **Standard** | 1 lodging (careful tier) + 1 place | all 7 | 8 + 7 = **15 tracks** |
| **Exhaustive** | all 5 | all 7 | 20 + 7 = **27 tracks, five waves** |

**Two global tracks are conditional**, because they are wasted on trips they don't apply to:

- **K** runs whenever the itinerary connects or spans more than one carrier — exactly when ticket structure, interline baggage and compensation regime matter. Skipped on a simple non-stop return.
- **L** runs whenever the destination's main language is not one the traveller speaks, read from the profile.

When either is skipped, **say so and why**. A silently omitted track looks identical to one that found nothing.

### Dispatch — in waves, never all at once

**The `WebSearch` budget is shared across every sibling agent, and so is the session limit.** This is the most important operational fact in the skill and it is invisible until it bites. A run that dispatched seventeen agents in a single message exhausted the shared search pool in about four minutes, took the session limit down with it, and lost **fourteen of the seventeen** before any returned. Everything after that was recovery.

- **Cap concurrency at 4–6 agents in flight.** The cap is on the *total*, not per city — per-city splits multiply the count fast, and exhaustive depth on a three-city trip is well past a dozen tracks.
- **Dispatch in waves, ordered by what unblocks synthesis.** Air and entry/health first, since routing and lead-time constraints shape everything downstream. Then lodging and day trips. Then food, sentiment, points, law, language.
- **Give every brief an explicit search budget** — a stated number of `WebSearch` calls, scaled to how many agents are in flight — alongside its numbered priority list, so an agent running low knows what to drop rather than thinning everything. Agents respect a stated cap and invent their own when none is given.
- **G and K run after A returns.** Layover explorability and ticket structure both depend on which routings actually exist.
- **Read only the track's own brief.** `agent-briefs.md` is roughly **19,000 tokens**; a single track's brief is under 2,000. Locate the track's `## X —` heading and read from there — never load the whole file to construct one dispatch.
- **Pass down what is already known to be blocked.** Quote the relevant lines from `source-map.md` into the brief. On one run, four separate agents each independently rediscovered that carrier sites and the dominant restaurant platform refuse automated access, spending real budget to learn something already written down.
- **Take the return as field mappings, not prose.** State the fields, state a row budget, and require **one record per finding keyed to those fields** — no narrative, no summary paragraph, no restating the table underneath it. `## Notes` carries only what a field cannot: a contradiction between sources, a timing trap, a blocked host. **A note that paraphrases its own table should not exist.** Returns on one run ran 80,000–120,000 tokens each, most of it exactly that.
- **Take newly discovered blocks back.** `source-map.md` records the blocks already known and the briefs quote them — but a block found *mid-run* dies with the agent unless it is asked for. Require a `## Blocked` field: the host, what was wanted, and which failure category it fell into. **Relay it into the briefs of agents not yet dispatched, and queue it for `source-map.md` with the date.** On one run four agents each independently spent budget discovering the same two sites refuse automated access. Same discipline `api-compatibility.md` already applies to providers: an observation on a date, re-tested rather than inherited forever.

**When an agent dies mid-run, resume it rather than re-dispatching.** Send it a message instead of spawning a fresh one: it resumes from its own transcript with its partial findings intact. On one run all four agents died at once on an account limit, two of them holding real checkpointed progress — re-dispatching would have discarded it and paid for the same research twice. **State in the resume message that the search budget is reset**, and restate the top two or three priorities, because a resumed agent does not know why it stopped.

Spawn in the **background** as `travel-researcher` or `travel-scout` (§4), each with its brief from `references/agent-briefs.md`.

**Every brief names where its findings land** — the deliverable sections that track fills, from the map in `deliverable.md`. State it at dispatch rather than working it out at synthesis: a track with no named destination is a track whose findings get compressed into a paragraph and lost. Two need watching in particular. **F owns no section of its own** — its output feeds verdicts inside five other sections, so nothing looks thin when it returns nothing. **H feeds four sections plus the itinerary**, which is why it is the most under-delivered track here and why both known stub failures came from it.

**Per-location tracks — dispatched once for each location**, so each returns already scoped to the section it fills. The location is a parameter of the brief.

| | Track |
|---|---|
| **C** | **Lodging — hotels *and* homeshares, in one table on the same all-in basis.** Direct sites vs. aggregators; Airbnb, Vrbo, Booking's apartments and the local platform that actually dominates there. Neighborhood tradeoffs, shuttles, resort fees, cancellation, **neighborhood safety data**, and **off-platform reviews** — a 9.1 on an OTA regularly hides a bad block. **Amenities listed per property** — pool, A/C, lift, kitchen, laundry, parking, luggage hold — verified against recent reviews rather than the OTA checkbox, and **checked against each traveller's mobility record**. **In warm destinations, rank a usable pool above an equivalent property without one**, and confirm it is open on the actual dates. For homeshares also: fees spread over real nights, **short-term-rental legality and licence number**, late-arrival handling, and scam signals. |
| **D** | **Experiences.** Operators direct, GetYourGuide/Viator-class, official park and museum sites, timed entry and sell-out lead times, transport included in the tour. Plus **local festivals and seasonal events** in or near the window, **experiences unique to that place or climate**, and the **etiquette** around each. **Everything the user named as a must-see is covered here and gets its own deliverable subsection.** |
| **E** | **Food.** Must-try dishes and the specific places locals name. Markets, neighborhood spots, reservation lead times, Michelin/Bib/50Best against local consensus. **Street food treated as a tier, not a caveat**, gated on H's water and foodborne verdict — recommended properly where it's safe, with named precautions where they apply. |
| **F** | **Community sentiment, for this location.** Reddit, TripAdvisor/FlyerTalk/Rick Steves-class forums, travel blogs and YouTube itineraries, tier lists, overrated/underrated threads. |
| **G** | **Day trips and local ground.** Reachable towns and excursions from this base, local transit, and **what is genuinely walkable from the lodging** — measured from map data, not estimated. Owns this location's rows in the distance and travel-time matrix. |

**Global tracks — dispatched once for the whole trip.**

| | Track |
|---|---|
| **A** | **Air.** Google Flights, airline direct sites, flexible-date scans. Non-stop first, then one-stop. **Every fare class priced** — basic economy through business — with what each actually includes. |
| **B** | **Inter-city ground.** The connection graph between bases: rail operators direct, Rome2Rio/Omio-class aggregators, intercity bus, ferries, car rental with one-way fees and insurance/IDP rules, fuel and tolls. Also **luggage forwarding** (Japan's takkyubin, European door-to-door services, airport-to-hotel delivery, station lockers) — shipping bags ahead is what makes a rail day or a long layover actually workable. |
| **H** | **Entry, health and climate.** **Visa regime and application process per passport nationality** — official URL, cost, advertised vs. actual processing time, apply-by date — for the destination and every country transited. **Required and recommended vaccinations including those triggered by transit countries**, outbreak data with case numbers, malaria and altitude, **tap-water potability and a plain street-food verdict passed to agent E**, hospitals near each base, eSIM, transit passes, holidays, climate normals, packing and dress codes. **Air quality and pollution** — seasonal AQI, haze and burning seasons, and whether anyone's health record makes it decision-relevant. Plus **payments**: cash essential / recommended / optional, which card networks actually work (Amex and Discover get refused far more than holders expect), whether signature-only cards fail at unattended kiosks, and whether a local payment app is mandatory — and if so, **whether a visitor can even register**, since most require a local bank account or ID. When dates are flexible, the **best-time-to-visit analysis** by month. |
| **I** | **Points, rewards and discounts.** **Do not attempt to access award engines or loyalty portals.** They require login, block automated access, and personalise results, so scraping them yields nothing usable and looks like an access attempt. Instead: **list the programmes, their transfer partners, and published conversion ratios wherever that data is public**, note live transfer bonuses and their end dates, and mark live award pricing `UNVERIFIED` — the user checks it while logged in. Then everything flights and hotels leave out: **city passes with the break-even actually calculated**, railcards, association and club car-rental rates, operator-direct vs. marketplace pricing, museum free days, dining programs, shopping portals, and memberships the user may already hold. |
| **J** | **Customs, law, stability and self-protection.** Named local scams and how they run, tourist traps and what locals say instead, customs and traditions including tipping and haggling, the **laws that get travellers arrested or fined**, and **current political and local instability** — advisories with their real reasoning, conflict and unrest, elections and charged dates in the window, announced strikes, and seasonal hazards. Deepens whatever the Phase 3 safety agent surfaced rather than repeating it. |
| **K** | **Fare rules, passenger rights and airport mechanics.** Second wave. **One ticket or separate tickets** for each itinerary and what a missed connection then costs — the highest-value finding in the track. Which **compensation regime** governs (EU261/UK261/APPR/DOT) and what a delay is worth, schedule-change rights, whose **bag allowance** applies on multi-carrier tickets, terminal changes and whether security is re-cleared, and lounge access. |
| **L** | **Language and communication.** Languages actually spoken by region, **English adoption broken down by context** — front desk vs. pharmacy vs. police vs. rural — rather than as one useless number. Signage, romanization, and whether ticket machines have an English mode. Translation tools that work for *this* language pair and the offline packs to pre-download. Phrases worth learning, including allergy and medical phrasing. Plus the wariness list: register mistakes, where English changes the price quoted, gestures, directness, and emergency communication. |

At **Quick** and **Standard** splits, C/D/E/F/G collapse into fewer agents per location — see the table above. The brief still names every field, so collapsing agents never means dropping columns.

Agents return **field mappings plus a short notes block**, never narrative and never an itinerary. Synthesis is your job, not theirs.

## 4. Model policy

You — intake, synthesis, matrices, recommendations, the artifact — run on the latest flagship model. Research agents run cheaper, because their job is retrieval and structured reporting, not judgment about the trip as a whole.

**Two custom agent types carry the model and the standing rules**, so the per-track brief no longer has to restate them. They live in `.claude/agents/` and are dispatched by name rather than by passing `model` on the call:

| Agent type | Model | Used for | Why |
|---|---|---|---|
| **`travel-recon`** | `sonnet` | Phase 3, one per destination | Breadth, not depth — and the standing rules are the *inverse* of the other two: stop at the first good answer, bands not figures, never chase fine print. It runs on the careful tier despite being shallow because it emits place names that shape the whole trip, and the pass is short enough that the cost delta is small. |
| **`travel-researcher`** | `sonnet` | Phase 3 safety agent · A, C, E, G, H, I, J, K | Fine print is where money is lost and trouble starts — fare conditions, award restrictions, contradictory reviews, and for H/J/K vaccination rules, criminal law, and whether a ticket strands you. A confidently wrong answer here is far worse than a slow one. |
| **`travel-scout`** | `haiku` | B, D, F, L | Largely retrieval and list-building against named sources. Fast, cheap fan-out is the right trade. |

**E moved from the cheap tier to the careful one**, and the reason generalizes: **any track that emits links, addresses, or identifiers at volume runs on the more careful model, because its failure mode is fabrication rather than slowness.** On a live run, two of three food agents on the cheap tier produced sourcing failures — one invented a table of URLs and reused a single venue ID across two restaurants, another returned map pins in the wrong prefecture. The careful-tier re-run hit the same blocked site and reported the block honestly instead of filling the gap. That difference is worth the cost.

Both agent definitions carry the link rules, the blocked-source ladder, the API-first list, budget triage, the `UNVERIFIED` convention, and the both-currencies requirement. Keeping those in the agent rather than the prompt is deliberate: on the run above, the safety rules were only as reliable as remembering to paste them into all thirty-seven dispatches, and the one that shipped without them is the one that fabricated.

Store the assignment in the profile alongside the model lineup it was chosen against. Offer it pre-filled in the gate round every run. Ask **fresh** — with a short note on which of the now-available models suits which track — on a first run and whenever the lineup has changed, so the skill does not quietly pin itself to a superseded generation.

## 5. Synthesis

Build the matrices in `references/matrices.md`. Required set: flight options, mode comparison, whole-path, lodging (hotels and homeshares together), excursions, food, nearby/day-trip, **distances and travel times**, budget scenarios, points & booking-channel, **discounts and savings**, **climate and daylight**, and — when dates are flexible — **best time to visit**.

Seven further sections — entry, money, health, weather, language, rights, and law — take their columns from the **track briefs** rather than from `matrices.md`, and the same rule governs them: **if an agent returned a table, print a table.** That boundary is where columns have twice been lost, once reducing a mandated per-passport entry table to five prose bullets.

Every matrix ends with a one-line **recommendation and why**. A matrix without a pick is not a decision, it is homework.

**Verify the arithmetic before publishing.** Recompute every derived column — unit and currency conversions, per-person divisions, totals, stated deltas — and check the relations that must hold: per-person × people × nights against the total, legs against door-to-door, components against the budget rollup. This belongs in the same phase as verifying agent-returned venues and coordinates, for the same reason: one consistent check where the document is assembled. The both-currencies rule puts a derived column on every price in the document, so a hand-typed error here is a standing exposure rather than a rare one. The full list is in `deliverable.md` under Publishing.

**Every row ends in a link, and it is the operator's own** — flights, rooms, tables, tours, rentals, tickets. The reader acts from the row, not a bibliography. Where a cell compresses an intricate rule, add a **further-reading link to the authoritative text**: the summary orients, the link is the truth.

Also build a **risk register**, high in the deliverable rather than scattered through the detail. It carries **travel advisories** — the level, the *actual reasoning*, and whether it applies to the itinerary or to a region they'll never see — plus whatever could realistically disrupt this trip: strikes, charged dates, outbreaks, water and food risk, single points of failure, and any `UNVERIFIED` finding a decision rests on. Every entry carries a mitigation; a risk without a fix is just anxiety.

Where agents contradict each other, say so explicitly and give the reason to trust one over the other — recency, whether it is the operator's own page, whether it is one review or forty.

## 6. The traveler profile

`traveler-profile.md` in this skill's directory. Schema in `references/profile-template.md`. Read at the start of every run, written at the end of any run where something durable changed.

It holds: **a record per traveller**, keyed by handle — age or range, mobility, health concerns, dietary needs, passport nationality · loyalty programs and rough balances · the destination wishlist · **activities and experiences they enjoy**, gathered in Phase 5 · the subagent model assignment and the lineup it was chosen against · home airports and drive-radius alternates · **languages spoken**, which gates whether agent L runs · preferred display currency · standing preferences learned over time.

**Travellers are stored individually and referenced by handle**, so a later run opens with *"same four as last time — Sam, Alex, Jo and Rae?"* rather than re-interrogating. A trip records the handles it applied to. Anyone who declined to be saved is planned for normally and kept nowhere.

**The wishlist and opportunistic detours.** On a first run, ask for the user's most-wanted destinations — open-ended, any number, any granularity. Store it ranked with a note on *why* each is wanted, since "Iceland for the aurora" and "Iceland for the road trip" imply opposite seasons.

Every later run checks the trip against that list. When an entry is reachable — a viable stopover, a feasible detour or open-jaw, or close enough for a multi-day extension — surface it unprompted with the cost in **money and days**, the routing that makes it work (check stopover programs and free-stopover fares specifically; several airlines give them away), and a researched short list of what to do there. Offer it as a priced option; never fold one silently into the plan.

Re-confirm the list in the gate round each run — a stale wishlist keeps pushing detours the user no longer wants.

## 7. Deliverable

Structure in `references/deliverable.md`. Publish as an Artifact:

1. Load the `artifact-design` skill first — required before writing any artifact page.
2. Write the HTML to the scratchpad, and keep the source markdown there too so a later revision does not mean re-researching from zero.
3. Publish with `Artifact`, favicon `✈️`, and hand back the URL.

The page requirements that are easy to get wrong — table overflow containers, theme tokens across all three theme states, self-containment under a strict CSP, a stable favicon — are in `deliverable.md` under Publishing. Follow them there rather than from memory.

Re-running research for the same trip **updates the same artifact** — same file path, or `url:` for one published in an earlier session. Do not mint a second link for the same trip.

## 8. Booking

Work out *how* each thing should be booked, not just what:

- Cash vs. points for every shortlisted flight and hotel, with cents-per-point math so "worth it" is a number rather than a vibe.
- **Transfer paths** — which currency the user holds feeds which partner, at what ratio and how fast, and whether a bonus is live. Transfers are one-way and irreversible: say so, and never suggest transferring before award space is confirmed.
- **Elite benefits and card perks that change the real price** — bags, lounge, waived resort fees, late checkout, hotel credits, free-night certificates, primary rental insurance — and which channel preserves them. OTA bookings often forfeit points and status recognition entirely, which can outweigh a small discount.
- **Every applicable discount**, verified on the operator's own page. Mark anything unconfirmed `UNVERIFIED` rather than passing along a code that fails at checkout.

Then hand over a checklist ordered by lead time, each line carrying its booking link and the cash-or-points call. **Visa applications and lead-time vaccinations go above the flights** — they gate whether the trip happens at all.

**The boundary.** This skill researches and prepares. It does not purchase, enter payment or passport details, create accounts, log into loyalty accounts, initiate point transfers, or submit booking forms. Those stay with the user. Say this up front if the user seems to expect otherwise, so it is not a surprise at the end.

## 9. Close the run by asking what else to dig into

**Every run ends with an explicit offer to research further.** Hand back the artifact URL, then ask — naming the specific things worth pursuing rather than asking an open question nobody can answer cold:

- **The gaps that a decision is resting on**, from the honesty section. These are the ones where five more minutes changes an outcome.
- **Anything a matrix left `UNVERIFIED`** that the user seemed to care about.
- **Any location, category, or day that came out thinner than the rest** — you can see this from the row counts, and the user cannot.
- **Whatever the recon pass surfaced and the gate dropped.** A place cut early is worth re-offering once the shape is settled, because the reason it was cut may no longer hold.

Ask it as a short list of concrete offers, not as "let me know if you need anything else". A closing question that names three real options gets answered; a generic one ends the conversation with the gaps still open.

## References

- [research-rules.md](references/research-rules.md) — the standard every agent works to. Read first
- [source-map.md](references/source-map.md) — the per-domain source list every agent works from, and where newly discovered blocks are recorded
- [api-compatibility.md](references/api-compatibility.md) — where a configured provider is known to fail *for a given destination*, dated, with re-test status
### Code layout

**`lib/` is imported, `scripts/` is run.** Anything used by more than one script lives in `lib/`, because the alternative is copies that drift — the currency symbol map once existed in two files and printed two different things for the same price.

| `references/lib/` | |
|---|---|
| `common.py` | HTTP with backoff, key loading, paths, the locations file |
| `money.py` | **Currency in one place** — symbols, the dated rate, and the both-currencies rule |
| `humanize.py` | **Machine values → reader-facing text.** Enums, statuses, nulls, opening hours |
| `render.py` | Standard table rendering, map links, the link injector |
| `report.py` | **The `Report` builder** — groups, rail, mobile menu, and it *owns every heading* |

| `references/tests/` | |
|---|---|
| `test_money.py` · `test_humanize.py` · `test_render.py` · `test_report.py` | **Offline unit tests** against fabricated fixtures. Every case is a defect that shipped |
| `test_live_apis.py` | **Live** endpoint reachability, plus the per-destination geocoder probe |

| `references/scripts/` | |
|---|---|
| `run_tests.py` | **Run this first, every run.** Exit code is the failure count |
| `build_report.py` | **Build a deliverable from a spec.** Run this instead of writing assembly code |
| `extract_sections.py` | One-time migration: an existing report → fragments + spec |
| `check_report.py` | Pre-publish structural, arithmetic and machine-output checks |
| `run_tests.py` | Run once per destination before dispatch |
| `climate.py` · `daylight.py` · `fx.py` · `places.py` | Fetch and compute. Destination passed at run time |

`references/templates/report.html` holds the page shell and stylesheet.

**Never hand-assemble a report.** Content goes in HTML fragments, structure in a spec, and `build_report.py` puts them together:

```bash
python references/scripts/build_report.py --spec trip.spec.json --out report.html
python references/scripts/check_report.py report.html
```

**The builder owns headings, and that is load-bearing.** A fragment must not contain its own `<h2>`; passing one raises. This exists because a published report shipped the same heading twice — the content and the assembly each believed they owned it, and neither could see the other. Ownership has to sit in exactly one place.

**`__pycache__` is a build artifact, not part of the skill.** `lib/` is an importable package, so running any script generates one; `.gitignore` covers it.
- [agent-briefs.md](references/agent-briefs.md) — the prompt for each research track
- [matrices.md](references/matrices.md) — exact column specs for every matrix
- [deliverable.md](references/deliverable.md) — report structure and booking checklist
- [profile-template.md](references/profile-template.md) — schema for `traveler-profile.md`
