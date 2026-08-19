# Deliverable

The output is a decision document. Someone should be able to read the first screen, know what you recommend and why, and then use the rest to either confirm it or take a different branch on purpose.

**Everything recommended is linked where it is recommended.** Every flight, room, restaurant, tour, rental, train, ticket and pass carries its own link inline — the operator's own page, not an aggregator's, and the reservation link where one is needed. The reader should never have to search for something you already found, and a Sources list at the bottom does not count: nobody scrolls to the bibliography to book row four.

**Complex topics carry a further-reading link beside the summary.** Where a paragraph compresses something intricate — a visa process, EU261 rights, an award programme's restrictions, vaccination requirements, driving and insurance rules — link the authoritative text at that point and label it (*the regulation itself*, *the airline's conditions of carriage*, *the ministry's own page*). Your summary is the orientation; the link is the truth, and some readers will need it.

## The section set

**These sections and this grouping are the default skeleton.** Previously only the rail's mechanics were specified, so the sections themselves were invented fresh each run — and a section nobody names is a section that can quietly fail to exist. Both known failures worked exactly that way: the weather section shipped as a stub and the entry table never appeared at all, and neither was noticed because nothing said they were owed.

`*` marks conditional sections. A conditional section that doesn't apply is **stated as skipped, with the reason** — the rule that already governs tracks K and L applies to their sections too, and for the same reason: a silently omitted section looks identical to one that found nothing.

**The outer grouping is by *place*, not by discipline.** A reader planning tomorrow in one city wants that city's transport, rooms, food and things to do together — not five separate discipline sections to jump between. So each location is its own rail group, carrying the same subsection set, and everything that applies to the whole trip comes after them.

```
Start here        Critical and time-sensitive   ← always the first section in the document
                  Where things stand            headline, settled vs open, assumptions to correct
                  Day by day                    the itinerary
                  When to go                  * flexible dates only
                  Wishlist detours            * only where something on the list is reachable

<Location 1>      Getting there and around      reaching it, local transit, what's walkable
                  Where to stay
                  Things to do
                  Eating and drinking
                  Day trips                   * omit where none, and say so
                  <Must-see>                  * one per thing the user named. see below
                  <Location-specific>         * anything that concerns only this place

<Location 2>      ... the same subsection set, in the same order ...

Trip-wide         Flights
                  Trains, roads, luggage        between the bases
                  Tickets and rights          * multi-carrier or connecting itineraries only
                  Entry
                  Money on the ground
                  Health
                  Weather and daylight
                  Language                    * where the traveller doesn't speak the language
                  Law, scams and safety
                  Points, passes and discounts
                  Budget rollup

Honesty           Risk register
                  What isn't verified
                  Sources
```

**Location groups run in itinerary order** — the order the traveller visits them, so the rail reads like the trip.

**Section ids follow `{location-slug}-{kind}`** — `riverport-lodging`, `oldtown-food`, `capital-daytrips`. This is what makes the structure checkable; `check_report.py` asserts every location carries the core set.

**Every location carries the same core subsections.** A location missing *Where to stay* is a failure, not a style choice — that uniformity is what lets a reader learn the shape once and then navigate every other place by muscle memory.

### Location-specific research goes under its location

Research that concerns only one place **lives in that place's group** — folded into an existing subsection where it fits, and given its own subsection where it does not. A motorsport museum an hour outside one city is that city's business, not a trip-wide topic. Do not create a trip-wide section for something only one location needs.

**Anything the user named as a must-see gets its own subsection, however small.** If they asked for a district, a circuit, a market, a museum — it is a heading in the rail, not three rows inside a general table. A named must-see compressed into a shared table is precisely the failure this rule exists to prevent: the user asked for it by name, so they will look for it by name.

### Five options minimum per category, ten as a soft cap

**Every category in every location carries at least five options.** Below that it is not a comparison — it is a list of whatever turned up, and one closure or sell-out leaves the reader with three. Transport sections are exempt: the number of ways to reach a place is what it is.

**Ten is a soft cap, not a hard one.** Where a sweep turns up one or two extras that genuinely earn a row, keep them. What the cap rules out is padding a table to look thorough.

**The count is per comparison table, not per section.** A section often holds one wide matrix plus small supporting tables, and totalling them lets a thin comparison hide behind its neighbours — a **two-row** decision table on where to spend three nights passed a floor of five by sitting between a four-row and a two-row sibling. `check_report.py` measures the largest table in the section, on the principle that the biggest table is the one the reader actually compares.

### Nothing machine-shaped reaches the reader

**No API enum, field name, status code, null, or ISO currency code appears in the finished page.** Every one of them is translated into something a person would say.

This is a class of defect, not a bug. A published report shipped **eighteen cells reading `PRICE_LEVEL_MODERATE`** — nothing was factually wrong, an enum had simply been printed straight into a human document. It looks fine to whoever wrote the code and looks broken to whoever reads the page.

