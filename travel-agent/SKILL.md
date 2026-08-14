---
name: travel-agent
description: Full-service travel planning — live-researches flights, trains, driving, lodging, excursions, food, festivals, and local spots across travel sites, Reddit/forums, blogs, and direct operator sites, then builds comparison matrices and a day-by-day itinerary. Use when the user is planning a trip, comparing destinations or routes, asking where to stay or eat or fly, weighing layovers or rail-vs-air, working out points versus cash, or wants an itinerary built.
---

# Travel agent

Plan trips the way a good human agent does: research everything live, from the actual operators and from people who have been there, then lay the options side by side so the user can decide. The output is a decision-making document, not a brochure.

The single biggest failure mode is answering from memory — everything in the deliverable traces to a page fetched **this session** (§2).

## 0. Tool preflight

`WebSearch` and `WebFetch` are frequently deferred. Load them before anything else:

```
ToolSearch(query: "select:WebSearch,WebFetch", max_results: 5)
```

When a site blocks plain fetches — Google Flights, many airline and OTA sites — fall back to `mcp__Claude_Browser__*` (`preview_start` with a `url`, then `get_page_text`). Use `mcp__claude-in-chrome__*` only when the user's own logged-in sessions are genuinely needed, and ask first.

## 1. Intake

Read `traveler-profile.md` in this skill's directory first. If it does not exist, this is a **first run**.

Then ask **one gate round** via `AskUserQuestion` before any real questioning, so there is a single interruption before the path forks. Bundle:

1. **Intake style** — quick round (one batch of essentials, then straight to research) or in-depth interview (a few rounds covering everything first).
2. **Research depth** — quick / standard / exhaustive (see §3).
3. **Subagent model** — pre-filled from the profile. Asked fresh on a first run, and whenever the available model lineup has changed since the stored choice (see §4).

On a first run, follow the gate round with the two profile questions — loyalty programs and the destination wishlist (§6). On later runs, show the stored values back and ask only whether anything changed.

**Quick path** — one more batch: **how flexible the dates are** (see below), budget band and what it covers, **party size and sleeping arrangements**, pace and interests. Everything else comes from the profile or from a default, and every assumption gets stated in the deliverable with an offer to re-run that leg if it is wrong.

**Sleeping arrangements are a distinct question, and headcount does not answer it.** Ask how many separate beds the party needs and who, if anyone, shares. Four adults travelling together are not two couples unless they say so, and the answer decides the entire lodging budget — a "two rooms for four people" search returns rooms holding one bed each across most of the world. Missing this on a live run invalidated every lodging price in three cities, and the traveller caught it after the plan was published.

**Ask what they specifically want to *do*, not just what they're interested in.** Broad interest categories — food, culture, nature, nightlife — do not surface the things that need booking months ahead, and those are exactly the things that get missed. A traveller who ticks "cities and modern culture" may also want a **sports fixture, a sumo tournament, a concert, a festival, a cooking class, a distillery tour, a market at dawn, a specific museum exhibition** — and none of that follows from the category.

This matters because these are the highest-lead-time items in any trip. On a live run the traveller had to ask for sumo, baseball and concerts explicitly after the research was already underway, and it turned out **the autumn sumo tour passed through their base city on two days of their stay** and a **home playoff game was plausible twenty minutes away** — neither of which any interest category would have produced. Both had ticket windows that had already opened.

So ask directly: *is there anything specific you want to see or do — a match, a performance, a festival, a class, a particular place?* Then check the window for those categories whether or not they name any, since a fixture list is cheap to check and impossible to recover once sold out.

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
4. **Pass the resolved list into every brief** — endpoint, auth shape, and the **live rate limit**, so agents pace against a real number instead of guessing. Same problem as the shared search budget, same treatment.

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

## 2. Research rules

**Read [research-rules.md](references/research-rules.md) before spawning agents.** It holds the full standard — sourcing, money, time, health and safety, legal and cultural exposure, transport, and how findings get reported — and every agent brief is written against it. Re-read it during synthesis when a finding looks too clean.

Three that decide whether the whole thing is worth anything, so they live here too:

**Live only.** Every price, schedule, opening hour, and closure comes from a search or fetch performed **this session**, carried with its source URL and the date accessed. Never fill a gap from training data. A confidently stated stale price is worse than no price, because the user acts on it.

**`UNVERIFIED` is a valid answer and a guess never is.** Anything unconfirmed gets labeled with a note on what you tried. An honest hole tells the user where to spend their own five minutes; an invention costs them a booking. Never invent flight numbers, addresses, hours, or prices — and in the health, entry, and legal sections an invented fact is dangerous, not merely unhelpful.

