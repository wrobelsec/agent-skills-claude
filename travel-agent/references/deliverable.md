# Deliverable

The output is a decision document. Someone should be able to read the first screen, know what you recommend and why, and then use the rest to either confirm it or take a different branch on purpose.

**Everything recommended is linked where it is recommended.** Every flight, room, restaurant, tour, rental, train, ticket and pass carries its own link inline — the operator's own page, not an aggregator's, and the reservation link where one is needed. The reader should never have to search for something you already found, and a Sources list at the bottom does not count: nobody scrolls to the bibliography to book row four.

**Complex topics carry a further-reading link beside the summary.** Where a paragraph compresses something intricate — a visa process, EU261 rights, an award programme's restrictions, vaccination requirements, driving and insurance rules — link the authoritative text at that point and label it (*the regulation itself*, *the airline's conditions of carriage*, *the ministry's own page*). Your summary is the orientation; the link is the truth, and some readers will need it.

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

In the order from `matrices.md`: flight options, mode comparison, whole-path, lodging, excursions, food, nearby and day trips, distances and travel times, budget scenarios, points and booking channel, discounts and savings.

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
- **Struck-through rejected rows keep their data.** Don't blank the cells; the reader wants to see *what* was rejected and how close it came.

**The caption carries the method**, per `matrices.md`: dates, party size, any hard constraint applied as a filter, the source and when it was pulled, and — where cells are empty — one line stating that blanks are marked rather than dropped. Someone landing mid-page should be able to tell what was compared, on what basis, and how much is confirmed, without scrolling up.

**The recommendation goes immediately after the table, not inside it.** One or two sentences: the pick, the reason, and what would change it. A recommendation hidden in a cell is a recommendation nobody reads, and it competes with the data around it.

### 7. Day-by-day itinerary

For each day: date and weekday, base city, what is planned in the morning / afternoon / evening, where meals are, and the transit between each with **realistic times** — including the walk to the station, the wait, and the fact that a museum takes longer than its listed duration.

Take every transit time from the **distances and travel-times matrix**, not from a guess — and use its realistic column, not the map's. Never chain three map times and call it an hour.

**Plan arrival day for the state the traveller will actually be in.** Itineraries routinely schedule day one as a normal day and it is not — a red-eye landing at 7am against a 3pm check-in, or an eight-hour eastward shift, is not a day for a timed-entry museum. Use H's jet-lag finding: the shift size, the direction (eastward is consistently harder), and the local arrival hour. Say what day one can realistically hold, note whether early check-in or a day room is available where the arrival is awkward, and leave it soft.

Build in slack. A plan with no gaps is a plan that breaks at 11am on day two. Mark which items are fixed (timed entry, reservations, festival hours) and which float, so the day can absorb a delay without the whole thing collapsing.

Note opening hours and closure days against the actual weekday — Monday closures alone have ruined a large fraction of all itineraries ever written.

### 8. Weather and packing

Climate normals for the dates: average high and low, rainfall, humidity, daylight hours, sea temperature where it matters. The live forecast **only if the trip is inside forecast range**, clearly labeled as a forecast with the date it was pulled — a 10-day forecast quoted as fact ages badly.

Then the packing list, tied to the actual planned activities rather than generic: layers, rain gear, footwear for the real terrain, adapters, sun and altitude.

Then **dress codes**, per item on the itinerary that has one — temple and mosque coverage, jacket-required restaurants, onsen tattoo policies, trail footwear requirements, club door policies, formal nights.

### 9. Health

Separate section, not a footnote inside packing. Required vaccinations and the lead time each needs, recommended ones, current disease activity **with case numbers, region, and date**, malaria and altitude where relevant, prescription medications that are restricted locally and what documentation to carry, and practical care — nearest hospital to each base with its distance, pharmacies, emergency number, insurance.

**Water and food, answered rather than hedged.** Is the tap water drinkable *for a visitor* — which is a different question from whether residents drink it — in each place they'll stay? What about ice, which usually comes from a different supply than the tap, fountains, and brushing teeth. Is a filter bottle worth carrying or is bottled an upsell.

Then the street-food verdict, stated plainly: **broadly safe, safe with named precautions, or genuinely risky**, with the reason. "Be careful with street food" is not a finding and helps nobody. If it's safe — as it is across much of Asia, Latin America and the Middle East, where the street food *is* the cuisine — say so, so the food section can recommend it without hedging. If precautions apply, name the real ones: stalls with queues and high turnover, cooked to order in front of you, skip raw items washed in tap water, ice, unpeeled fruit, unpasteurised dairy. Add what to carry (rehydration salts, an antidiarrhoeal, whether a standby antibiotic is standard advice for this region) and when a stomach problem here needs a doctor rather than waiting it out.

**This verdict is repeated at the top of the food matrix.** That duplication is deliberate: the food section is where someone is actually deciding what to eat, and a warning three sections away is a warning that didn't land.

Anything with a lead time also appears at the top of the booking checklist, because a vaccine needing ten days is a scheduling constraint rather than a packing note.

### 10. Entry requirements

One row per traveller nationality × country, including every country transited — never generalized across passports where the party holds different ones. Which regime applies, what the application involves, cost, **advertised versus actual processing time**, and the **official** application URL with an explicit warning about the paid lookalike sites that shadow every e-visa system.

Anything requiring an application gets an "apply by" date in the booking checklist. A visa running three weeks against an advertised 72 hours is a flight-booking constraint, not paperwork.

### 11. Money on the ground

The practical answer to "can I just use my card here?" — one of the most useful half-pages in the document, and one most guides wave through.

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

## Publishing

1. Load the `artifact-design` skill **first** — required before writing any artifact page.
2. Write the HTML to the scratchpad. Keep the source markdown there too, so a revision does not mean re-researching from zero.
3. Publish with `Artifact`: favicon `✈️`, a stable `<title>` naming the trip, a one-sentence `description`.
4. Hand back the URL.

### Navigation

**This document needs a persistent side rail, and it is not optional.** Eighteen sections is far past the length anyone reads top to bottom. The reader arrives wanting one specific thing — the booking checklist, tomorrow's plan, the entry rules, what the recommendation actually was — and a page that can only be reached by scrolling makes them hunt for it every time. They will come back to this page a dozen times before the trip and almost never to read it in order.

- A **sticky left rail** on desktop, holding every section anchor. It stays put while the content scrolls.
- **Group the links by what the reader is trying to do**, not by the section numbering above: deciding, the itinerary itself, getting there, on the ground, practicalities, the honest limits. The numbering in this file is a writing order, not a reading order, and the rail should reflect how someone actually arrives at the page.
- **Don't number the rail items.** These sections aren't a sequence — numbering them implies a progression that doesn't exist and invites the reader to think they've missed something.
- Below roughly 1000px, **hide the rail rather than collapsing it into a hamburger**. On a phone the page is a scroll regardless, and a disclosure menu is more friction than the thing it replaces.
- Give every section `scroll-margin-top` so an anchor jump doesn't land the heading jammed against the viewport edge.
- Anchor links need a visible focus state, same as everything else.

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
