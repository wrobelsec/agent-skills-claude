# Comparison matrices

Column specs for every matrix in the deliverable. These are the synthesis product — agents return raw findings, you build these.

Rules that apply to all of them:

- **Every matrix ends with a one-line recommendation and why.** A matrix without a pick is homework, not advice.
- Every price in **local currency and the user's preferred currency**, with the dated FX rate stated once at the top of the report.
- Every row traceable to a source. Where a cell could not be verified, write `UNVERIFIED` rather than a plausible number.
- Sort by the dimension that matters for the decision, not alphabetically. Usually that is all-in cost or total time.
- Mark the **recommended row** visibly, and mark any row that is a trap (cheap headline, bad total) so it is not accidentally chosen.
- Where a research agent flagged a contradiction between sources, carry it into the matrix rather than resolving it silently.
- **Every row carries a link, and it is the operator's own.** Whatever the row recommends — a flight, a room, a table, a tour, a car, a train, a ticket — the reader must be able to act on it from that row. Not from a bibliography at the bottom of the page. Where an official page genuinely cannot be found, write that in the cell rather than linking something that merely looks official.

### Column order

**This applies to any matrix wide enough to scroll horizontally** — lodging, flights, excursions, food, day trips. Narrow tables that fit on one screen can put the link last; the problem this solves doesn't arise there.

For the wide ones the order below is the order they appear, and it is not cosmetic: past a dozen columns the first few decide whether the table is usable at all.

1. **Identity** — what this row is. Pinned when the table scrolls.
2. **The normalized comparator** — the one number that is comparable *across rows*, and pinned alongside identity. Usually **per person per night** for lodging, per person for tours, all-in per traveller for flights. This is not the same as the total, and the total is the wrong thing to lead with: a four-night stay and a one-night ryokan have totals that cannot be compared at all, while their per-person-per-night figures can.
3. **The action link** — immediately after. The reader who has decided from the first two columns should not scroll through twenty more to find how to book it. Putting it last, as is conventional, means the two ends of the decision sit as far apart as the table allows.
4. **The total**, and any other money.
5. **Everything else**, grouped so related fields sit together — configuration, then amenities, then access, then reviews and cautions.

Where several tables in one section describe variants of the same thing — city hotels and ryokan, say — **keep the column positions identical and adapt the labels**. "On-site food" becomes "Dinner and breakfast" for a ryokan where meals are the point; "neighbourhood safety" becomes "setting" where there is no neighbourhood. Same skeleton, so a reader who has learned one table can read the next; different words, so each says something true.
- Where a matrix cell compresses a complex rule into a few words — a fare condition, a compensation regime, a visa route, an insurance term — carry a **further-reading link to the authoritative text** alongside it. The reader should never have to go searching for the rule you summarized.

### Sections that are tables, not prose

The matrices below are not the whole deliverable. Several sections have their column specs in **`agent-briefs.md`** instead — that file governs what the *agent returns*, and nothing was carrying those columns across the synthesis boundary, so they were being compressed into paragraphs and lost.

That is not hypothetical. It has happened twice: the weather section shipped as three rows of monthly normals against a full climate spec, and the **entry section shipped as five prose bullets against a mandated per-passport table** — the one section where a missing row means someone is refused at check-in.

| Section | Column spec lives in |
|---|---|
| Entry | `agent-briefs.md` Track H — one row per **traveller nationality × country** |
| Money on the ground | Track H — the payments table |
| Health | Track H — sections, with vaccination lead times as rows |
| Weather and daylight | **Matrix 12 below** |
| Language | Track L |
| Tickets and rights | Track K |
| Law, scams and safety | Track J |

**The rule that governs the eleven matrices governs these too:** the column list is the deliverable's column list, unverified cells are marked rather than dropped, and every row carries its source. **If an agent returned a table for a section, print a table.** Prose belongs around it, not instead of it — a confident paragraph reads as finished, which is exactly why nobody caught either failure above.

## Contents