**Authority hierarchy for anything with consequences.** Entry rules, vaccination requirements, transit legality, law: the destination government's own page is the authority, the traveller's foreign ministry is the cross-check. Never rest a consequential claim on a travel blog, and never trust a summary that does not name the nationality it applies to.

## 3. Research fan-out

Depth comes from the gate round:

- **Quick** — A, C, F, plus H whenever the destination is somewhere the user has not been. Health and entry requirements are never optional on an unfamiliar destination, however light the rest of the research is.
- **Standard** — A, B, C, D, E, F, H, J, plus I whenever the profile lists loyalty programs.
- **Exhaustive** — all twelve (A–L), plus extra agents split per city on multi-city trips.

**Two tracks are conditional at any depth below exhaustive**, because they are wasted on the trips they don't apply to:

- **K** runs whenever the itinerary connects or spans more than one carrier — which is exactly when ticket structure, interline baggage, and compensation regime matter. Skipped on a simple non-stop return.
- **L** runs whenever the destination's main language is not one the traveller speaks, read from the profile.

When either is skipped, **say so and why**. A silently omitted track looks identical to one that found nothing.

### Dispatch — in waves, never all at once

**The `WebSearch` budget is shared across every sibling agent, and so is the session limit.** This is the most important operational fact in the skill and it is invisible until it bites. A run that dispatched seventeen agents in a single message exhausted the shared search pool in about four minutes, took the session limit down with it, and lost **fourteen of the seventeen** before any returned. Everything after that was recovery.

- **Cap concurrency at 4–6 agents in flight.** The cap is on the *total*, not per city — per-city splits multiply the count fast, and exhaustive depth on a three-city trip is well past a dozen tracks.
- **Dispatch in waves, ordered by what unblocks synthesis.** Air and entry/health first, since routing and lead-time constraints shape everything downstream. Then lodging and day trips. Then food, sentiment, points, law, language.
- **Give every brief an explicit search budget** — a stated number of `WebSearch` calls, scaled to how many agents are in flight — alongside its numbered priority list, so an agent running low knows what to drop rather than thinning everything. Agents respect a stated cap and invent their own when none is given.
- **G and K run after A returns.** Layover explorability and ticket structure both depend on which routings actually exist.

Spawn in the **background** as `travel-researcher` or `travel-scout` (§4), each with its brief from `references/agent-briefs.md`.

**Every brief names where its findings land** — the deliverable sections that track fills, from the map in `deliverable.md`. State it at dispatch rather than working it out at synthesis: a track with no named destination is a track whose findings get compressed into a paragraph and lost. Two need watching in particular. **F owns no section of its own** — its output feeds verdicts inside five other sections, so nothing looks thin when it returns nothing. **H feeds four sections plus the itinerary**, which is why it is the most under-delivered track here and why both known stub failures came from it.

