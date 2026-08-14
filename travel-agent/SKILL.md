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

**Quick path** — one more batch: **how flexible the dates are** (see below), budget band and what it covers, party size and ages, pace and interests. Everything else comes from the profile or from a default, and every assumption gets stated in the deliverable with an offer to re-run that leg if it is wrong.

**Date flexibility is a distinct question, always asked.** Not "what are your dates" but *how movable are they*, which changes what the research is for:

- **Locked to an event** — price ±1–2 days anyway, so the cost of the fixed dates is visible. Sometimes it is zero, which is worth knowing.
- **Flexible by days** — scan the surrounding window; report what the flexibility is worth in money and whether it dodges a holiday, closure, or festival crush.
- **Flexible by weeks, or open** — then **the best time to visit is part of the job, not a footnote.** Agent H builds a month-by-month picture (weather, seasonal pricing, crowds, what is only open or only happening then, and the months locals themselves name as best), and the deliverable leads with a dated recommended window compared against whatever the user originally proposed. A trip moved three weeks is often a materially better trip for less money — and that finding is worthless once the flights are booked.

**In-depth path** — a few rounds adding: destination shortlist or "surprise me", passport nationality per traveller, mobility and dietary needs, appetite for long layovers and multi-city routing, willingness to drive abroad, hotel vs. whole-home preference, trip themes, and hard avoids. Write the durable answers back to the profile.

**Currency** is asked once and stored. Every price appears in **both** the local and the user's preferred currency — `¥18,000 (~$118)` — with the FX rate and its lookup date stated once at the top. A rate quoted without a date is worthless a month later.

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

Spawn `general-purpose` subagents in the **background**, all in one message, each with its brief from `references/agent-briefs.md` and its `model` from §4. **G and K run in a second wave after A returns** — layover explorability and ticket structure both depend on which routings actually exist.

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

You — intake, synthesis, matrices, recommendations, the artifact — run on the latest flagship model. Research agents run cheaper, because their job is retrieval and structured reporting, not judgment about the trip as a whole. Pass `model` explicitly on every `Agent` call.

| `model` | Agents | Why |
|---|---|---|
| `sonnet` | A, C, G, H, I, J, K | Fine print is where money is lost and trouble starts — fare conditions, award restrictions, contradictory reviews, and for H/J/K vaccination rules, criminal law, and whether a ticket strands you. A confidently wrong answer here is far worse than a slow one. |
| `haiku` | B, D, E, F, L | Largely retrieval and list-building against named sources. Fast, cheap fan-out is the right trade. |

Store the assignment in the profile alongside the model lineup it was chosen against. Offer it pre-filled in the gate round every run. Ask **fresh** — with a short note on which of the now-available models suits which track — on a first run and whenever the lineup has changed, so the skill does not quietly pin itself to a superseded generation.

## 5. Synthesis

Build the matrices in `references/matrices.md`. Required set: flight options, mode comparison, whole-path, lodging (hotels and homeshares together), excursions, food, nearby/day-trip, **distances and travel times**, budget scenarios, points & booking-channel, **discounts and savings**, and — when dates are flexible — **best time to visit**.

Every matrix ends with a one-line **recommendation and why**. A matrix without a pick is not a decision, it is homework.

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
