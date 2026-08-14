# Agent briefs

One brief per research track. Paste the **shared preamble** plus the track brief into the `Agent` prompt, substituting the trip parameters. Spawn all agents of a wave in a single message, `run_in_background: true`, with the `model` from the skill's model policy.

## Contents

- [Shared preamble](#shared-preamble)
- [A — Air](#a--air-model-sonnet)
- [B — Ground](#b--ground-model-haiku)
- [C — Lodging](#c--lodging-model-sonnet)
- [D — Experiences](#d--experiences-model-haiku)
- [E — Food](#e--food-model-haiku)
- [F — Community sentiment](#f--community-sentiment-model-haiku)
- [G — Corridor scout](#g--corridor-scout-model-sonnet-second-wave)
- [H — Entry, health and climate](#h--entry-health-and-climate-model-sonnet)
- [I — Points, rewards and discounts](#i--points-and-rewards-model-sonnet)
- [J — Customs, law, stability and self-protection](#j--customs-law-stability-and-self-protection-model-sonnet)
- [K — Fare rules, passenger rights and airport mechanics](#k--fare-rules-passenger-rights-and-airport-mechanics-model-sonnet-second-wave)
- [L — Language and communication](#l--language-and-communication-model-haiku)

Twelve tracks, A through L. The model per track is in the heading and in SKILL.md §4; the two must agree.

**K and L are conditional.** K runs when the itinerary connects or spans more than one carrier; L runs when the destination's main language is not one the traveller speaks. Both always run at exhaustive depth. When either is skipped, **say so in the deliverable** — a silently omitted track looks identical to one that found nothing.

---

## Shared preamble

> You are researching one track of a travel plan. Another agent is synthesizing your findings alongside the other tracks, so **return raw sourced findings, not a polished narrative** — a markdown table plus a notes block. Do not write an itinerary or a recommendation letter.
>
> **Trip parameters:** [origin] · [destination(s)] · [dates and flexibility] · [party size and ages] · [budget band] · [pace and interests] · [constraints] · [passport nationality per traveller] · [preferred currency]
>
> **Before you start, read two files in the `travel-agent` skill directory:**
>
> - `references/research-rules.md` — the standard your findings will be held to. Non-negotiable.
> - `references/source-map.md` — your source starting points. Read the section for your track, cover every class of source listed, and find the local equivalents it misses.
>
> **The rules that decide whether your work is usable:**
>
> 1. Load your tools first: `ToolSearch(query: "select:WebSearch,WebFetch", max_results: 5)`. If a site blocks a plain fetch, fall back to the in-app browser (`mcp__Claude_Browser__preview_start` with the url, then `get_page_text`).
> 2. **Everything comes from a live fetch you performed just now.** Never state a price, schedule, hour, or availability from memory. Every row carries a source URL and today's date.
> 3. Anything you could not verify live is labeled `UNVERIFIED` with a note on what you tried. A gap is more useful than an invention. Never invent flight numbers, addresses, phone numbers, prices, or — in the health, entry and legal tracks — rules.
> 4. Prices in **local currency and [preferred currency]** both, all-in rather than headline, with the FX rate and where you got it.
> 5. Check the **operator's own site** alongside any aggregator, and report the difference.
> 6. Check everything against **the actual travel dates and weekdays** — holidays, closures, seasonal schedules, festivals.
> 7. Where sources disagree, report both and say which is more current or more authoritative. Disagreement is a finding, not a problem to smooth over.
> 8. Date your community sources. A 2019 consensus is not current.
> 9. Search in the local language where it will help, and translate.
> 10. **Return two kinds of link, and don't confuse them.** The *source* is where you learned something. The **action link** is where the reader books the room, reserves the table, buys the ticket, or reads the actual rule — and it belongs in the row itself, not only in your sources list. Prefer the operator's own URL over an aggregator's; it survives longer and carries the real terms. Where no official page exists, say so rather than linking something that merely looks official.
> 11. **For anything intricate you compress into a phrase** — a fare condition, a visa route, a compensation rule, a programme restriction — also give the **authoritative link** so the synthesis can put it beside the summary. Your one-line version is orientation; the reader may need the source text.
>
> **If you run low on budget, report what you have rather than nothing** — say what you covered, what you did not reach, and what you would check next.
>
> Return: the table specified below, then a `## Notes` block for anything that does not fit a cell (caveats, contradictions, timing traps, things that surprised you), then a `## Sources` list of every URL with what it gave you.

---

## A — Air (model: `sonnet`)

Find every reasonable way to fly this. Non-stop first, then one-stop; only consider two-stop if non-stop and one-stop are absent or absurd.

**Price every fare class, not just the cheapest.** Basic economy, standard economy, premium economy, business, and first where it exists. Basic economy is routinely a false floor — once a bag and a seat assignment are added back it can lose to standard, and that only shows when they sit side by side. On some routes business is a much smaller premium than expected. For each class record what the fare actually includes: carry-on and checked allowance, seat selection, changes and cancellation, upgrade eligibility, points earning rate, lounge access, and lie-flat vs. angled vs. recliner on the long leg.

Check meta-search **and** the airline direct, and report the delta. Check the low-cost carriers on the route separately — many never appear in meta-search at all.

If dates are flexible, scan the ±window and report what the flexibility is worth in money.

When the origin or destination metro has more than one usable airport, cover each — and for each, get **the cost and time from that airport to the city center or the likely lodging area**: taxi/rideshare fare band, train or bus fare and journey time, distance, whether hotel shuttles serve it. A cheap fare into the far airport regularly loses once a $70, 90-minute transfer is counted.

For every itinerary with a stop, record the layover city, the layover duration, the minimum connection time at that airport, and whether the connection is airside-only or requires clearing immigration.

| Option | Routing | Stops | Airline | Aircraft | Dep/Arr (local) | Flight time | Door-to-door | Fare class | All-in price (local / pref) | What's included | Layover city + duration | Change/refund | Airport→city cost & time | Book direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## B — Ground (model: `haiku`)

Every non-flying way to cover the same legs: rail, intercity bus, driving, ferry.

For **rail**, go to the national operator's own site for the real fare and the booking window (advance fares often open 30–90 days out and are a fraction of the walk-up price). Check whether a rail pass beats point-to-point tickets for this specific itinerary and **show the arithmetic** — passes lose more often than their marketing suggests. Seat 61 for how the journey actually works.

For **driving**: distance, drive time with realistic breaks, fuel cost, tolls, parking cost at the destination, one-way drop fees, cross-border restrictions, insurance requirements and what a credit card typically covers, **International Driving Permit requirements** (mandatory in several countries — the counter refuses without one), automatic-transmission availability, and low-emission zones or city driving bans. Note where a car is a liability rather than an asset.

For **ferries**: operator direct, seasonal timetable for the actual dates.

Also research **luggage forwarding and storage** for this destination: door-to-door services (Japan's takkyubin via Yamato or Sagawa; whatever exists locally elsewhere), airport-to-hotel delivery, station coin lockers, and same-day storage networks. Price, drop-off deadline, delivery window, size and weight limits, and **reliability reputation from independent sources**. Say plainly whether it is dependable enough to route an itinerary around — it is in Japan, and much less so in most places.

| Leg | Mode | Operator | Duration | Frequency | All-in cost (local / pref) | Booking window | Comfort/class options | Luggage handling | Stops possible en route | **Operator booking link** | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|

Plus a second table for luggage services: | Service | Route covered | Price | Drop deadline | Delivery time | Size/weight limits | Reliability (source) |

## C — Lodging (model: `sonnet`)

Find 6–10 genuinely different options across the budget band, spread across the neighborhoods that make sense for this trip.

**Cover hotels AND homeshares — both, every time.** Search Airbnb, Vrbo, Booking.com's apartment inventory, and the platforms that matter locally (Vacasa, Plum Guide, Sonder, Kid & Coe, and the regional players — in much of Europe and Asia the site locals actually use is not one of the American ones; find it). For a party of 3+, a stay over a few nights, or anywhere with a kitchen requirement, a whole-home rental frequently wins on both price and space — and just as frequently loses once the fees land. Price both and let the matrix show it.

Homeshares have failure modes hotels do not, and each needs checking rather than assuming:

- **Total cost, not nightly rate.** Cleaning fee, service fee, pet fee, local occupancy and tourist taxes, and any extra-guest charge. A $90/night listing with a $150 cleaning fee is $140/night over three nights. Always report the all-in nightly on the actual number of nights.
- **Short-term-rental legality.** Many cities now ban, cap, or license short-term rentals — New York, Barcelona, Amsterdam, Paris, Kyoto and others — and unlicensed listings get cancelled at short notice, sometimes days before arrival. Check the city's own registration rules and whether the listing shows a registration or licence number. An illegal listing is a cancellation risk, not a bargain.
- **Check-in reality.** Self check-in versus meeting a host, what happens on a late or delayed arrival, whether there is anyone to call at 11pm, and whether stairs, lifts, or luggage access are an issue.
- **Cancellation terms**, which on homeshare platforms are set by the host and are frequently far harsher than a hotel's.
- **Scam listings** — no reviews or suspiciously few, photos that reverse-image-search elsewhere, a host pushing to move payment off-platform (always a scam), prices well below the market. Say plainly when a listing looks wrong.
- **Read the host's reviews, not just the property's**, and look for the recurring complaints: noise, the listing not matching the photos, cleanliness, surprise rules, a neighbourhood that reviews describe differently than the listing does.

For genuine like-for-like comparison, price hotels and homeshares on the same all-in basis and note what each includes that the other doesn't — breakfast, daily housekeeping, and a front desk on one side; kitchen, laundry, separate bedrooms, and space on the other.

**AMENITIES — list them per property, because this is what people actually choose on.** Two travellers looking at the same price pick differently based on whether there is a lift, and the listing rarely makes it obvious. For each option record:

- **Pool** — and the details that decide whether it is usable: indoor or outdoor, heated or not, **seasonal closure or renovation** (a hotel pool closed for the season is worse than no pool, because it was the reason you booked), opening hours, whether it is a real pool or a plunge-sized decoration, rooftop, adults-only, and whether towels are provided.
- **Air conditioning** — do not assume it. Much of Europe, Japan's older stock, and a lot of boutique and heritage properties have none or have it only in some rooms, and in summer that decides the stay. Where it exists, note whether it is per-room controllable or a central system on a building-wide schedule.
- **Lift/elevator** — critical in older European buildings and walk-up apartments. A charming fourth-floor room is a different proposition with three suitcases. Note the floor and whether stairs are unavoidable.
- **Kitchen or kitchenette**, and what is actually in it — a "kitchenette" is sometimes a kettle and a microwave.
- **Laundry** — in-unit, on-site facility, or a service with a per-item charge. Decides how much anyone needs to pack on a longer trip.
- **Wi-Fi** — free or paid, and whether reviews say it actually works. "Free Wi-Fi" that drops constantly is a complaint theme worth surfacing.
- **Parking** — on-site, nearby, or none, and the nightly cost, which is frequently not in the room rate.
- **Breakfast** — included or paid, what kind, and the hours (a breakfast that starts at 8am is useless before a 7am departure).
- **Luggage hold** before check-in and after checkout — small, and it repeatedly decides how a first and last day can be used.
- **Accessibility** — step-free entry, roll-in shower, lift access, where relevant to the party.
- Plus: gym, on-site restaurant and bar, room service and its hours, in-room fridge, safe, bath versus shower only, balcony, spa or sauna, beach access, pet policy, and soundproofing where reviews mention it.

**In warm destinations, prefer a pool — and treat its absence as a real cost.** Where the climate research puts average highs around 27°C / 80°F or above during the stay, or the trip is beach- or tropical-shaped, a pool stops being a luxury and becomes the thing that makes an afternoon survivable when it is too hot to walk around. So:

- Rank properties with a usable pool above equivalent ones without, and say so explicitly in the recommendation rather than leaving the reader to notice.
- **Verify the pool is actually open for the travel dates.** Seasonal closures, renovations, and "under maintenance" are common and are the single most annoying way for this to go wrong. Check recent reviews, not just the amenity list.
- Where the best option on every other measure has no pool, say that plainly and price the trade — sometimes a nearby beach, a public lido, or a day pass at another hotel covers it, and that is worth researching rather than assuming.

Compare **direct vs. aggregator** for each and report the delta: rate difference, member rates, breakfast included or not, cancellation terms by channel, and whether the booking earns points and elite recognition at all. Get to the **all-in nightly cost** — resort fees, city and tourist taxes, and parking are excluded from the headline number on nearly every channel.

Check the property's own page and the airport's page for **complimentary shuttles**. They exist more often than they are advertised and can swing a decision by $60/day.

For each neighborhood, research **safety** properly: government advisories (check two countries' — they disagree usefully), city or police crime maps where published, and area-specific threads on the local subreddit and travel forums. Distinguish clearly between actually dangerous, fine-but-unpleasant-after-dark, fine-but-dead-at-night-with-nowhere-to-eat, and fine-but-a-40-minute-commute-from-everything. These get conflated constantly and only one is a safety issue.

For each property, verify **off the booking platform** — Google Maps reviews (rating, count, and recency), Reddit and forum mentions of the specific property, local-language reviews, and Street View of the actual block. Report the **specific complaint themes**, not a number. On-platform reviews are filtered; a 9.1 on an OTA regularly hides a bad block.

| Property | Type | Neighborhood | All-in nightly (local / pref) | Direct vs OTA delta | **Pool (open on dates?)** | **A/C** | **Lift** | **Other amenities** | Included (breakfast/shuttle/etc) | Transit & walk access | Airport transfer cost & time | Cancellation | Platform score | Independent review read (Google Maps + community) | Complaint themes | Neighborhood safety read | Book direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## D — Experiences (model: `haiku`)

Three things, in this order:

**1. The must-do experiences**, cross-checked against community sentiment so the list is not just what markets hardest. For each: operator, price, duration, **what transport is included in the tour** (this changes the ground-transport math elsewhere in the plan), booking lead time and whether it sells out, cancellation terms, and best time of day for crowds.

Check the **official site** for parks, museums, and monuments — timed entry, lottery systems, permit windows that open months ahead and sell out in minutes, free days, closure days, and last-admission times that are not the closing time.

**2. Festivals, celebrations, and seasonal events** in or near the travel window — national and religious holidays, regional festivals, carnivals, harvests, night markets, sporting fixtures, and natural timing (blossom and foliage forecasts, aurora season, migrations). Also the **experiences unique to this place or this climate** — the thing that cannot be done anywhere else, or cannot be done in another season. Flag anything worth shifting the dates a few days for.

For each festival or cultural event, research the **etiquette**: what to wear, what to bring or offer, photography rules, tipping and gifting norms, whether visitors are welcome to participate or are expected to observe, ticketing or invitation requirements, and behaviors that read as disrespectful locally. Also flag the knock-on effect — festivals fill hotels and raise prices across a wide radius, often months ahead.

**3. Independent reviews for every operator** — Google Maps, Reddit, forums, blogs — separately from the rating on the platform selling the ticket. An operator with 4.9 stars on its marketplace and a wall of complaints on Reddit is exactly the finding to surface.

| Experience | Operator | Price (local / pref) | Duration | Transport included | Booking lead time | Sells out? | Cancellation | Best time/season | Platform rating | Independent review read | Crowd notes | Book direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

Plus: | Festival/event | Dates | Location | What it is | Etiquette & dress | Tickets needed | Effect on prices/lodging | Source |

## E — Food (model: `haiku`)

Three tiers, all three required:

**Must-try dishes** — what this place is actually known for, including the seasonal ones available on these dates, and *why* each matters.

**The established names** — Michelin (including Bib Gourmand, the useful tier), regional awards, Eater-class city guides.

**Where locals actually eat** — the local review platform rather than the international one (Tabelog in Japan, Dianping in China, and the equivalent elsewhere), local-language food blogs, city subreddits, market and street-food guides. Search neighborhood by neighborhood, not city-wide. At least a third of the list should be things that appear on no English top-10.

**STREET FOOD — recommend it or don't, based on the health finding, and say which.** In much of the world the street food *is* the cuisine, and steering a traveller into restaurants out of vague caution costs them the best eating in the destination. Agent H is researching water potability and foodborne risk here; take that verdict and act on it:

- **Broadly safe** — research and recommend it properly. Named stalls and markets, what each is known for, hours (many are evening-only, or open at dawn and gone by nine), which night markets and which streets, how ordering works, and cash expectations. Treat it as a tier of the list, not a caveat at the bottom.
- **Safe with precautions** — recommend it *and* attach the specific precautions to the specific entries: which stalls turn over fast, what is cooked to order in front of you, and what to skip.
- **Genuinely risky** — say so with the reason, and point to the same dishes in a safer setting so the traveller still eats the actual cuisine.

Either way, flag **water-dependent items** wherever tap water is not potable — ice, drinks mixed with tap water, salads and raw herbs, unpeeled fruit, fresh juices. These are how visitors most often get ill, and they appear at every price level: a smart restaurant is not automatically safer than a stall. Repeat the water and street-food verdict in your own notes even though Agent H is also reporting it; this is the one duplication in the research that is deliberate, because it is the thing most likely to actually ruin someone's week.

Practicalities per entry: hours from the venue's own site or social rather than a stale aggregator (permanently-closed is common), reservation platform and **how far ahead booking opens** — some open exactly 30 days out at a set hour and fill in seconds — cash-only, queue-only, closed days, English availability, dietary suitability against [constraints], and where the nearest ATM is for the cash-only spots.

| Spot or dish | Type | Must-try / local-favorite | Neighborhood | Price band (local / pref) | Reservation needed & lead time | Hours & closed days | Cash only? | Consensus (which sources agree) | **Venue link + reservation link** | **Map pin** | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|

For the venue link, give its own site or social page and the actual reservation URL where one is needed. The best entries on your list will have **no web presence at all** — that is expected for family kitchens, sodas and stalls, and is not a reason to drop them. Write `no online presence` and give a map pin instead, since an address alone is frequently not enough to find them.

## F — Community sentiment (model: `haiku`)

The honesty pass. What do people who have actually been there say — including what they say is not worth it?

Sweep Reddit hard (city subreddit, the local-resident subreddit which is separate and more honest, r/travel, r/solotravel, and any country-specific sub), TripAdvisor destination forums, FlyerTalk, Rick Steves' forum for Europe, blogs, YouTube itinerary and "what I'd skip" videos, and tier lists.

Report specifically:

- **Overrated** — heavily marketed, consistently disappointing. Say what people say instead.
- **Underrated** — repeatedly named by residents, absent from the marketing.
- **Tourist traps and scams** — the specific ones, by name and location.
- **Common regrets** — "I wish I'd", "don't do what I did", pacing mistakes, booking mistakes.
- **Contested** — where opinion genuinely splits, and along what line (first visit vs. returning, with kids vs. without, summer vs. winter).

Weight recency and **state the date of every thread you rely on**. A 2019 consensus is not current.

| Claim | Verdict (must-do / skip / contested) | Who says so | Recency | Strength of consensus | Notable dissent | Source |
|---|---|---|---|---|---|---|

## G — Corridor scout (model: `sonnet`, second wave)

Runs **after Agent A returns**, since layover candidates depend on which routings actually exist. Pass A's flight options and the user's **wishlist** into this brief.

Four jobs:

**1. Day trips and easily-reachable places** from the destination — with real each-way travel time and cost, and a worth-it verdict backed by community sources rather than a tourism board.

**2. Layover cities as mini-destinations.** For each layover in A's options: minimum connection time at that airport, whether leaving the airport requires clearing immigration and whether a **transit visa** is needed, airport-to-city-center time and cost each way, left-luggage availability and hours, and what is realistically doable in the actual gap after subtracting a safety buffer. Give each a plain explorability score with the reasoning, and be honest when the answer is "stay in the terminal."

**3. Wishlist matches.** Check the user's wishlist against this trip's geography and routings. For anything reachable — on a viable routing as a stopover, a feasible detour or open-jaw, or close enough for a multi-day extension — work out what it would cost in **money and days** to add. Check **stopover programs and free-stopover fare rules specifically**; several airlines give a multi-day stopover away free on the right fare. Include a short researched list of what to actually do there, held to the same standards as the main destination.

**4. The distance and travel-time matrix.** You own this. Using **map data rather than estimates**, measure every pair the itinerary puts back to back — lodging to each shortlisted excursion, airport to lodging, restaurant to the next thing, each day-trip destination, and any two things scheduled consecutively. The other agents will have returned addresses and neighborhoods; turn those into real numbers.

For each pair record distance, the mode they will actually use, the map's time, and a **realistic time** that adds parking, waiting for the bus, the walk to and from the stop, traffic at that hour on that weekday, and the fact that mountain roads and dense old towns run slower than routing engines assume. Include cost, service frequency (a 12-minute ride with a 90-minute headway is a 90-minute journey), last departure of the day, and whether it runs on Sundays and holidays.

Flag explicitly any pair the plan treats as adjacent but isn't — two sights "both in the old town" can be forty minutes apart uphill, and that is the finding this table exists to produce.

| Place | Why (day trip / layover / wishlist) | Travel time each way | Cost each way (local / pref) | Days needed | Added cost vs. base plan | Routing that makes it work | Visa/transit rules | **How to get there — operator or tour link** | Worth-it verdict + source |
|---|---|---|---|---|---|---|---|---|---|

Plus: | From → To | Distance | Mode | Map time | Realistic time | Cost | Frequency | Last departure | Sunday/holiday service | **Timetable / journey-planner link** | Notes |

## H — Entry, health and climate (model: `sonnet`)

Runs on `sonnet` rather than `haiku` because vaccination requirements and entry rules are places where a confidently wrong answer can end a trip at the check-in desk or the border.

**ENTRY — answer this for the traveller's actual passport, and treat any application as a scheduling constraint.**

Entry rules are passport-specific, and a rule that applies to one nationality frequently does not apply to another travelling on the same itinerary. If the party holds different passports, answer for each — do not assume they are treated alike. The destination government's own immigration page is the authority; the traveller's foreign ministry page is the cross-check. Never rely on a visa-service blog, and never rely on a summary that does not name the nationality it applies to.

For the destination **and every country transited**:

- **Which regime applies** — visa-free, visa on arrival, e-visa, ETA-class electronic authorization, or full consular visa. Note the permitted stay length and whether it can be extended.
- **The application process, step by step**, when one is needed: which official site (there are many convincing paid lookalike sites that charge for free authorizations — name the real one and warn about the copies), what documents are required, whether biometrics or an in-person consular appointment is needed and how far out appointments are currently running, photograph specifications, and whether the passport must be surrendered during processing.
- **Cost and processing time** — official fee, service fees, standard versus expedited timelines, and current real-world processing times rather than the advertised ones. **This is a hard date on the booking checklist**: an e-visa that says "72 hours" and is currently taking three weeks changes when flights should be booked.
- **Transit rules specifically.** A connection can require a transit visa even when you never leave the airport, and some airports route all connecting passengers through immigration, which changes both visa and vaccination exposure. Check this per airport, not per country.
- **Passport validity rule** (six months beyond entry is common, but the destination's stated rule and the airline's enforced rule often differ — report both), **blank page requirements**, **onward or return ticket requirements** and whether they are actually enforced at check-in, proof of funds, proof of accommodation, and any arrival form or health declaration.
- **Departure requirements** — exit fees, departure taxes and whether they are in the fare, and overstay penalties.

Return this as a table with one row per traveller nationality × country, so nothing is silently generalized: | Passport | Country | Regime | Permitted stay | Application needed? | Where to apply (official URL) | Documents | Cost | Processing time (advertised / actual) | Apply by | Source |

**HEALTH — research this properly, it is the section most often waved through.**

- **Required vaccinations**, which are entry conditions rather than advice. Critically, several are triggered by a **country transited rather than the destination** — yellow fever is the classic case, and a two-hour connection in the wrong airport can trigger a requirement needing ten days of lead time. Check the requirement against *every* country on *every* candidate routing, and check whether the exemption for airside transit applies at that specific airport — some airports have no airside transit path at all, which voids the exemption.
- **Recommended vaccinations** and how far ahead each must be given. Anything with a lead time is a scheduling constraint and goes to the top of the booking checklist.
- **Current outbreaks and disease activity — with actual case numbers, regions, and dates.** "Dengue is present" is not a finding; "2,425 national cases as of August, up 18% year-on-year, 305 of them in the province they are visiting, peak season May–November, and the mosquito bites in daylight" is. Check the destination's health ministry and the traveler's public-health authority for current surveillance data.
- **Malaria** — whether prophylaxis is recommended for the specific region and altitude they will be in, not the country as a whole.
- **Altitude** — where the itinerary goes above ~2,500m, acclimatization needs and symptoms.
- **WATER — answer concretely, by region, because it often differs sharply within one country.** Is the tap water potable for a visitor? Note that "safe for residents" and "safe for a visitor whose gut has never met the local flora" are different answers, and say which you mean. Cover: tap water in each place they will stay, ice in drinks (frequently made from a different supply than the tap), fountains and refill stations, whether a filter bottle or purification tablets are worth carrying, whether bottled is genuinely necessary or an upsell, and brushing teeth. Also flag where water is safe but the mineral content or chlorination reliably upsets visitors anyway. Include recent boil-water notices or supply problems if any.

- **FOODBORNE RISK, and specifically street food.** This determines whether the food agent can recommend the best eating in the destination or has to steer around it, so answer it clearly rather than hedging. Research: the destination's actual foodborne-illness picture (traveller's diarrhoea rates, any current outbreaks — hepatitis A, cholera, typhoid, norovirus — with dates), how food hygiene is regulated and whether street vendors are licensed and inspected, and what the informed local and expat consensus is on eating from stalls.

  Then give a **usable verdict, not a disclaimer.** "Be careful with street food" helps nobody. What is needed is: is street food broadly safe here, safe with specific precautions, or genuinely risky? If it is safe — which in much of Asia, Latin America and the Middle East it is, and where the street food *is* the cuisine — say so plainly so it can be recommended. If precautions apply, name the real ones: high turnover stalls with queues, food cooked to order in front of you rather than sitting out, avoiding raw items washed in tap water, peeling your own fruit, ice, unpasteurised dairy, shellfish, and specific dishes with a known reputation. If it is genuinely risky, say that and why.

  Also cover: which specific foods carry real risk in this destination regardless of venue, whether restaurant food is meaningfully safer than street food (frequently it is not), what to carry (oral rehydration salts, an antidiarrhoeal, whether a standby antibiotic is standard advice for this region), and when a stomach problem here warrants a doctor rather than waiting it out.

  **This finding is passed to the food agent and to the synthesis.** Mark it clearly so it cannot be missed.
- **Prescription medications** — anything routine at home that is a controlled substance or outright banned there, and what documentation to carry. People get detained over ADHD and codeine medication.
- **Practical care:** nearest real hospital to each base and how far it is, clinic and pharmacy availability, emergency number, and whether travel insurance is **required for entry** (some countries do require proof).
- **Medical evacuation reality** — for remote, high-altitude, island, or small-craft destinations, what an evacuation would actually involve and roughly cost, and whether that makes dedicated evacuation cover worth buying. Note that agent I is separately checking what the traveller's existing cards already provide, so do not research card benefits here — establish what the destination demands, and let I establish what they already hold.

**JET LAG AND ARRIVAL DAY.** Time-zone difference between origin and destination, direction of travel (eastward is consistently harder to adjust to than westward), local arrival time, and how many hours the traveller will have been awake on arrival. From that, say plainly **whether day one is realistically usable** and what it can hold — this matters because itineraries routinely schedule arrival day as though it were a normal day, and it is not. Include the standard adjustment guidance for the shift size and direction: light exposure timing, when to sleep and when not to, and how many days to full adjustment. On a red-eye arrival also check whether early check-in or a day room is available at the shortlisted lodging, since a 7am arrival against a 3pm check-in is a real problem.

**MONEY AND PAYMENT — answer "can I just use my card here?" concretely.** This is one of the most practical things a traveller needs and one of the most commonly hand-waved. Report:

- **Current FX** with the date and source.
- **The cash verdict, stated as one of three things**, not as a hedge: *cash is essential* (you will be stuck without it), *cash is strongly recommended* (cards work in most places but enough gaps exist that you should carry some), or *cards are fine* (you can realistically travel cashless). Say roughly how much cash to carry and for what — Japan and Germany are far more cash-driven than visitors expect, while Sweden and much of Korea are nearly cashless.
- **Which card networks are actually accepted.** Visa and Mastercard are near-universal; **American Express and Discover are refused far more often than their holders expect**, and in some countries they are effectively useless outside chain hotels. Note JCB in Japan, UnionPay in China, and any local network. If the traveller's main card is Amex, that is a finding they need before departure, not after.
- **Chip-and-PIN versus signature.** US-issued cards often lack a PIN, which fails specifically at **unattended kiosks** — rail ticket machines, petrol pumps, motorway tolls, parking, bike-share. Note where this bites and whether a PIN can be set in advance.
- **Contactless and mobile wallets** — whether tap is standard, and whether Apple Pay and Google Pay are widely accepted.
- **Local payment apps, and critically whether a visitor can actually use one.** In several countries a domestic app is the default and cash is fading behind it — Alipay and WeChat Pay in China, UPI in India, PIX in Brazil, Swish in Sweden, MB Way in Portugal, Bizum in Spain, Twint in Switzerland, Blik in Poland, PromptPay in Thailand, PayNow in Singapore, M-Pesa in Kenya, Interac e-Transfer in Canada. **The decisive question is whether the app requires a local bank account, national ID, or local phone number** — most do, which makes them unusable for a tourist regardless of how dominant they are. Where a foreign-card workaround exists (Alipay and WeChat now support international cards with limits), say what it is, what it costs, and what the limits are. Where there is no workaround, say that plainly so the traveller plans around it with cash.
- **Where cash is still required even in card-friendly countries** — small vendors, markets, taxis, temples and shrines, rural areas, tipping, luggage lockers, public toilets, and small restaurants. Name the specific categories rather than generalizing.
- **ATMs** — which banks are foreigner-friendly and which reject foreign cards outright (a real problem in Japan, where many bank ATMs do not take them and convenience-store ATMs are the answer), withdrawal limits per transaction and per day, fees on both ends, whether cards work in ATMs at the airport, and whether to use a debit rather than a credit card to avoid cash-advance interest.
- **Dynamic currency conversion** — where terminals and ATMs offer to charge in the traveller's home currency. **Always decline**; the built-in rate is consistently poor. Note that this is offered aggressively in some markets.
- **Practicalities:** whether large notes get refused, whether change is a problem, whether to bring home currency to exchange or just withdraw locally, and how tips are paid (many countries have no way to tip on a card).
- **VAT refund** process, thresholds, and whether it is worth the airport queue.

| Question | Answer for this destination | Detail | Source |
|---|---|---|---|
| Is cash necessary? | essential / strongly recommended / optional | How much to carry, and for what | |
| Which networks work? | | Amex/Discover acceptance specifically | |
| PIN needed? | | Where signature-only cards fail | |
| Contactless / Apple Pay? | | | |
| Local payment app required? | | **Can a tourist actually register?** | |
| ATM strategy | | Which banks, limits, fees | |

**Connectivity:** eSIM providers against local SIMs and home-carrier roaming; which transit and ride-hailing apps actually work there.

**Getting around:** transit passes and whether they beat pay-as-you-go for this itinerary, with the arithmetic.

**Dates:** public holidays, school holidays, and closures falling in the window.

**Climate:** normals for these dates — average high and low, rainfall, humidity, daylight hours, sea temperature if relevant, altitude. Plus the live forecast **only if the trip is inside forecast range**, clearly labeled as a forecast with the date pulled; if the trip is beyond forecast range, say so rather than passing climatology off as a forecast. Then turn it into concrete packing guidance tied to the planned activities: layers, rain gear, footwear for the real terrain, adapters, sun and altitude. Include **dress codes** for anything the itinerary might include — temple and mosque coverage rules, jacket-required restaurants, onsen tattoo policies, trail footwear requirements, club door policies.

**BEST TIME TO VISIT — only if the trip parameters say dates are flexible by weeks or open.** Build a month-by-month picture: weather, high/shoulder/low season pricing for flights and lodging, crowd levels, what is available only in certain months (festivals, wildlife, blossom or foliage, seasonal passes, roads and trails that open), what shuts seasonally, and **the months locals themselves name as best** — which frequently differ from the tourist high season. End with a dated recommended window and the reason.

Return as sections rather than one table, with `Health`, `Packing list`, and `Dress codes` subsections, plus a `Best time to visit` table if dates are flexible.

## I — Points and rewards (model: `sonnet`)

The user's programs and rough balances are in the trip parameters. Work against the flights and hotels the other agents shortlisted.

For each shortlisted option: cash price, award price in points, and the **cents-per-point value of that specific redemption** next to that program's typical baseline valuation, so a bad redemption is visibly bad. Which of the user's programs can cover it, and through which partner.

**Transfer paths:** which transferable currency the user holds feeds which airline or hotel partner, at what ratio, how long the transfer takes (instant vs. several days matters when award space is moving), and whether a transfer bonus is currently live. Note plainly that transfers are one-way and irreversible, and that space should be confirmed before transferring.

**Redemption limits and fine print** — this is where value is actually decided: award availability and fare-class capacity on the specific dates, blackouts, minimum-stay or partner-only restrictions, **carrier-imposed surcharges and taxes still payable in cash** (on some programs these exceed the value of the points), change/cancel/redeposit fees, points expiration and account-activity rules, transfer minimums and increments, family pooling, and any cap on points-plus-cash.

**Elite benefits** the user's current tier actually gets on these specific bookings — bags, lounge, upgrades, late checkout, waived resort fees — and **which booking channel preserves them**. Many OTA bookings forfeit points and status recognition entirely, which can outweigh a discount.

**Card-linked perks already held:** hotel credits, free-night certificates, portal-only rates, primary rental-car insurance.

**Travel protection the cards already provide** — worth checking before anyone buys a standalone policy, because the overlap is large and most people don't know what they're carrying. Cover: trip cancellation and interruption limits, trip delay (what triggers it, and the per-person cap), baggage delay and loss, missed connection, emergency medical and **medical evacuation** limits, and rental-car coverage tier. Two conditions decide whether any of it applies: **the trip usually must be paid for with that card**, and coverage frequently requires booking through particular channels. State both. Agent H is separately establishing what this destination actually demands — remote or high-altitude destinations can need evacuation cover well beyond a typical card limit — so give the numbers and let the synthesis compare them rather than pronouncing on adequacy here. Card benefit guides published by the issuer are the authority; benefit terms change and blog summaries go stale fast.

| Booking | Cash price (local / pref) | Award price (points) | Cash still payable | Cents per point | Program baseline | User's program(s) that work | Transfer path (ratio, time, bonus) | Availability on dates | Restrictions & fees | **Link to the programme's own terms** | Elite benefits triggered | Points earned by channel | Burn or earn? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

**DISCOUNTS AND LOYALTY BEYOND FLIGHTS AND HOTELS.** Points research usually stops at airfare and lodging, which leaves most of the trip unoptimized. Also cover, for the specific things the other agents shortlisted:

- **City passes and tourist cards** — the museum/transit bundles most cities sell. **Do the break-even arithmetic against the actual itinerary** rather than repeating the marketing: list what the plan already includes, what the card covers, and whether it wins. These lose more often than they are sold as winning, and saying so is a real finding.
- **Rail and transit** — advance-purchase fares, railcards and discount cards (many pay for themselves in two journeys), multi-day transit passes versus pay-as-you-go, group and off-peak fares, and youth/senior/student bands.
- **Car rental** — corporate and association discount codes (CDP/BCD/AWD numbers), membership rates through AAA/CAA, Costco Travel, AARP, or a warehouse club, and whether any of them beat the public rate once the mandatory local insurance is added.
- **Experiences and attractions** — the operator's own direct-booking discount versus the marketplace price, combo and multi-attraction tickets, free-admission days at museums, advance-purchase discounts, and student/senior/military/child pricing. Check the official site for free days before recommending a paid ticket.
- **Dining** — restaurant loyalty and booking programs that earn miles (airline dining programs, OpenTable-class points), prix-fixe and restaurant-week promotions falling in the window, lunch menus that serve the same kitchen at a fraction of dinner prices, and any card-linked dining offers.
- **Card-linked offers** — Amex Offers, Chase Offers and equivalents frequently carry live merchant credits for airlines, hotels, and booking sites. These are account-specific, so report what typically appears and tell the user to check their own account rather than asserting they have one.
- **Shopping portals and cashback** — airline and bank shopping portals that pay miles or cash on bookings made through them, which stack with the booking's own earning.
- **Memberships the user may already hold** — AAA/CAA, Costco, AARP, alumni associations, unions, employer travel programs, museum reciprocal memberships (a home museum membership often gets free entry abroad), and hostel or hotel-brand memberships.
- **Legitimate coupon sources only.** The operator's own promotions page, official newsletter signup discounts, and current published promo codes. Do not scrape sketchy coupon-aggregator sites and present expired or invented codes as live — a code that fails at checkout is worse than none. Verify each against the operator, and mark it UNVERIFIED if you cannot.

| Item | Category | Standard price | Discount route | Discounted price | Savings | Requires | Verified? | **Where it's claimed (link)** | Source |
|---|---|---|---|---|---|---|---|---|---|

Do not log into any account or initiate any transfer. Research published terms and public award-availability tools only.

## J — Customs, law, stability and self-protection (model: `sonnet`)

Four distinct areas. The third and fourth are the ones usually missing, and they carry the worst downside.

**1. Scams and tourist traps — the specific ones, by name and location.**

Not generic advice. Which scams are actually run in this city, how they open, and what the tell is. Cover at minimum: airport and street taxi tricks (meter tampering, "the meter is broken", long-hauling, unofficial cabs), ATM and card skimming and which machines are safe, card-terminal double-charging and dynamic currency conversion, fake police and fake officials, the "it's closed today, let me take you somewhere better" gambit, gem/carpet/tailor shop commissions, spiked drinks and inflated bar bills, rental vehicle damage claims, fake or overpriced "official" guides at monuments, ticket resale scams, and street games. Include the local-specific ones that only exist there.

Then the **legal-but-bad-value traps**: which attractions are heavily marketed and consistently disappointing, which restaurants sit on the main square charging triple, and what locals and repeat visitors say to do instead. Source from Reddit, forums, and recent traveller reports rather than tourism boards, and note the date of each source — scam patterns change.

**2. Customs and traditions — how not to be rude.**

Greetings and physical contact norms, forms of address, tipping norms **including where tipping is an insult**, dining etiquette (who orders, who pays, what is rude to leave, whether to finish the plate), shoes on or off and where, queueing, punctuality expectations, gift-giving, **whether haggling is expected or offensive** and roughly what discount is normal where it is, gestures that mean something different there, religious observance visitors are expected to accommodate (prayer times, fasting months, sabbath closures), noise and public-behaviour norms, and how to behave at any festival, temple, shrine, or ceremony on the itinerary.

**3. Laws that get travellers arrested, fined, or deported.**

Research from the destination's own government and the traveller's foreign ministry — not blogs. Cover:

- **Drugs** — including substances legal where the traveller lives. Cannabis legality at home is irrelevant abroad and this catches people constantly. Note penalties, not just legality.
- **Prescription medications** that are controlled or banned locally, and what documentation to carry.
- **Alcohol** — public drinking, purchase hours, dry days, age limits, and whether being drunk in public is itself an offence.
- **Drones** — registration, permits, outright bans, and confiscation at customs.
- **Photography** — government and military sites, airports, bridges, police, and rules about photographing people, especially children.
- **Vaping and e-cigarettes** — banned outright in several countries with real penalties.
- **Currency** — import and export limits, declaration thresholds, restrictions on taking local currency out.
- **Customs** — what cannot be brought in (food, seeds, meat, certain books or media), and what cannot be taken out (antiquities, coral, shells, protected wood).
- **Dress codes with legal force**, as distinct from cultural expectation.
- **LGBTQ+ legal status and practical safety** — the law, and separately how it is actually enforced, stated factually.
- **Public assembly and protest** rules, and photographing them.
- **Traffic and pedestrian law** — jaywalking enforcement, dashcam legality, drink-drive limits (often far lower than at home, sometimes zero), required equipment, and what to do after an accident.
- **Identification** — whether to carry the passport itself or a copy is acceptable.
- **Policing** — what actually happens when stopped, whether roadside fines are legitimate, where bribery is routine and how travellers are advised to handle it, and the embassy contact process if detained.

**4. Political and local instability, conflict, and disruption.**

Report what is actually happening, with dates and sources, and distinguish clearly between *dangerous*, *disruptive*, and *background noise a resident would shrug at*. The failure modes here run both ways: a plan that ignores a live conflict is negligent, and one that treats every protest as a crisis is useless and insulting to the place.

- **Current advisories** — the traveller's foreign ministry plus at least one other country's, since they weight things differently and the disagreement is informative. Report the level *and* the specific reasoning, and note whether it applies to the whole country or to regions the traveller will never go near. A country-level warning driven by a border region 900km away should not be reported as if it applies to the beach town they're visiting.
- **Armed conflict, insurgency, and organized crime** — where it is active, which regions are affected, whether it touches the itinerary at all, and whether it affects overflight or routing. Some conflicts close airspace and reroute flights without the destination itself being unsafe.
- **Civil unrest and protest** — current movements, what triggers them, where they concentrate, and whether they are peaceful or have turned violent. Note that participating in or even photographing a protest is illegal for foreigners in some countries.
- **Elections, referendums, anniversaries, and political dates falling in the window.** These reliably produce demonstrations, road closures, transport shutdowns, alcohol bans, and occasionally curfews or internet restrictions. Check the political calendar against the actual travel dates.
- **Strikes** — the single most likely form of disruption in much of Europe and Latin America, and the most under-researched. Check for announced or threatened action by air traffic control, airline staff, rail, metro, buses, taxis, port workers, and museum and public-sector staff. Many countries require strikes to be announced in advance, so they are frequently knowable.
- **Border and regional tensions** that could affect crossings, visas on arrival, or a planned side trip into a neighbouring country.
- **Natural-hazard and infrastructure risk** where relevant to the dates: hurricane and typhoon season, wildfire, seismic and volcanic activity, flooding, and grid or water reliability.
- **Practical consequence** — embassy location and contact, registration programs (STEP and equivalents), what travel insurance typically will and will not cover for unrest, and whether any of this makes a refundable booking worth the premium.

Weight recency heavily and date every claim. A 2023 assessment of a fast-moving situation is not current, and saying "as of [date]" matters more here than anywhere else in the research.

| Item | Category (scam / trap / custom / law / instability) | What it is | How it presents | Consequence if you get it wrong | What to do instead | Affects this itinerary? | Source + date |
|---|---|---|---|---|---|---|---|

Then `## Notes` with two short lists at the top: **"things that would get you in real trouble"** — the handful with legal consequences — and **"what could actually disrupt this trip"** — strikes, political dates, seasonal hazards, ranked by likelihood. Both stated plainly and without alarmism. Then `## Sources`.

## K — Fare rules, passenger rights and airport mechanics (model: `sonnet`, second wave)

Runs **after Agent A returns**, alongside G, because every question here is about specific itineraries. Pass A's shortlisted options into this brief. Skip this track entirely on a simple non-stop return with one carrier.

**1. Ticket structure — answer this first, it is the highest-value item in the track.**

For each shortlisted itinerary, determine whether it is **one ticket (single PNR) or separate tickets**, and state the consequence plainly:

- On **one ticket**, a missed connection is the airline's problem: they rebook you, and on longer delays they owe duty of care — meals, and a hotel where an overnight results.
- On **separate tickets**, a missed connection is entirely yours. The onward carrier owes you nothing, your fare is gone, and you buy a new ticket at the walk-up price. Checked bags are not through-tagged, so you reclaim and re-check, which itself needs time and often landside access.

Meta-search sells self-transfer routings (Kiwi-class) that look like normal connections and are not. Where one appears, get the **actual terms of the operator's own guarantee** — what it covers, what it excludes, the claim process, and how long it takes to pay — rather than the marketing line. Flag any itinerary where a modest saving is buying real exposure, and say how much connection time would be needed to make a self-transfer sane.

Also record, per itinerary: the **operating carrier versus the marketing carrier** (codeshares mean the airline on the ticket is often not the one flying, which changes bag rules, seat selection, and who to talk to when it breaks), and whether the fare is a published fare or a consolidator/basic-economy bucket with different change rights.

**2. Compensation rights — which regime governs, and what it is worth.**

Determine the regime for each leg. It follows the **carrier and the departure point, not the traveller's nationality**, which surprises people:

- **EU261 / UK261** — any flight departing the EU/UK, and flights into them on an EU/UK carrier. Amounts by distance, what counts as an extraordinary circumstance, and the re-routing and care obligations that apply even when cash compensation doesn't.
- **Canada's APPR**, and any other regional regime relevant to the routing.
- **US DOT rules** — weaker on delay compensation but with real obligations on refunds, tarmac delays, and bags.

For each itinerary say what is owed for a long delay, a cancellation, and a denied boarding, and how to claim. **Flag explicitly when a marginally cheaper itinerary sits outside every regime** — a $40 saving that gives up a potential €600 entitlement is a bad trade the fare comparison alone will never show.

**3. Schedule changes.** What counts as a material change with this carrier, and what it entitles you to — usually a free rebook onto a different flight, sometimes a full refund even on a non-refundable fare. Airlines rarely advertise this and most travellers accept whatever they are moved to. Note the window for acting.

**4. Baggage on multi-carrier itineraries.** When carriers differ on one ticket, whose allowance applies — the rules vary by alliance and by which carrier issued the ticket, and the answer is frequently not the cheaper carrier's. Check interline baggage agreements, whether bags are through-tagged to the final destination, oversize and sports-equipment handling, and **gate-check risk on regional aircraft**, where a roller bag that fits the mainline cabin will not fit the regional jet.

**5. Airport transit mechanics** for each connection point: which terminals, how to move between them and how long that actually takes (some transfers involve a train or a bus outside security), whether **security must be re-cleared**, whether immigration must be cleared, realistic immigration and security queue times at that airport for that hour, fast-track or priority options and whether the fare or status includes them, and whether the published minimum connection time is realistic or optimistic for that specific pairing.

**6. Lounge access** at each airport on the routing: what the fare class or the traveller's status opens, what a held card opens (Priority Pass and equivalents), paid day-pass options and prices, arrivals lounges where they exist, opening hours against the actual flight times, and — honestly — whether the lounge at that airport is worth the walk. Some are excellent; many are a crowded room with crisps.

| Itinerary | One ticket or separate? | Consequence if the connection is missed | Operating vs marketing carrier | Compensation regime | What a long delay / cancellation is worth | Schedule-change rights | Bag allowance that applies | Through-tagged? | Terminal change | Re-clear security? | Realistic connection risk | Lounge access | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Then `## Notes` leading with **any itinerary that is on separate tickets or outside all compensation regimes**, since those are the findings that should change a booking decision. Then `## Sources`.

## L — Language and communication (model: `haiku`)

Skip this track when the destination's main language is one the traveller already speaks.

**1. What is actually spoken.** Official and regional languages, which dominates in each place on this itinerary (national and regional languages diverge sharply in Spain, India, Switzerland, Belgium, and many others), the script or alphabet, and whether the written form uses characters the traveller cannot decode at all. Note where a language the traveller might expect to be useful isn't — Spanish in Brazil, Mandarin in much of Southeast Asia.

**2. English adoption, broken down by context — never as a single number.** "English is widely spoken" is close to useless because it is true of hotel receptions and false of pharmacies almost everywhere. Rate each separately, from what recent travellers actually report:

hotel front desk · restaurants (and whether that differs between tourist areas and neighbourhood places) · taxis and rideshare · trains and buses, including staff and ticket offices · pharmacies and medical settings · police · shops and markets · rural areas versus the capital · younger versus older speakers.

Flag the gaps that matter most: **being unable to communicate in a pharmacy or with emergency services** is a different order of problem from a menu you can't read.

**3. Signage and machines.** Is transit signage bilingual or romanized? Road signs? Street names? Do metro and rail ticket machines offer an English mode, and do the apps? Are menus translated, photographed, or neither — and is there a picture-menu or plastic-food convention that solves it? Whether station and stop announcements are made in English. This determines how independently someone can move around.

**4. Tools that actually work for this language pair.** Which translation app performs well here (they differ substantially by language — some handle Japanese or Thai far better than others), **which offline packs to download before departure** since roaming may be patchy and some countries block certain services, camera and live translation for menus and signs, handwriting or drawing input for character-based scripts, and whether a local messaging app is the norm for contacting hosts, guides, and restaurants.

**5. Phrases worth learning** — chosen for utility, not phrasebook filler. Greeting and thanks (which carry more social weight in some cultures than travellers expect), please and excuse me, numbers and prices, "do you speak English", "where is the toilet", "the bill please", "I don't understand", directions, and **the dietary, allergy, and medical phrasing the party actually needs** — an allergy written in the local script on a card is worth more than any app. Give pronunciation guidance that a non-linguist can use.

**6. What to be wary of — the part with no mainstream equivalent.** Research honestly:

- **Where speaking English changes the price you are quoted** — real in many markets, and worth knowing before you open with English.
- **Register and formality.** Languages with formal and informal address (tu/vous, du/Sie, Japanese keigo) where a phrasebook gives the wrong one, and where using the casual form with a stranger or an official reads as rude.
- **False friends and mistranslations** that cause offence or confusion, including words that are innocuous in one variety of a language and vulgar in another — this catches Spanish and Portuguese speakers constantly across countries.
- **Gestures** that mean something different or something offensive: thumbs-up, the OK sign, beckoning, counting on fingers, pointing with a finger or foot.
- **Directness.** Whether "no" is said plainly or implied, whether a yes may mean "I heard you", and how to tell a polite refusal from agreement — a genuine source of misunderstanding in much of East and Southeast Asia.
- **Names, titles and honorifics**, and how to address service staff and officials.
- **Taboo topics** — politics, religion, history, money, family questions — that are ordinary small talk elsewhere.
- **Emergency communication** without a shared language: the emergency number, whether operators speak English, whether the destination has a translation or interpreter line, what to write down and carry, and how to ask for help at a pharmacy or hospital.

| Item | Category (language / English adoption / signage / tool / phrase / pitfall) | Detail | Where it matters | Source + date |
|---|---|---|---|---|

Then `## Notes` leading with the **English-adoption summary by context** and the **three things most likely to cause a real problem** for this traveller in this country. Then `## Sources`.