| | Track |
|---|---|
| **A** | **Air.** Google Flights, airline direct sites, flexible-date scans. Non-stop first, then one-stop. **Every fare class priced** — basic economy through business — with what each actually includes. |
| **B** | **Ground.** Rail operators direct, Rome2Rio/Omio-class aggregators, intercity bus, ferries, car rental with one-way fees and insurance/IDP rules, fuel and tolls. Also **luggage forwarding** (Japan's takkyubin, European door-to-door services, airport-to-hotel delivery, station lockers) — shipping bags ahead is what makes a rail day or a long layover actually workable. |
| **C** | **Lodging — hotels *and* homeshares, in one table on the same all-in basis.** Direct sites vs. aggregators; Airbnb, Vrbo, Booking's apartments and the local platform that actually dominates there. Neighborhood tradeoffs, shuttles, resort fees, cancellation, **neighborhood safety data**, and **off-platform reviews** — a 9.1 on an OTA regularly hides a bad block. **Amenities listed per property** — pool, A/C, lift, kitchen, laundry, parking, luggage hold — verified against recent reviews rather than the OTA checkbox. **In warm destinations, rank a usable pool above an equivalent property without one**, and confirm it is open on the actual dates. For homeshares also: fees spread over real nights, **short-term-rental legality and licence number**, late-arrival handling, and scam signals. |
| **D** | **Experiences.** Operators direct, GetYourGuide/Viator-class, official park and museum sites, timed entry and sell-out lead times, transport included in the tour. Plus **local festivals and seasonal events** in or near the window, **experiences unique to that place or climate**, and the **etiquette** around each. |
| **E** | **Food.** Must-try dishes and the specific places locals name. Markets, neighborhood spots, reservation lead times, Michelin/Bib/50Best against local consensus. **Street food treated as a tier, not a caveat**, gated on H's water and foodborne verdict — recommended properly where it's safe, with named precautions where they apply. |
| **F** | **Community sentiment.** Reddit, TripAdvisor/FlyerTalk/Rick Steves-class forums, travel blogs and YouTube itineraries, tier lists, overrated/underrated threads. |
| **G** | **Corridor scout.** Day trips and easily-reachable towns, plus cities a *routing through* the destination unlocks. Scores each layover city for explorability. Cross-references the **wishlist** and hunts stopover and open-jaw fares. Also owns the **distance and travel-time matrix** — measured from map data, not estimated. |
| **H** | **Entry, health and climate.** **Visa regime and application process per passport nationality** — official URL, cost, advertised vs. actual processing time, apply-by date — for the destination and every country transited. **Required and recommended vaccinations including those triggered by transit countries**, outbreak data with case numbers, malaria and altitude, **tap-water potability and a plain street-food verdict passed to agent E**, hospitals near each base, eSIM, transit passes, holidays, climate normals, packing and dress codes. Plus **payments**: cash essential / recommended / optional, which card networks actually work (Amex and Discover get refused far more than holders expect), whether signature-only cards fail at unattended kiosks, and whether a local payment app is mandatory — and if so, **whether a visitor can even register**, since most require a local bank account or ID. When dates are flexible, the **best-time-to-visit analysis** by month. |
| **I** | **Points, rewards and discounts.** Award availability and cash-vs-points break-even, elite benefits, **transfer paths between programs** with ratios and timing, live bonuses, card perks held. Then everything flights and hotels leave out: **city passes with the break-even actually calculated**, railcards, association and club car-rental rates, operator-direct vs. marketplace pricing, museum free days, dining programs, shopping portals, and memberships the user may already hold. |
| **J** | **Customs, law, stability and self-protection.** Named local scams and how they run, tourist traps and what locals say instead, customs and traditions including tipping and haggling, the **laws that get travellers arrested or fined**, and **current political and local instability** — advisories with their real reasoning, conflict and unrest, elections and charged dates in the window, announced strikes, and seasonal hazards. |
| **K** | **Fare rules, passenger rights and airport mechanics.** Second wave. **One ticket or separate tickets** for each itinerary and what a missed connection then costs — the highest-value finding in the track. Which **compensation regime** governs (EU261/UK261/APPR/DOT) and what a delay is worth, schedule-change rights, whose **bag allowance** applies on multi-carrier tickets, terminal changes and whether security is re-cleared, and lounge access. |
| **L** | **Language and communication.** Languages actually spoken by region, **English adoption broken down by context** — front desk vs. pharmacy vs. police vs. rural — rather than as one useless number. Signage, romanization, and whether ticket machines have an English mode. Translation tools that work for *this* language pair and the offline packs to pre-download. Phrases worth learning, including allergy and medical phrasing. Plus the wariness list: register mistakes, where English changes the price quoted, gestures, directness, and emergency communication. |

Agents return raw sourced findings as tables plus notes, never narrative. Synthesis is your job, not theirs.

## 4. Model policy

You — intake, synthesis, matrices, recommendations, the artifact — run on the latest flagship model. Research agents run cheaper, because their job is retrieval and structured reporting, not judgment about the trip as a whole.

**Two custom agent types carry the model and the standing rules**, so the per-track brief no longer has to restate them. They live in `.claude/agents/` and are dispatched by name rather than by passing `model` on the call:

| Agent type | Model | Tracks | Why |
|---|---|---|---|
| **`travel-researcher`** | `sonnet` | A, C, E, G, H, I, J, K | Fine print is where money is lost and trouble starts — fare conditions, award restrictions, contradictory reviews, and for H/J/K vaccination rules, criminal law, and whether a ticket strands you. A confidently wrong answer here is far worse than a slow one. |
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

It holds: loyalty programs and rough balances · the destination wishlist · the subagent model assignment and the lineup it was chosen against · home airports and drive-radius alternates · passport nationality · **languages spoken**, which gates whether agent L runs · preferred display currency · dietary needs · mobility constraints · standing preferences learned over time.

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

## References

- [research-rules.md](references/research-rules.md) — the standard every agent works to. Read first
- [source-map.md](references/source-map.md) — the per-domain source list every agent works from
- [agent-briefs.md](references/agent-briefs.md) — the prompt for each research track
- [matrices.md](references/matrices.md) — exact column specs for every matrix
- [deliverable.md](references/deliverable.md) — report structure and booking checklist
- [profile-template.md](references/profile-template.md) — schema for `traveler-profile.md`