| Machine form | What the reader gets |
|---|---|
| `PRICE_LEVEL_MODERATE` | `MID`, colour-coded — and only when no real figure exists |
| `OPERATIONAL` · `CLOSED_PERMANENTLY` | *Open* · *Permanently closed* |
| `wheelchairAccessibleEntrance` | *Step-free entrance* |
| an ISO code before a number | the currency symbol a reader sees on a menu |
| `None` / `null` / `NaN` in a cell | *not stated* |
| `LOOKUP_FAILED TypeError` | *Lookup failed* |

**`check_report.py` enforces this** and fails the build on a hit. Two notes from writing that check: it scans **visible text only** — `<script>` and `<style>` legitimately contain camelCase — and **`None` is checked at markup level**, as a cell containing nothing else, because "None required" and "None. Just a surprise on the meter" are correct English and flagging them produced three false positives against good prose.

**Formatting counts as legibility too.** Precision is decided once per range — never two decimals on one bound and none on the other — and the currency symbol appears once per range, matching how the local-currency side is written.

### Every venue is verified into its location before it is filed

**Run `places.py --expect <region>` once per location section and resolve every mismatch before publishing.** A venue that resolves outside the region it sits under is mis-filed, and the script exits with the count.

This is the one structural error that survives every other check in this document. **Thirteen restaurants from one city shipped inside another city's section of a published report** — a combined food track returned one table spanning three cities, and the split at synthesis went by row order rather than by where each place actually is. The section counts looked healthy, every row was individually accurate, and the failure was invisible precisely because nothing was false. It also hid a second problem in plain sight: one city showed twenty-nine food options while another showed five, and that lopsidedness read as "one is better researched" rather than as a filing bug.

**Compounding effect worth knowing:** the verifier appends the section's city to each lookup, so a mis-filed venue gets queried against the wrong city and comes back with a wrong pin. **Correct the filing first, then re-query.** Re-querying a mis-filed row just produces a confident wrong answer.

### The template carries structure, never trip data

**No stylesheet, class name, or template comment may name a real airport, city, property or date.** The template is the part that ships to every user and every trip; trip data reaches the page through the report spec and the traveler profile at run time, into the *table*, never into the CSS.

This is written down because a table of routings from the traveller's home airport was styled with a class named after that airport — `t-<airport-code>` — with the code repeated through six CSS rules and a comment. Nothing was factually wrong and the page rendered correctly, which is exactly why it survived a genericisation pass that removed every other trip reference: **a class name does not read like data.** It is, and it went to a public repository. Name classes for the role the table plays (`t-origin`, `t-lodging`, `t-food`), not for the trip that first needed them.

### Every place name is a map link, and never bolded

**Every hotel, restaurant, experience, tour, museum, station and venue name links to its map location** — the name itself is the anchor, not a pin icon or a trailing "(map)".

**Do not bold place names in matrices.** The link is the emphasis, and bolding them broke the link-injection pass outright: `<b>Name</b>` defeated the matcher and whole sections shipped with no map links while every check reported clean. Bold is for the finding inside a cell — a closure day, a cash-only warning — never for the name of the thing the row is about.

`render.unbold_identity()` strips it at build time and `check_report.py` fails the report if any survives — **both**, because the strip itself shipped broken. It matched a literal `<tr>` and only `<b>`, so every row carrying an attribute and every name written `<strong>` kept its bold: **40 of them published while the rule reported success.** Write the fragments unbolded anyway. A build-time fix you cannot see running is indistinguishable from one that isn't.

**City names in headers link once per city**, on the first section of that location's group. Repeating it in every subsection header is noise. A new major location — another city, another region — gets its own single link when it first appears.

**Group labels describe reader intent, never research structure.** Someone looking for the visa rule does not know it came from track H, and never needs to. Order within a group runs most-decisive first.

**The rail is the table of contents, so every section that exists appears in it.** The weather section was reachable only by scrolling, which is part of why its thinness went unremarked for so long.

**The risk register sits in Honesty as the complete record — but anything in it that changes a decision gets promoted.** A lead-time item belongs in Booking deadlines; a risk that makes one branch worse belongs in The open questions. The register is where the full list lives, not where the urgent parts hide.

### Where each track lands

Every research track resolves to named sections, and this is stated in the brief at dispatch rather than worked out at synthesis. A track with no destination is a track whose findings get compressed into a paragraph and lost.

Per-location tracks land in **their own location's** subsections. Global tracks land in Trip-wide, and three of them fan out into every location group.

| Track | Scope | Lands in |
|---|---|---|
| **Recon** (Phase 3) | per destination | **Day by day** (the outline) · connections → *Getting there and around* · candidates → *Things to do* |
| **Safety** (Phase 3) | trip | **Critical and time-sensitive** · **Risk register** |
| **C** Lodging | per location | *{location}* → Where to stay |
| **D** Experiences | per location | *{location}* → Things to do · **each named must-see its own subsection** · on-sale and ballot dates → **Critical and time-sensitive** |
| **E** Food | per location | *{location}* → Eating and drinking |
| **F** Sentiment | per location | **No section of its own — see below** |
| **G** Day trips and local ground | per location | *{location}* → Day trips · Getting there and around · distances feed **Day by day** |
| **A** Air | trip | Flights |
| **B** Inter-city ground | trip | Trains, roads, luggage |
| **H** Entry, health, climate | trip | **Four trip-wide sections** — Entry · Money on the ground · Health · Weather and daylight — **plus hospitals and air quality into each location's *Getting there and around***, plus jet lag → **Day by day** |
| **I** Points and discounts | trip | Points, passes and discounts · Budget rollup |
| **J** Law and stability | trip | Law, scams and safety · **plus location-specific scams into each location** · advisories → **Risk register** |
| **K** Fare rules and rights | trip | Tickets and rights |
| **L** Language | trip | Language |