1. [Flight options](#1-flight-options)
2. [Mode comparison](#2-mode-comparison)
3. [Whole-path](#3-whole-path)
4. [Lodging](#4-lodging)
5. [Excursions](#5-excursions)
6. [Food](#6-food)
7. [Nearby and day trips](#7-nearby-and-day-trips)
8. [Distances and travel times](#8-distances-and-travel-times)
9. [Budget scenarios](#9-budget-scenarios)
10. [Points and booking channel](#10-points-and-booking-channel)
11. [Best time to visit](#11-best-time-to-visit-flexible-dates-only)
12. [Climate and daylight](#12-climate-and-daylight)

---

## 1. Flight options

The core matrix. Non-stop options first, then one-stop, sorted by all-in cost within each group.

**Every fare class gets a row or a sub-row** — basic economy, standard economy, premium economy, business, first where it exists. This is the point of the matrix: basic economy is frequently a false floor once a bag and a seat are added back, and business is sometimes a far smaller premium than expected on a given route. Neither is visible unless the classes sit side by side.

| Column | Contents |
|---|---|
| **Option** | Short label used in the itinerary and checklist. **Pinned** |
| **All-in price** | Base fare + bags + seat selection + fees, per traveller, both currencies. **Pinned** — the comparator every row is judged on |
| **Book direct** | The carrier's own booking page, immediately after the price |
| Routing | `JFK → NRT` or `JFK → ICN → NRT` |
| Stops | 0 / 1 / 2 |
| Airline + aircraft | Carrier and equipment — a 787 and a 757 on the same transatlantic route are different trips |
| Dep / Arr | Local times both ends, with the date, plus arrival-day offset (`+1`) |
| Flight time | In the air |
| **Door-to-door** | Home to lodging, including transfers and a realistic airport buffer. The number that actually matters |
| Fare class | Basic economy / economy / premium / business / first |
| What's included | Carry-on and checked allowance, seat selection, changes, upgrade eligibility, points earning rate, lounge, seat type on the long leg (lie-flat / angled / recliner) |
| **Ticket structure** | **One ticket (single PNR) or separate tickets.** On separate tickets a missed connection is entirely yours — no rebooking, no duty of care, fare gone, bags not through-tagged. Self-transfer products look like ordinary connections and are not. This column decides bookings and belongs next to the price, not in a footnote |
| **Compensation regime** | EU261 / UK261 / APPR / DOT / none, and what a long delay or cancellation is worth. **Mark itineraries that fall outside every regime as a trap row** — a $40 saving that gives up a potential €600 entitlement is a bad trade that the fare comparison alone will never reveal |
| Layover city + duration | Blank for non-stop |
| Connection mechanics | Terminal change, whether security or immigration must be re-cleared, and whether the published minimum connection time is realistic for that specific pairing |
| Explorability | Score for the layover city (see matrix 7 logic) — or `terminal only` with the reason |
| Change / refund | The real terms, not the marketing phrase |
| **Airport → lodging** | Cost band and time from *that* airport to the actual lodging or first activity, plus mode. Required whenever a metro has more than one usable airport — a cheap fare into the far airport routinely loses once a $70, 90-minute transfer is counted |
| Award option | Points price if applicable, cross-referenced to matrix 9 |

Follow with a short note on what date flexibility is worth in money, if dates are flexible.

## 2. Mode comparison

Air vs. rail vs. drive vs. bus vs. ferry for the same leg. Build one per significant leg.

| Column | Contents |
|---|---|
| Mode | And operator |
| All-in cost | Including bags, seat fees, fuel, tolls, parking, insurance — whatever applies to that mode |
| **Total time** | Door to door, including check-in, security, station transfers, and traffic realism |
| Frequency | Departures per day, and the last one |
| Comfort | Seat pitch, ability to work, food, noise, whether it is restful or draining |
| Luggage | What you can bring and what you have to carry |
| **Luggage forwarding** | Whether a service covers this leg: cost, drop-off deadline, delivery window, reliability. This changes which modes are realistic |
| Flexibility | Change and cancel terms, walk-up availability |
| Scenery | Whether the journey is itself worth something |
| Stops possible | What you can break the trip at en route — the strongest argument for rail and driving |
| Booking window | When it opens and when the cheap fares vanish |
| **Link** | The operator's own booking page — the national rail site, the coach company, the ferry line, the rental supplier. Not the aggregator, which is where the fare comparison came from but not where the terms live. For rail passes, link the pass's official page next to the break-even arithmetic |

Note rail passes explicitly with the break-even arithmetic against point-to-point tickets. Passes lose more often than they are marketed to.

## 3. Whole-path

End-to-end routings scored against each other. This is the matrix for the "should the whole trip be shaped differently" question.

Rows are complete alternatives: A→C direct · A→B→C with a stopover · open-jaw (fly into one city, out of another) · rail in, fly out · a loop hitting three cities · the wishlist-extension version.

| Column | Contents |
|---|---|
| Path | The full shape, with modes |
| Total transit cost | All legs, both currencies |
| Total transit time | All legs, door to door |
| Days consumed by travel | Days that are mostly transit rather than trip |
| Cities / regions gained | What this shape gets you that the others do not |
| Lodging implications | More check-ins, more nights, more bag-hauling |
| Hassle | Extra bookings, visa or transit-visa exposure, missed-connection risk, one-way car fees |
| Wishlist hit | Whether this path picks up something from the user's wishlist |
| Net verdict | Worth it for whom |
| **How to book it** | Which rows from the flight and lodging matrices compose this path, plus the link to the search that actually produces it — a multi-city or open-jaw query rather than two separate round-trip searches, since that is the part people can't reconstruct on their own |

## 4. Lodging

Hotels and homeshares appear in **one table, priced on the same all-in basis** — that comparison is the whole point, and it disappears if they are split into separate lists.

| Column | Contents |
|---|---|
| **Property** | Name and type (hotel / apartment / homeshare / ryokan / hostel), and the platform. **Pinned** — the row is meaningless without it once the table scrolls |
| **Per person / night** | **Pinned alongside the name, because it is the only figure comparable across rows.** Stays differ in length and configuration — a four-night two-room booking and a one-night ryokan have totals that cannot be set against each other, while these can. Derived from the all-in total, not from a headline rate. **Only meaningful between rows whose bed configuration actually matches the party**: a per-person figure computed off a shared bed is not a cheaper option, it is a different one |
| **Book** | The operator's own link, immediately after the price. A reader who has decided from the first two columns should not scroll twenty more to act. For a rejected row, say **Rejected** here rather than leaving a live link to something you are advising against |
| **All-in total** | For the whole stay, after resort fees, city and tourist taxes, parking — and for homeshares, **cleaning and service fees divided across the actual number of nights**. A $90 listing with a $150 cleaning fee is $140/night over three nights, and the nightly rate on the search page is fiction. Both currencies |
| Type | Hotel, serviced apartment, ryokan, homeshare — and how many rooms the booking is |
| Neighborhood | And in one phrase what that neighborhood is like |
| **Bed configuration** | **The field that invalidates every other one if it is wrong.** Explicit, never an occupancy number: "2 rooms × 2 single beds = 4", "1 room, 4 separate futons". **Room count is not bed count** — most markets sell a room type that reaches its stated occupancy only by two people sharing, and it is usually the cheapest row in the table. Where the party doesn't share, those **fail: show them struck through with the reason, not deleted**, or the reader rediscovers them on the booking site and assumes they were missed. `BED CONFIG UNVERIFIED` where the listing won't say |
| Homeshare checks | Only for homeshares: short-term-rental **legality and licence number** in that city (unlicensed listings get cancelled, sometimes days out), check-in method and what happens on a late arrival, and whether anything about the listing looks like a scam — no review history, off-platform payment requests, price far below market |
| What it includes that the other doesn't | Hotels bring breakfast, housekeeping, a front desk, and a late-arrival guarantee. Homeshares bring a kitchen, laundry, separate bedrooms, and space. Name the trade rather than burying it |
| **Pool** | Yes/no, and if yes: indoor or outdoor, heated, hours, and **confirmed open on the travel dates** — seasonal closures and renovations are common and are the worst way for this to go wrong. Note when it is plunge-sized rather than swimmable. **In warm destinations this column carries real weight** (see below) |
| **A/C** | Never assume it. Much of Europe, older Japanese stock, and heritage properties have none, or have it only in some rooms. Note whether it is room-controllable or on a building schedule |
| **Lift** | And which floor. A fourth-floor room up stairs is a different proposition with luggage, and old European buildings routinely have no lift |
| **Gym** | Hours — many are 24-hour, many close at 22:00, and a few are 06:00–09:00 only, which is useless to most people. Whether it costs extra. And what is **actually in it**: "fitness centre" covers both a real gym and one treadmill in a converted storeroom, and only photos or recent reviews tell you which |
| **Spa, sauna &amp; baths** | The single most under-weighted amenity in most lodging research, and a genuine quality-of-life item on a long or cold trip. Note the type — spa, sauna, thermal or hot-spring bath, hammam, plunge pool — whether it is **free to guests or charged** (often a per-visit fee even at a property that advertises it), the hours, whether it is gender-separated or mixed, and any **rule that would exclude a member of the party** (tattoo policies, swimwear requirements, age limits). Where a destination has a bathing culture, a property with a proper bath at business-hotel prices beats a plainer room at the same rate, and the recommendation should say so |
| **On-site food &amp; drink** | Restaurant, bar, café, room service **and its hours** — plus the honest verdict on whether any of it is worth eating in. This matters most in two specific cases: a **late arrival** when nothing outside is open, and a **neighborhood that is dead at night**, where "there's a restaurant downstairs" changes the whole stay. Note the last order time; a hotel restaurant that stops serving at 20:00 is not a fallback |
| **Other amenities** | Kitchen (and what is actually in it), laundry — in-unit, facility, or paid service — Wi-Fi quality not just presence, parking and its nightly cost, breakfast and its hours, luggage hold before check-in and after checkout, fridge, safe, bath vs shower only, balcony, soundproofing where reviews raise it, pet policy, and accessibility features where the party needs them |
| Direct vs. OTA | The delta, and what the direct rate includes that the OTA rate does not — plus whether the OTA booking earns points and elite recognition at all |
| Included | Breakfast, airport shuttle, transit pass, lounge, late checkout |
| Transit & walk access | Nearest station and walk time, walkability of the immediate area, and whether there is anywhere to eat nearby at night |
| Airport transfer | Cost and time from the arrival airport |
| Cancellation | Free-until date, or non-refundable |
| Platform score | With review count |
| **Independent review read** | Google Maps rating and count, plus what Reddit, forums, and local-language reviews say. Separate column from the platform score on purpose |
| **Complaint themes** | The specific recurring complaints — noise, thin walls, slow lifts, the block after dark. More useful than any number |
| **Neighborhood safety** | With the source. Distinguish *actually dangerous* from *unpleasant after dark* from *dead at night* from *far from everything* — these get conflated constantly and only one is a safety issue. For a property with no neighbourhood to speak of — a mountain ryokan, an island resort — relabel this **Setting** and describe what is actually around it |

**Where the same section holds several lodging types**, keep these column positions and adapt the labels: *On-site food* becomes **Dinner and breakfast** for a ryokan where the meals are the reason to go, and gains room for what the kaiseki actually is; *Direct vs. OTA* is where a direct-booking discount belongs; and a **Season note** column earns its place wherever an ingredient, a road, or a facility opens or closes on a date near the stay.

**The caption carries the method.** Dates, party size, any hard constraint applied as a filter, the source and the date it was pulled, and — where cells are empty — one line saying that blanks are marked rather than dropped. A reader who lands on a table mid-page should be able to tell from the caption alone what was compared, on what basis, and how much of it is confirmed.

**Verify amenities against photos and recent reviews, never the checkbox.** OTA amenity lists are generous and stale — they are where a drained seasonal pool, a broken lift, a "kitchenette" that is a kettle, and a gym consisting of one exercise bike all survive indefinitely. The property's own site is better; recent guest photos and reviews are best, because that is the only place a facility being *closed for renovation on your dates* actually surfaces. Any amenity load-bearing enough to influence the pick gets confirmed this way before it earns a recommendation.

**Warm destinations: rank a usable pool above an equivalent property without one.** Where the climate research puts average highs at or above roughly 27°C / 80°F during the stay, or the trip is beach- or tropical-shaped, a pool stops being a luxury and becomes what makes the hottest part of the day usable. Say so in the recommendation rather than leaving the reader to spot it in a column — and where the otherwise-best option has no pool, price the trade honestly: a nearby beach, a public lido, or a day pass at another hotel sometimes covers it, and that is worth checking rather than assuming.

## 5. Excursions

| Column | Contents |
|---|---|
| **Experience** | And what it actually is. **Pinned** |
| **Price** | Both currencies, **per person**, noting group discounts. **Pinned** — the comparator across rows |
| **Book direct** | The operator's own page, immediately after the price. Where a marketplace listing resells an operator's own tour, link the operator |
| Operator | Direct operator, and whether the marketplace listing is a resale |
| Duration | Including transit to the start point |
| **Transport included** | What the tour covers — this feeds back into the ground-transport plan and can make an expensive tour the cheap option |
| Booking lead time | And whether it sells out; permit and lottery windows called out separately |
| Cancellation | Real terms, and weather policy for outdoor activities |
| Season / crowd notes | Best time of day, closure days, last admission |
| Platform rating | With count |
| **Independent review read** | Google Maps and community consensus, separate from the selling platform's rating. Flag operators whose off-platform reputation contradicts their listing |

## 6. Food

**Open this matrix with the water and street-food verdict**, in one or two lines, before any recommendation. It is stated in the health section too, and that repetition is deliberate — this is where someone is actually deciding what to put in their mouth, and a warning three sections away is a warning that didn't land.

| Column | Contents |
|---|---|
| **Spot or dish** | The specific place, and what to order there. **Pinned.** Give the name exactly as the source has it, so it can be machine-verified |
| **Price band** | Both currencies, per person. **Pinned** |
| **Link** | The venue's own site or social page, and the **reservation link** where one is needed — the specific booking platform, not "call ahead". For a market or a street-food cluster, a map link to the actual location, since the address alone is often unhelpful. Where a place genuinely has no web presence — true of the best sodas, stalls and family kitchens — write `no online presence` and give the map pin instead |
| Tier | Must-try / established name / local favorite / **street food**. Aim for at least a third in the last two |
| Neighborhood | And which itinerary day it fits |
| **Address** | The verified street address as printed by the venue or the local platform. This is what a places lookup resolves against, and a paraphrased name with no address cannot be checked |
| Reservation | Needed or not, platform, and **how far ahead booking opens** — some open exactly 30 days out at a set hour and fill in seconds |
| Hours & closed days | From the venue's own page, not a stale aggregator |
| **Safety note** | Only where it applies, and only concretely. Water-dependent items to skip if the tap isn't potable — ice, fresh juice, raw herbs and salad, unpeeled fruit — and for stalls, whether it's cooked to order in front of you. Leave this cell blank where there is nothing real to say rather than filling it with generic caution, which trains the reader to ignore the column |
| Practicalities | Cash only and nearest ATM, queue only, no English, dietary suitability |
| Consensus | Which sources agree, and whether the marketing and the locals disagree |
| **Still open?** | Confirmed against a places lookup where one is available, not just the presence of a listing. **A permanently-closed venue that still ranks well in search is the commonest way a food list goes wrong**, and reading the listing will never catch it |

Where street food is safe, **it belongs in this matrix as a proper tier, not a footnote** — in much of the world it is the cuisine, and routing a traveller into restaurants out of vague caution costs them the best eating in the destination. Where it isn't safe, say so with the reason and point to the same dishes in a safer setting.

## 7. Nearby and day trips

| Column | Contents |
|---|---|
| Place | And the one-line reason to go |
| Type | Day trip / stopover / layover excursion / multi-day extension / wishlist item |
| Travel time each way | Realistic, with mode |
| Cost each way | Both currencies |
| Time on the ground | What is actually left after transit |
| Added cost vs. base plan | For extensions and detours: money and days |
| Routing that makes it work | Stopover fare, open-jaw, free-stopover program |
| Visa / transit rules | Especially for layover excursions — whether leaving the airport is even permitted |
| **Explorability** (layovers) | Minimum connection time, immigration required or airside-only, airport-to-center time each way, left-luggage availability and hours, realistic time in the city after a safety buffer. Say "stay in the terminal" plainly when that is the answer |
| Worth-it verdict | With the community source behind it |
| **Link** | How to actually get there — the train or bus operator's timetable page, the tour that covers it, or the official site of the thing worth going for. A day trip with no transport link is a suggestion, not a plan |

## 8. Distances and travel times

The matrix that decides whether an itinerary survives the day. Built from **map data**, not estimates. Every pair the itinerary actually puts back to back gets a row: lodging to each excursion, airport to lodging, restaurant to the next thing, each day-trip destination, and any two things scheduled consecutively.

| Column | Contents |
|---|---|
| From → To | The specific pair, named as they appear in the itinerary |
| Distance | Road distance, and straight-line separately if the road route is much longer (mountains, water, one-way systems) |
| Mode | The one they will actually use — not the fastest theoretical option |
| Map time | What the mapping service says |
| **Realistic time** | Map time plus parking, waiting for the bus, the walk to and from the stop, traffic at that hour of that weekday, and the reality that mountain roads and dense city centres run slower than routing engines assume. This is the number the itinerary uses |
| Cost | Both currencies, for the whole party |
| Frequency | For transit and ferries — a 12-minute journey with a 90-minute headway is a 90-minute journey |
| Notes | Last departure of the day, whether it runs on Sundays and holidays, whether the walk is safe after dark, whether it is step-free |
| **Link** | The operator's timetable or journey-planner page for that leg, so the reader can re-check it closer to the date. Timetables change seasonally and this is the column that goes stale fastest |

Two rules that stop this matrix from lying:

- **Never chain map times without buffer.** Three legs of "20 minutes" is not an hour, it is closer to ninety minutes once you count getting out of the door each time.
- **Flag any pair the plan treats as adjacent but isn't.** Two sights "both in the old town" can be forty minutes apart uphill. That is exactly the finding this matrix exists to surface.

## 9. Budget scenarios

Same trip, three ways. Rows are cost categories, columns are the three scenarios.

| Category | Shoestring | Balanced | Splurge |
|---|---|---|---|
| Flights | | | |
| Ground transport | | | |
| Lodging (× nights) | | | |
| Food | | | |
| Experiences | | | |
| Misc (SIM, tips, entry fees, insurance) | | | |
| **Total, both currencies** | | | |
| **Per person per day** | | | |
| What changes | The specific trade in each — which is often one or two decisions, not uniform belt-tightening | | |

## 10. Points and booking channel

| Column | Contents |
|---|---|
| Booking | Which flight or hotel from the matrices above |
| Cash price | Both currencies |
| Award price | Points required |
| Cash still payable | Taxes and **carrier-imposed surcharges** — on some programs these exceed the value of the points, which makes an award booking a bad deal that looks free |
| **Cents per point** | For this specific redemption |
| Program baseline | That program's typical valuation, so a bad redemption is visibly bad next to it |
| User's program(s) | Which held balance can cover it, directly or via transfer |
| **Transfer path** | Source → partner, ratio, transfer time (instant vs. days matters when space is moving), live bonus if any. Note that transfers are one-way and irreversible, and space should be confirmed first |
| Availability | Award space on the actual dates, and fare-class capacity |
| **Restrictions & fees** | Blackouts, minimum stay, partner-only rules, change/cancel/redeposit fees, expiration and activity rules, transfer minimums and increments, family pooling, points-plus-cash caps |
| Elite benefits triggered | Bags, lounge, upgrade odds, late checkout, waived resort fees |
| Points earned by channel | Direct vs. OTA vs. portal — many OTA bookings earn nothing and forfeit status recognition |
| **Burn or earn** | The verdict, in plain words |
| **Link** | Where the award is actually booked — the issuing program's own search or call-centre page — plus a **further-reading link to that program's terms**, since the restrictions summarized in one cell (surcharges, redeposit fees, expiration, transfer minimums) are where the value is really decided and the cell cannot hold them all |

### 10b. Discounts and savings, everything else

Points research that stops at flights and hotels leaves most of the trip unoptimized. One table for every other line item the plan contains.

| Column | Contents |
|---|---|
| Item | The specific booking — this excursion, this rail leg, this car rental, this restaurant |
| Standard price | What it costs booked the obvious way |
| Discount route | City pass, railcard, association or warehouse-club rate, corporate rental code, operator-direct discount, free-admission day, lunch menu instead of dinner, shopping portal, card-linked offer, membership already held |
| Discounted price | And the saving, in both currencies |
| Requires | Membership, advance purchase, a specific day, a minimum group size, an account the user may not have |
| **Verified** | Whether you confirmed the offer live on the operator's own page. An expired or invented promo code that fails at checkout is worse than no code — mark `UNVERIFIED` rather than passing one along |
| **Link** | The page where the discount is actually claimed — the pass's purchase page, the railcard application, the museum's free-day calendar, the operator's promotions page. A saving the reader cannot find how to claim is not a saving |

Two things this table must do honestly. **City passes and tourist cards get real arithmetic** — list what the itinerary already includes, what the card covers, and whether it actually wins; they lose more often than they are marketed as winning, and saying so is a genuine finding. And **card-linked offers are account-specific** — report what typically appears and tell the user to check their own account, never assert that an offer is sitting there.

## 11. Best time to visit (flexible dates only)

Build this whenever the user said their dates are flexible by weeks or open. Rows are months or named windows; the job is to make the trade-off between price, weather, and crowds visible in one place so a three-week shift can be argued for on evidence.

| Column | Contents |
|---|---|
| Window | Month or named season, with the local name if there is one (veranillo, shoulder, monsoon, Golden Week) |
| Weather | Temperature range, rainfall, humidity, daylight, sea temperature — the numbers, not adjectives. **Median plus tail frequency, not bare ranges** (see matrix 12), and where a candidate window is a partial month, aggregate over that window rather than letting it inherit the month's figure. Monthly bins blur exactly the distinction this matrix exists to draw |
| Crowds | High / shoulder / low, and what that means concretely: queue lengths, whether reservations are needed, whether the good places are booked out |
| Price index | Flight and lodging cost relative to the cheapest month, as a multiple or percentage |
| Only-then | What is available *only* in this window — festivals, wildlife, blossom or foliage, a pass that runs seasonally, a road or trail that opens |
| Closed-then | What shuts: seasonal closures, monsoon shutdowns, ferry timetables, mountain passes, whole towns that hibernate |
| Locals say | The months residents themselves name as best, which frequently differ from the tourist high season |
| Verdict | Recommended / acceptable / avoid, with the reason in one line |
| **Link** | The climate data and the festival or season calendar behind the row, so a reader arguing for a date shift has the evidence rather than your assertion |

Budget scenarios (matrix 9) is the one table with no link column — its rows are cost categories, not bookable things. Every other matrix has one.

Close with a **dated recommended window** and a direct comparison against whatever the user originally proposed: what moving would cost or save, and what it would gain or lose. A better trip found after the flights are booked is not a finding, it is a regret.

## 12. Climate and daylight

**Built on every trip**, unlike matrix 11 which only builds when dates are flexible. That asymmetry is why this matrix exists: a locked-date trip previously had no climate spec at all, and the section shipped as three rows of monthly normals plus a paragraph of hedging.

Two tables. Rows are every base plus any day-trip destination whose conditions differ materially — which in practice means anywhere at a different elevation or on a different coast.

**Table A — Conditions over the window**

| Column | Contents |
|---|---|
| Place | Base or day-trip destination |
| Avg high | Aggregated over the **actual travel dates**, both units |
| Avg low | As above |
| Chilly night | The low that occurs roughly one year in ten. **This is what to pack for**, not the average — an average low nobody experiences is a worse guide than a cold night they might |
| Extreme recorded | Coldest and warmest in the sample, so the true range is visible |
| vs published monthly normal | The delta, where material. **This column is the finding.** It tells the reader that the figure they will find on every other site is wrong for their dates, and roughly by how much |
| Data point | What the lookup actually resolved to, **including elevation**, flagged wherever it doesn't represent the place |

**Table B — Rain, daylight and disruption**

| Column | Contents |
|---|---|
| Place | As above |
| Days with rain | Share of days recording measurable precipitation, and as a count out of the actual stay — "42%, about 6 of 15" is usable in a way a percentage alone isn't |
| Typical total | The **median**. This is the planning number |
| Mean | Shown alongside, so the gap between them is visible wherever a heavy tail exists. Where the two are close, that itself says the climate is well-behaved |
| Washout risk | Frequency of a single disruptive day across the sample, and what it was. "3 of 16 years saw a 55–145 mm day, all late-season cyclone remnants" is actionable; an average is not |
| Sunset, first → last day | Local time at both ends of the stay, with day length. **Where this crosses below roughly 17:00, it is an itinerary constraint** and the recommendation must say so |

**Caption carries the method**, per the general rule: years sampled, the exact window, the dataset, the query date, grid elevations, and the note that derived figures are labelled as derived.

**Recommendation after the table** covers packing — layers versus real cold, what the destination-specific hazard is — and **the departure-time consequence wherever daylight is short**. A scenic day trip that needs a morning start should be named here as well as in the itinerary.

**Label adaptation applies**, as it does for lodging variants: a tropical destination replaces *Chilly night* with humidity and heat index, a monsoon destination replaces *Washout risk* with wet-season onset probability, a high-latitude winter trip promotes daylight to the first table. **Same column positions, adapted labels** — the skeleton is what makes several of these readable side by side.