Two need calling out, because they are where findings disappear:

**Track F has no section, which makes it the one that vanishes without trace.** Sentiment is cross-cutting by design: it supplies the worth-it verdicts in Day trips, the consensus reads in Eating and drinking, the overrated calls in Things to do, and the block-level reads in Where to stay. Because it owns no heading, nothing looks thin when it contributes nothing. **At synthesis, check those landing points carry a community source — and check them once per location**, since F now runs per location too. A day-trip verdict with no sentiment behind it means F failed for that city and the failure was invisible.

**Track H fans out to four trip-wide sections, every location group, and the itinerary**, which is why it is the most under-delivered track in the skill and why both known stubs came from it. One agent's return has to reach a lot of destinations; treating it as "the H section" guarantees most of them thin out.

## Critical and time-sensitive

**The first section in the document and the first entry in the rail.** It exists because the findings that carry a deadline are the ones most damaged by being scattered — a booking window that closed while the reader was three sections away is a total loss, and nothing else in the document can compensate.

Ordered by **when each one bites**, soonest first:

- **Deadlines already running** — a booking window open now, a transfer ratio degrading on a stated date, a tour that sells out months ahead, a ballot that has already opened
- **Documents that must be obtained before departure** — visas, International Driving Permits, vaccinations with lead times. These gate whether the trip is legal or the activity is possible at all
- **Safety findings that change whether or where to go** — the advisory, outbreak, or seasonal hazard that would alter the plan rather than merely inform it
- **Decisions the user still owes**, each stated as a choice with its own deadline and what hangs on it
- **Anything `UNVERIFIED` that a booking decision is resting on**

**Every entry is one line plus a pointer to the section holding the detail.** This is a dashboard, not a second copy of the document — the moment it starts restating the sections beneath it, it stops being scannable and the deadlines go back into hiding.

The risk register in Honesty remains the **complete** record. This section holds only what is urgent, and anything urgent is promoted here rather than living solely in the register.

## Structure

### 1. Headline

Three to five sentences. The recommended trip shape, the total cost per person, the total days, and the one thing that most drives the recommendation. Then the single most consequential trade-off — the thing a reasonable person might choose differently — stated plainly rather than buried.

### 2. Assumptions and what to correct

Everything assumed rather than asked, listed compactly, with an offer to re-run any leg where an assumption is wrong. Include the profile-derived values used (loyalty programs, home airports, currency, wishlist) so a stale profile is visible rather than silently driving the plan.

State the **FX rate and the date it was looked up** here, once. Every price below is in both currencies against this rate.

### 3. What could actually go wrong

A risk register, high on the page, because these are the findings that change decisions and they get buried if they're scattered through the detail. One card or row per risk, each carrying **severity**, what it is with evidence and dates, and — always — **the mitigation**, since a risk without a fix is just anxiety.

What belongs here:

- **Travel advisories** — the traveller's foreign ministry level and at least one other country's, reported with the **actual reasoning** behind the level and whether it applies to the itinerary or to a region they'll never see. A country-level warning driven by a distant border region is not a warning about the beach town, and saying so is as important as reporting the level. Link the advisory.
- Anything from the stability research that could realistically disrupt *this* trip: announced strikes, elections and charged dates in the window, unrest, seasonal hazards.
- Health risks with real likelihood — current outbreaks, water, foodborne risk.
- Single points of failure in the plan: the one road, the one ferry, the connection that has to work, the sold-out permit.
- Legal exposure worth knowing before departure.
- Anything marked `UNVERIFIED` that a decision is resting on.

Rank by severity, and be honest about likelihood in both directions — omitting a live conflict is negligent, and inflating an ordinary city's petty-theft rate into a crisis is useless and unfair to the place. The test is whether a well-informed resident would recognize the description.

### 4. Wishlist opportunities

Only if the trip touches something on the user's wishlist. What is reachable, what the extension costs in money and days, what routing makes it work, and a short researched list of what to do there. Priced as an option — never folded into the base plan.

### 5. When to go (flexible dates only)

If the user said their dates are movable by weeks or open, this section comes *before* the matrices, because it changes what the matrices are about. Lead with a dated recommended window and the reason, then the month-by-month table, then a direct comparison against whatever the user originally proposed: what moving would cost or save, and what it gains or loses. A better trip discovered after the flights are booked is a regret, not a finding.

### 6. The matrices

In the order from `matrices.md`: flight options, mode comparison, whole-path, lodging, excursions, food, nearby and day trips, distances and travel times, budget scenarios, points and booking channel, discounts and savings, and climate and daylight.

These do not all live together on the page — they sit in the sections that own them, per the map in *The section set* above. Lodging goes in Where to stay, climate in Weather and daylight, and so on.

Each closes with its one-line recommendation and why.

**The column list in `matrices.md` is the deliverable's column list. Render every field.** This sounds obvious and it is the easiest rule here to break, because the wide matrices are awkward to lay out and the tempting fix is to keep four or five columns and fold the rest into a "Notes" cell. That **destroys the comparison the matrix exists to make** — the reader can no longer scan one attribute down the list, which is the whole point of a table.

It also makes missing research invisible. A dropped column and a column full of `UNVERIFIED` look identical to the writer and completely different to the reader: one hides that nobody checked, the other says so and tells them where to spend their own five minutes.

**A field with no data still appears, marked `UNVERIFIED`.** Never omit it.

**Let wide tables be wide and scroll horizontally.** Lodging runs past twenty columns and that is fine. Let the page fill the window and resize with it, keep running prose to a readable measure independently — the two do not need the same width — and put every table in its own `overflow-x: auto` container so it scrolls inside itself while the page body never does.

Four things this needs to actually work, each of which fails silently otherwise:

- **`min-width: 0` on any grid or flex ancestor of the table.** Grid and flex children default to `min-width: auto`, which makes them expand to fit a wide table instead of letting its container scroll. This is the single commonest reason an `overflow-x: auto` container doesn't scroll, and it looks like the overflow rule is broken when it isn't.
- **`table-layout: fixed` with real per-column widths.** Under automatic layout the browser **ignores `max-width` on cells** and sizes them to their content, so long text pushes columns wide and bleeds across its neighbours. Fixed layout is what makes declared widths hold.
- **Widths sized to what each column actually holds.** A yes/no field and a paragraph of complaint themes should not be the same width. Set narrow columns narrow and prose columns wide, or the table is twice as long to scroll as it needs to be.
- **`overflow-wrap: break-word` on every cell**, so an unbroken string — a long URL, a station name, a currency range — wraps instead of forcing its column open.

**Pin the item column and the price column**, not just the first one. Those are the two fields every comparison is made against, and losing either while scrolling right makes the rest of the row meaningless. Sticky headers on vertical scroll, too. Column order is specified in `matrices.md` — identity, the normalized comparator, the action link, then the total, then detail — and it matters more here than anywhere, because the reader may never scroll past the fourth column.

**Mark state visibly, and make the quiet states quiet.** A table this wide is scanned, not read, so the eye needs to catch what matters without reading every cell:

- **Verified, failed, and cautioned** each get a visible marker — a short chip reading *Confirmed*, *Fails*, *Unverified*, *Pick*, *Trap*. A row that fails a hard requirement should be legible as failing from a metre away.
- **`UNVERIFIED` is styled deliberately understated** — small, muted, lowercase. It appears in a great many cells on an honest first draft, and if it shouts, the table reads as broken rather than as candid. It is information, not an error.
- **Past roughly half a section's cells, say it once at the top instead.** Per-cell marking is right until the density stops carrying information: a live report reached **328 markers, 154 in the lodging section alone**, at which point the reader can no longer tell *this cell is unknown* from *this table is mostly unknown* — and the second is a different message that deserves one plain sentence rather than being inferred cell by cell. State what is solid, what is not, and what would close it. The per-cell markers then read as detail inside a stated frame. In that example bed configurations were confirmed and load-bearing while live pricing was largely absent, and nothing on the page made that distinction visible.
- **Struck-through rejected rows keep their data.** Don't blank the cells; the reader wants to see *what* was rejected and how close it came.
- **Derived is a third state, and it is not `UNVERIFIED`.** Much of this document's most valuable content is computed rather than observed: all-in prices, realistic travel times, door-to-door totals, per-person normalisations, break-evens, cents-per-point, statistical figures, and every converted currency. A derived figure **carries its method where it appears** — the conversion basis, the percentile, the sample, the adjustment applied. Marking it `UNVERIFIED` throws away good work by calling it a gap; marking it as plain fact overstates it.
- **A correction to something an earlier version asserted is marked as a correction.** When new research contradicts a published claim, say so visibly rather than editing it away. A reader who already read the page needs to know which belief to drop, and a silent edit makes the document less trustworthy rather than more. The struck-through convention covers rejected rows; this covers rejected *statements*.

**The caption carries the method**, per `matrices.md`: dates, party size, any hard constraint applied as a filter, the source and when it was pulled, and — where cells are empty — one line stating that blanks are marked rather than dropped. Someone landing mid-page should be able to tell what was compared, on what basis, and how much is confirmed, without scrolling up.

**The recommendation goes immediately after the table, not inside it.** One or two sentences: the pick, the reason, and what would change it. A recommendation hidden in a cell is a recommendation nobody reads, and it competes with the data around it.

### 7. Day-by-day itinerary

For each day: date and weekday, base city, what is planned in the morning / afternoon / evening, where meals are, and the transit between each with **realistic times** — including the walk to the station, the wait, and the fact that a museum takes longer than its listed duration.

Take every transit time from the **distances and travel-times matrix**, not from a guess — and use its realistic column, not the map's. Never chain three map times and call it an hour.

**Where daylight is short, put the departure-time consequence on the day it affects.** A scenic day trip in a window where the sun sets before roughly 17:00 is a morning departure or a wasted trip, and that belongs on the day rather than only in the weather section. The daylight figures are in matrix 12; the itinerary is where they become actionable.

**Plan arrival day for the state the traveller will actually be in.** Itineraries routinely schedule day one as a normal day and it is not — a red-eye landing at 7am against a 3pm check-in, or an eight-hour eastward shift, is not a day for a timed-entry museum. Use H's jet-lag finding: the shift size, the direction (eastward is consistently harder), and the local arrival hour. Say what day one can realistically hold, note whether early check-in or a day room is available where the arrival is awkward, and leave it soft.

Build in slack. A plan with no gaps is a plan that breaks at 11am on day two. Mark which items are fixed (timed entry, reservations, festival hours) and which float, so the day can absorb a delay without the whole thing collapsing.

Note opening hours and closure days against the actual weekday — Monday closures alone have ruined a large fraction of all itineraries ever written.

### 8. Weather and daylight

**Render matrix 12 — both tables.** This section previously carried a prose description and no column spec, and it shipped as three rows of published monthly normals plus a paragraph of hedging. The spec exists now; print it.

The two things that make this section worth reading, neither of which survives in a monthly-normals table:

- **The delta against the published monthly figure.** Trips don't occupy calendar months, and a stay in the back half of one can run several degrees off the number the reader will find everywhere else. Showing both is what corrects their other sources.
- **Sunset at the first and last day of the stay.** Where it falls before roughly 17:00, **say what that means for the days it affects** — which scenic day trips need a morning departure, and which become half-days if started after lunch. That consequence belongs here *and* on the affected days in the itinerary; a daylight figure nobody acts on is trivia.

The live forecast **only if the trip is inside forecast range**, clearly labeled as a forecast with the date it was pulled — a 10-day forecast quoted as fact ages badly. Beyond forecast range, say so rather than letting climatology read as a prediction.

Then the packing list, tied to the actual planned activities rather than generic: layers, rain gear, footwear for the real terrain, adapters, sun and altitude. Tie each item to the finding that justifies it — "a real jacket, because nights run near freezing one year in ten" is a packing instruction someone follows.

Then **dress codes**, per item on the itinerary that has one — temple and mosque coverage, jacket-required restaurants, onsen tattoo policies, trail footwear requirements, club door policies, formal nights.

### 9. Health

Separate section, not a footnote inside packing. Required vaccinations and the lead time each needs, recommended ones, current disease activity **with case numbers, region, and date**, malaria and altitude where relevant, prescription medications that are restricted locally and what documentation to carry, and practical care — nearest hospital to each base with its distance, pharmacies, emergency number, insurance.

**Water and food, answered rather than hedged.** Is the tap water drinkable *for a visitor* — which is a different question from whether residents drink it — in each place they'll stay? What about ice, which usually comes from a different supply than the tap, fountains, and brushing teeth. Is a filter bottle worth carrying or is bottled an upsell.

Then the street-food verdict, stated plainly: **broadly safe, safe with named precautions, or genuinely risky**, with the reason. "Be careful with street food" is not a finding and helps nobody. If it's safe — as it is across much of Asia, Latin America and the Middle East, where the street food *is* the cuisine — say so, so the food section can recommend it without hedging. If precautions apply, name the real ones: stalls with queues and high turnover, cooked to order in front of you, skip raw items washed in tap water, ice, unpeeled fruit, unpasteurised dairy. Add what to carry (rehydration salts, an antidiarrhoeal, whether a standby antibiotic is standard advice for this region) and when a stomach problem here needs a doctor rather than waiting it out.

**This verdict is repeated at the top of the food matrix.** That duplication is deliberate: the food section is where someone is actually deciding what to eat, and a warning three sections away is a warning that didn't land.

Anything with a lead time also appears at the top of the booking checklist, because a vaccine needing ten days is a scheduling constraint rather than a packing note.

### 10. Entry requirements

**This is a table, and it has already shipped as prose once.** A live report reduced a mandated per-passport table to five bullets with no rows, no apply-by date, and a blanket assumption that the whole party held the same passport. It read as finished, which is exactly the problem: a confident paragraph looks complete whether or not anything was checked. **Of every section here, this is the one where a missing row means someone is refused at check-in.**

Render Track H's table: **one row per traveller nationality × country**, including every country transited, never generalized across passports. Which regime applies, permitted stay, what the application involves, documents, cost, **advertised versus actual processing time**, an apply-by date, and the **official** application URL with an explicit warning about the paid lookalike sites that shadow every e-visa system.

**Every nationality in the party gets its own rows even where they are expected to match.** The table exists so the assumption is tested rather than asserted — if all four travellers do hold the same passport, four identical rows cost nothing and prove it was checked.

Anything requiring an application gets an "apply by" date in the booking checklist. A visa running three weeks against an advertised 72 hours is a flight-booking constraint, not paperwork.

### 11. Money on the ground

The practical answer to "can I just use my card here?" — one of the most useful half-pages in the document, and one most guides wave through.

**Render Track H's payments table, including its `Source` column** — a live report dropped that column entirely, in a document whose core rule is that every row traces to a source. Prose belongs around the table, not instead of it.

Lead with the **cash verdict** in one line: cash is *essential*, *strongly recommended*, or *optional*, with roughly how much to carry and what for. Then:

- **Which card networks actually work.** Visa and Mastercard are near-universal; **Amex and Discover are refused far more often than their holders expect**. If the traveller's main card is an Amex, that belongs in the risk register, not a footnote.
- **Whether a PIN is needed** — signature-only cards fail at unattended kiosks: rail machines, petrol pumps, tolls, parking, bike-share.
- **Contactless and mobile wallets**, and whether tap is standard.
- **Local payment apps, with the question that actually matters**: can a visitor register at all? Most require a local bank account, national ID, or phone number, which makes a dominant domestic app irrelevant to a tourist. Where a foreign-card workaround exists, give it with its limits and cost; where it doesn't, say so, so the traveller plans around it with cash.
- **Where cash is still required** even in card-friendly countries — markets, taxis, temples, rural areas, tips, lockers, small restaurants. Name the categories.
- **ATM strategy** — which banks take foreign cards and which reject them outright, limits, fees on both ends, and debit versus credit to avoid cash-advance interest.
- **Decline dynamic currency conversion**, every time. The terminal's offer to charge in your home currency always costs you.

### 12. Language and communication

Skip only when the destination's main language is one the traveller speaks — and say that you skipped it.

Lead with **English adoption by context**, because a single country-level claim is useless: front desk, restaurants, taxis, rail staff, pharmacies, police, shops, rural areas. Then signage and machines — whether transit is romanized or bilingual, whether ticket machines have an English mode — since that determines how independently someone can move around.

Then: **translation tools that work for this language pair**, with the offline packs to download *before* departure; a short phrase list chosen for utility rather than phrasebook filler, including allergy and medical phrasing written in the local script if the party needs it; and the **wariness list** — register and formality mistakes, where speaking English changes the price quoted, false friends and gestures, whether refusal is stated or implied, and how to get help in an emergency with no shared language.

Close with the three things most likely to cause a real problem for *this* traveller in *this* country.

### 13. If it goes wrong — rights and airport mechanics

Skip when the trip is a simple non-stop return; say so.

Lead with **ticket structure**, since it is the finding most likely to change a booking: which shortlisted itineraries are one ticket and which are separate tickets, and what a missed connection costs under each. On separate tickets there is no rebooking, no duty of care, the fare is gone, and bags are not through-tagged.

Then **what you're owed when it breaks**: the compensation regime governing each itinerary — EU261, UK261, APPR, DOT, or none — what a long delay, a cancellation, and a denied boarding are each worth, and how to claim. Flag any itinerary sitting outside every regime, because the fare comparison will never show that. Add schedule-change rights, which most travellers never exercise.

Then the mechanics for each connection: terminal changes, whether security or immigration gets re-cleared, realistic queue times, and whose baggage allowance applies on a multi-carrier ticket. Finish with lounge access — what the fare, status, or a held card opens, and whether that lounge is actually worth the walk.

### 14. Staying out of trouble

Four subsections, in this order, because the consequences escalate:

- **Scams and traps** — the specific ones run here, by name, with how each opens and what the tell is. Plus the legal-but-bad-value traps and what locals say to do instead.
- **Customs and courtesy** — greetings, tipping (including where it insults), dining etiquette, shoes, haggling norms, religious observance, and conduct at anything ceremonial on the itinerary.
- **Laws worth knowing** — lead with the short list that carries real legal consequence: drugs including those legal at home, restricted prescriptions, alcohol rules, drones, photography restrictions, vaping bans, currency limits, and traffic law where the drink-drive limit is far lower than at home. Then the rest. State it factually and without alarmism — the goal is a traveller who knows the two or three things that actually matter here, not one who is frightened of the place.

- **Stability and disruption** — conflict or unrest and where it is, political dates in the window, announced strikes, seasonal hazards. Advisories themselves belong in §3 with the rest of the risk register; don't restate them here. Close with a short ranked list of **what could realistically disrupt this trip**, since that is the actionable part.

Where LGBTQ+ legal status or similar is relevant to the travellers, state the law and, separately, how it is actually enforced. Both facts matter and they are often different.

### 15. Booking checklist

Ordered by **lead time — what sells out or expires first goes at the top**, not by trip chronology. Permit lotteries and restaurant windows that open months ahead belong above the flight, even though the flight comes first on the trip. **Vaccinations with a lead time go above everything**, since they gate whether the trip is legal at all.

Each line: what to book, **the direct link to book it**, by when, the price, the **cash-or-points call**, the cancellation terms, and any prerequisite (an IDP before the car, a visa before the flight, a transfer before the award). This is the section the reader works through with a browser open, so a line without a working link is a line that doesn't function.

### 16. Budget rollup

Both currencies, per person and total, per day. Flag the two or three line items that dominate — usually it is not what people expect — and what each would take to move.

### 17. Backups and failure modes

The plan for when it does not go to plan: rain days for outdoor items, alternates for anything that might be sold out, what a strike or cancellation does to the routing and what the recovery is, which bookings are refundable and which are not, and the practical emergency information (embassy, emergency numbers, insurance).

### 18. Sources

This is the **provenance index, not the link directory** — booking and official links already sit inline next to the things they belong to. What goes here is where each finding came from: every URL, grouped by section, each with the date accessed, so any claim in the document can be traced and re-checked.

Then two lists that make the document's limits visible instead of hidden:

- **Everything marked `UNVERIFIED`**, with what was tried. If a decision rests on one of these, say which.
- **Anything that will go stale fastest** — timetables, seasonal hours, award pricing, advisories, promo codes — with a note to re-check before booking.

**When a finding closes a gap, strike it from this list in the same edit.** This is the rule that keeps the honesty section honest, and it is easy to break: findings get added where they belong and nobody walks back here. On one run **four entries drifted** — two questions the body had since answered were still listed as open, a count was stale, and one item appeared twice. A reader who trusts this section, which is exactly the reader it is written for, was being told a question was unresolved while the answer sat two sections above.

A resolved item may stay, **struck through, with the answer and a pointer** — never as an open question. That is the mirror of the marked-corrections rule: that one covers superseding a *claim*, this one covers superseding a *gap*.

## Publishing

1. Load the `artifact-design` skill **first** — required before writing any artifact page.
2. Write the HTML to the scratchpad. Keep the source markdown there too, so a revision does not mean re-researching from zero.
3. **Run the checks below.**
4. Publish with `Artifact`: favicon `✈️`, a stable `<title>` naming the trip, a one-sentence `description`.
5. Hand back the URL.

### Check the arithmetic before publishing

**Every derived column gets recomputed and compared, programmatically.** Hand-typed derived cells are where silent errors live, and they are invisible on reading because a wrong number looks exactly like a right one — a published table once carried a converted temperature copied from the row above it, which no amount of proofreading catches. The both-currencies rule alone puts a derived column on **every price in every matrix**, so this is a standing exposure across the whole document rather than an occasional risk.

Recompute: unit conversions, currency conversions, per-person divisions, totals, and every stated delta.

Then check the relations that **must** hold. A violation means a derived cell is wrong, and each of these is cheap to test:

- `per-person-per-night × people × nights = total` — both columns already sit in the lodging matrix, so this one is free
- individual legs sum to the stated door-to-door time
- component costs sum to the budget rollup
- `points + cash surcharge` reconciles with the stated cents-per-point against the cash price
- arrival is after departure; last departure is after first
- base fare ≤ all-in price, on every row
- min ≤ mean ≤ max wherever a range and an average both appear

### Never read the deliverable whole — extract from it

A finished report runs past **200 KB, roughly 57,000 tokens**. Reading it to answer a question about one section costs more than the entire skill's reference set. **Query it with a script instead** — pull the headings, the section boundaries, one table's rows, the link hosts per section. Every structural fact in the checks below was established that way, and none of them required loading the document.

This was discovered by necessity rather than instruction on the run it comes from, which is why it is written down: the pull to just read the file is strong and the cost is invisible until measured.

### Check the structure before publishing

- **Every section in the set has either content or a stated reason it was skipped.** This is the check that would have caught both known failures.
- **Every `id` has a rail entry and every rail entry resolves.** Two lines of script, and it has already caught a missing anchor.
- **Critical and time-sensitive is the first section** in both the rail and the document.
- **Every location group carries the core subsection set**, and every location section id matches `{location-slug}-{kind}` against a declared location. A location silently missing *Where to stay* is the location-grouped equivalent of the old missing-section failure.
- **Every section whose columns are specified prints a table**, not a paragraph — the ones listed in `matrices.md` under *Sections that are tables, not prose* included.
- **Every required matrix is present, or documented as skipped with the reason — checked per location** for the location-scoped ones. Checking sections is not the same as checking matrices: a run that passed every section check was still missing three required matrices, because nothing asserted the matrix set. Where one genuinely doesn't apply, **say so in the report**.
- **Every location section carries at least one Google Maps link.** A location section with no linked place is one where nothing was made findable.
- **No gaps entry contradicts the body**, and no entry appears twice. See the reconciliation rule above.

`references/scripts/check_report.py` implements these. Run it rather than rewriting it.

**One warning from its own history.** The script matched a literal `<table>` for most of its life, so **every table written as `<table class="…">` was silently skipped** — column counts and captions reported `ok` against tables it had never examined. A check that passes because it never ran is worse than no check, because it is trusted. When adding a check, confirm it fails on a document you know to be broken before believing it passes on one you hope is fine.

**That was not one bug, it is the failure mode of this codebase.** The same shape has now been found eight times: `<table>` skipping classed tables; `google.com/maps` missing `maps.google.com/?cid=`; `None` handled while other nulls were not; five currency codes handled out of thirty; `<b>` stripped while `<strong>` survived; `<tr>` and `<tbody>` matched bare so every row and body carrying an attribute was skipped; the lodging invariant requiring its class on the `<table>` when it sits on the wrapper, so it reported **`0 rows checked` as though that were a pass**; and the word `resolved` counted as gap-resolution when a caption meant coordinate-resolution.

So, whenever you write a matcher: **enumerate the valid spellings of the thing before matching one of them.** Tags take attributes. Nulls have several literals. Emphasis has two tags. URLs have several hosts. And a count of zero is a symptom, never a result — if a check reports that it examined nothing, treat it as failing until you know why.

### Navigation

**This document needs a persistent side rail, and it is not optional.** Eighteen sections is far past the length anyone reads top to bottom. The reader arrives wanting one specific thing — the booking checklist, tomorrow's plan, the entry rules, what the recommendation actually was — and a page that can only be reached by scrolling makes them hunt for it every time. They will come back to this page a dozen times before the trip and almost never to read it in order.

- A **sticky left rail** on desktop, holding every section anchor. It stays put while the content scrolls.
- **The groups are specified in *The section set* above** — Start here, one group per location in itinerary order, Trip-wide, Honesty. They describe what the reader is trying to do, not how the research was organised. The numbering in this file is a writing order, not a reading order.
- **Don't number the rail items.** These sections aren't a sequence — numbering them implies a progression that doesn't exist and invites the reader to think they've missed something.
- **Every section that exists appears in the navigation.** A section reachable only by scrolling is one whose absence or thinness nobody notices.
- Give every section `scroll-margin-top` so an anchor jump doesn't land the heading jammed against the viewport edge.
- Anchor links need a visible focus state, same as everything else.

**On mobile the rail becomes a floating menu pinned to the top of the viewport — it does not disappear.**

This corrects earlier guidance in this file, which said to hide the rail below roughly 1000px on the reasoning that a phone is a scroll anyway. That was wrong, and the location grouping makes it clearly wrong: **this document is now thirty-odd sections across five or six groups, and a phone reader with no navigation has to scroll past four cities to reach the entry rules.** The rail is how anyone finds anything here, and phones are where a travel document is actually read — at the station, in the taxi, outside the restaurant.

- **A `position: sticky; top: 0` bar** across the top of the content, travelling with the page so it is reachable from any scroll position. Not `fixed` — sticky keeps it in flow, so it never overlaps the masthead on load and never covers content at the end of the page.
- **Give it a solid token background and a `z-index`** above the content. A translucent bar over a scrolling wide table is unreadable.
- **The current section is the button label.** Tapping opens the full grouped list; tapping an entry jumps and closes it. Showing where you *are* is half the value — on a document this long, "which city am I in" is a real question.
- **Keep the group headings inside the open menu.** Flattening thirty anchors into one undifferentiated list is worse than no menu; the grouping is the thing that makes it navigable.
- **The menu must scroll internally** with `max-height` and `overflow-y: auto`. A list of every section on a phone is taller than the viewport, and a menu whose last third is unreachable is a bug that only appears on the longest trips.
- Below the desktop breakpoint the left rail is hidden and this replaces it — one navigation, never both at once.

Where the trip has a genuine either/or in it — two candidate routings, two versions of a week — **give each branch its own anchor** so the reader can send someone straight to the one under discussion.

### Page requirements that are easy to get wrong

- Every matrix inside its **own `overflow-x: auto` container**. These tables are wide; the page body must never scroll sideways.
- Theme tokens on bare `:root`, redefined under `@media (prefers-color-scheme: dark)` guarded as `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`. Give `body` an explicit token background.
- Fully self-contained — a strict CSP blocks every external host. No CDN scripts, no external fonts, no remote images.
- Favicon identical across redeploys. Users find the tab by its icon.

**Re-running research for the same trip updates the same artifact** — same file path, or pass `url:` for one published in an earlier session. Do not mint a second link for the same trip.

## Tone

Set in [research-rules.md](research-rules.md) under *Reporting findings* — write like an agent who will hear about it if the recommendation is wrong. One thing specific to the finished page: **flag the traps as visibly as the picks.** The fare that is cheap until the bag is added, the hotel that is cheap until the taxi is added, the award that is free until the surcharge is added. In a table those rows look like winners, and someone will choose one unless you mark it.

**Show rejected options struck through, not deleted.** When later research invalidates something the page previously recommended, leave the row visible with a line through it and one line on why it failed. Silently removing it means the reader finds it again on their own — it's still the top result on every booking site — and has no idea it was already considered and ruled out. This matters most for the options that *look* best: the cheapest row in a table is the one someone will rediscover, so it is the one that most needs a visible reason for its absence.

The same applies to corrections. When a finding is withdrawn rather than adjusted — because the number was answering the wrong question, not merely wrong — **say that plainly rather than quietly restating it.** A reader who saw the earlier version needs to know it's gone, not wonder whether they misread it.
