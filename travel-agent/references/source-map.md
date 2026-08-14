# Source map

Named starting points per domain. They are **classes of source, not a checklist to exhaust** — the goal is coverage of every class for the specific trip, plus the local equivalents these lists miss. In most countries the site locals actually use is not on any English list; find it (search in the local language, ask the local subreddit) and use it.

Every source below is only as good as its date. Carry the URL and the access date with anything taken from it.

## Contents

- [When a source won't load](#when-a-source-wont-load)
- [Query an API before you scrape a page](#query-an-api-before-you-scrape-a-page)
- [Flights](#flights)
- [Rail, road, bus, ferry](#rail-road-bus-ferry)
- [Luggage forwarding and storage](#luggage-forwarding-and-storage)
- [Lodging](#lodging)
- [Neighborhood safety](#neighborhood-safety)
- [Experiences, tours, festivals](#experiences-tours-festivals)
- [Food and drink](#food-and-drink)
- [Community sentiment](#community-sentiment)
- [Points and loyalty](#points-and-loyalty)
- [Weather and climate](#weather-and-climate)
- [Entry, money, connectivity](#entry-money-connectivity)
- [Health, disease and immunizations](#health-disease-and-immunizations)
- [Law, customs and scams](#law-customs-and-scams)
- [Maps, distances and travel times](#maps-distances-and-travel-times)
- [Fare rules, passenger rights and airports](#fare-rules-passenger-rights-and-airports)
- [Language and communication](#language-and-communication)
- [Search patterns that work](#search-patterns-that-work)

---

## When a source won't load

Four failures look alike from the outside and need opposite responses. Treating them all as "blocked" wastes budget retrying the unretryable, and writes off domains that were only partly closed.

| What you see | What it is | What to do |
|---|---|---|
| **403**, or a "checking your browser" interstitial | **Bot protection.** A server-side fetcher has no JS, a datacenter IP, and a non-browser TLS fingerprint — that trips generic anti-automation. Fare and rate pages are defended hardest, because scraping them is a commercial concern. | **Will not clear on retry.** Use labelled search snippets, or a different source entirely. Stop spending budget on it. |
| Works early, then **429 or empty** later in the run | **Rate limiting — frequently self-inflicted**, as sibling agents pile onto the same host from one egress. | Fetch early, keep what you get. The real fix is the concurrency cap in `SKILL.md`, not a workaround. |
| **200 OK** returning a shell, an error string, or nothing useful | **JS-rendered.** Not a block at all — there is simply nothing in the HTML. | Use the in-app browser, which executes JS. A plain fetcher will never work here. |
| **DNS failure, TLS certificate mismatch, genuine 404** | **The site is broken — or you guessed the URL.** | Nothing to work around; mark `UNVERIFIED`. Distinguish "the site refused me" from "I invented a path" — only the first is a source problem. A certificate mismatch is worth reporting to the user; it says something about the business. |

Two distinctions worth carrying:

- **Partial blocks are common — probe before writing off a domain.** One airline served its HTML award pages fine and blocked only a PDF download. One government site blocked its advisory page while its immigration pages worked.
- **Sources that reliably work are as useful to record as ones that don't.** Domestic booking platforms, national meteorological services, and government (`.gov`, `.go.jp`, and equivalents) sites are consistently fetchable — they are less commercially sensitive and therefore less defended. Domestic lodging platforms are also where precise detail lives that international aggregators flatten away.

**This is a living list.** Add what blocks and what works on every run, with the failure type, so the next run doesn't rediscover it. One track lost budget to the same bot-protected restaurant site three separate times in one run.

## Query an API before you scrape a page

For commodity facts — geography, time, weather, currency, holidays — structured data beats scraping, can't be misread, and can't be fabricated. The following are **keyless and verified working**; re-check before relying on them, since free services move and fold.

| Need | Endpoint | Notes |
|---|---|---|
| **Geocoding, and checking a coordinate is where you claim** | `nominatim.openstreetmap.org/search?q=…&format=json` | Descriptive User-Agent, ~1 req/sec. **Use it to verify every coordinate you emit** — an agent once returned map pins in the wrong prefecture, which one lookup would have caught. |
| **Daylight** | `api.sunrise-sunset.org/json?lat=…&lng=…&date=…&formatted=0` | **Returns UTC — convert to local.** Fills the sunrise/sunset gap when the usual almanac sites block. |
| **Public holidays** | `date.nager.at/api/v3/PublicHolidays/{year}/{ISO2}` | Authoritative and instant, versus cross-checking blog calendars. |
| **Weather and climate** | `api.open-meteo.com/v1/forecast` · historical at `archive-api.open-meteo.com` (to 1940 — derive normals) | **Different hosts.** Use the national met service as the authority and this for machine-readable numbers. |
| **FX** | `api.frankfurter.dev/v1/{YYYY-MM-DD}?from=XXX&to=YYY` | ECB reference rates. **Returns the date with the rate**, which is exactly what the money rules require. The old `.app` host 301s. |

Also useful and keyless: **OSRM's demo server** for driving distances, and the **USGS feed** for seismic activity.

**Verified NOT usable:** `travel-advisory.info` serves a certificate for `*.kasserver.com` and fails to load. It is widely recommended and it does not work — proof that this list must be tested rather than copied from a listicle.

**The boundary, stated plainly, because it explains the whole blocklist above.** Keyless APIs cover the commodity layer. The commercially valuable categories — **flight fares, lodging rates, place listings and hours, transit timetables** — sit behind a key or a contract, which is exactly why those sites run bot protection. Reach for an API for the commodity layer; spend the scraping budget on what only scraping can reach.

**Keyed APIs are discovered per destination, not listed here** — see the API discovery step in `SKILL.md`. What's available varies by country, free tiers change, and hardcoding a national transit API into a skill meant for anywhere is how this list goes stale.

---

## Flights

**Meta-search:** Google Flights (calendar and price-graph views for the flexible-date question), Kayak, Skyscanner, Momondo, Kiwi.com (self-transfer routings other engines hide), ITA Matrix-style advanced routing tools.

**Always also the airline direct.** The fare rules, the true bag allowance, the seat map, and the change policy live on the carrier's own page, and the direct price plus direct-booking perks frequently beat the OTA once it is all counted. Low-cost carriers (Ryanair, Wizz, Southwest, Spirit, AirAsia, Scoot, and regional equivalents) are often **absent from meta-search entirely** — check them separately or miss the cheapest option on the route.

**Route existence:** FlightConnections-style tools answer "does anyone fly this non-stop" faster than a fare search. Airline alliance route maps for award routings.

**Product quality:** SeatGuru-style seat maps, aeroLOPA, airline product pages for lie-flat vs. recliner vs. angled, aircraft type from the schedule (a 787 and a 757 on the same transatlantic route are different trips).

**Airport ground access:** the airport's own official site for transit options and journey times, plus the city transit authority. This is where the second-airport comparison gets its numbers.

## Rail, road, bus, ferry

**Multi-modal:** Rome2Rio for "how do people actually get from A to B", Omio, Trainline.

**Rail direct** — always, for the real fare and the booking window: national operators (Japan Railways and the regional JR companies, Deutsche Bahn, SNCF/SNCF Connect, Trenitalia and Italo, Renfe, SBB, ÖBB, Amtrak, VIA Rail, KTX, China Railway, Indian Railways/IRCTC), plus the regional passes (Eurail/Interrail, JR Pass and the regional JR passes, Swiss Travel Pass) with a **break-even calculation against point-to-point tickets** — passes lose more often than they are marketed to.

**Seat 61** is the reference for how any given rail journey actually works: which train, which class, when booking opens, whether the pass is worth it.

**Bus:** FlixBus, Megabus, national coach operators, and in much of the world the intercity bus is the primary network rather than the budget fallback.

**Car rental:** Discover Cars, Rentalcars.com, AutoEurope as aggregators; the rental company direct for the real terms. Check specifically — one-way drop fees, cross-border restrictions, insurance requirements and what the user's credit card already covers, **International Driving Permit requirements** (mandatory in Japan, Italy, Greece, and others; the rental counter will refuse without it), minimum age surcharges, manual vs. automatic availability, fuel policy, toll transponders, low-emission-zone rules and city driving bans.

**Ferries:** operator direct, Direct Ferries as an aggregator; seasonal schedules change dramatically and the winter timetable is not the summer one.

**Driving reality:** Google Maps for distance and time, plus a check on tolls, fuel price, parking cost at the destination, and whether the destination is somewhere a car is a liability rather than an asset.

## Luggage forwarding and storage

Worth a real search on every trip with more than one base or a long layover — it changes which itineraries are physically pleasant.

- **Japan:** Yamato Transport (takkyubin) and Sagawa, bookable from hotel front desks and konbini; airport-to-hotel and hotel-to-hotel, typically next-day. Extremely reliable and cheap enough to be the default for anyone doing Tokyo–Kyoto with a suitcase.
- **Europe and elsewhere:** door-to-door luggage shipping services and courier-based options; check reliability reports before recommending, since this market is much thinner than Japan's.
- **Same-day storage:** station coin lockers, Bounce/Radical Storage-class networks, hotel bag holds before check-in and after checkout, airport left-luggage counters and their hours.

Report price, drop-off deadline, delivery window, size and weight limits, and reputation for reliability — a service that "usually" arrives next day is not one to route an itinerary around.

## Lodging

**Hotel aggregators:** Booking.com, Hotels.com, Agoda (strongest in Asia), Expedia, Hostelworld, plus regional players.

**Homeshare and whole-home rental — search these every time, not as an afterthought:** Airbnb, Vrbo, Booking.com's apartment inventory (large and frequently overlooked), Vacasa, Plum Guide, Sonder, and the local platform that actually dominates in that market — in much of Europe, Asia and Latin America it is not one of the American sites. For a party of three or more, a stay of several nights, or anywhere a kitchen matters, a whole home often wins on price and space — and often loses once fees land, which is exactly why both go in the same table.

Homeshare-specific checks that hotels don't need: **total cost including cleaning and service fees spread over the real number of nights**; **short-term-rental legality** in that city (New York, Barcelona, Amsterdam, Paris, Kyoto and a growing list ban, cap, or license them, and unlicensed listings get cancelled at short notice — look for a registration or licence number on the listing); host-set cancellation terms, which are frequently harsher than a hotel's; late-arrival and self-check-in arrangements; and scam signals — thin review history, off-platform payment requests, photos that appear elsewhere, prices far below market.

**Direct, always.** Compare the direct rate against the OTA rate and report the delta including: best-rate guarantees, member rates, included breakfast that the OTA rate excludes, cancellation terms that differ by channel, and whether the booking earns points and elite recognition at all. Resort fees, city and tourist taxes, and parking are frequently excluded from the headline number on every channel — get to the all-in nightly cost.

**Airport and area shuttles:** the property's own page, and the airport's page. Complimentary shuttles exist far more often than they are advertised, and one can swing a hotel decision by $60/day.

**Amenities — verify, don't read the checkbox.** OTA amenity lists are stale and generous. The property's own site is better; **recent reviews and Google Maps photos are best**, because that is where a closed pool, a broken lift, a "kitchenette" that is a kettle, or air conditioning that only runs on a building schedule actually surfaces. Check specifically for **seasonal pool closures and renovations on the travel dates** — an amenity list will happily advertise a pool that is drained for the winter. For older European and Japanese properties, confirm A/C and lift rather than assuming; neither is standard.

**Off-platform verification** — required before recommending anything:
- Google Maps reviews (rating *and* count, plus recent ones — a 2019 consensus is not current)
- Reddit and forum threads naming the specific property or block
- Local-language reviews where they exist
- Street View for the actual block, which reveals things no review mentions

## Neighborhood safety

- Government travel advisories (the user's own foreign ministry, plus one other country's for a second read — they often disagree, and the disagreement is informative)
- City or police open crime maps where published
- Numbeo-style crime indices as a rough baseline only, never as the sole source
- Area-specific threads on the local city subreddit and on travel forums — "is X a good area to stay" is one of the most-asked questions on earth and usually well answered
- Distinguish clearly between *actually dangerous*, *fine but unpleasant after dark*, *fine but dead at night with nowhere to eat*, and *fine but a 40-minute commute from everything*. These get conflated constantly and only one of them is a safety issue.

## Experiences, tours, festivals

**Marketplaces:** GetYourGuide, Viator, Klook (strongest in Asia), Airbnb Experiences, Tiqets.

**Operator direct** — often cheaper, and the marketplace listing frequently resells a tour the operator runs itself.

**Official sites** for parks, museums, and monuments: timed entry, lottery systems, permit windows (some open months ahead and sell out in minutes), free days, closure days, last-admission times that are not the closing time.

**Festivals and seasonal events** in or near the window: national and religious holidays, matsuri and regional festivals, carnivals, harvests, night markets, sporting fixtures, and natural timing — blossom and foliage forecasts, aurora season, migrations, monsoon breaks. Sources: national and city tourism boards, event calendars, the local subreddit, and specialist forecast sites for blossom/foliage.

For each festival also research the **etiquette**: what to wear, what to bring or offer, photography rules, tipping and gifting norms, whether visitors are welcome to participate or expected to observe, ticketing or invitation requirements, and behaviors that read as disrespectful locally. And flag the knock-on effect — festivals fill hotels and raise prices for a wide radius, sometimes months ahead.

**Independent reviews** for every operator, same standard as lodging: Google Maps, Reddit, forums, blogs. An operator with a 4.9 on the platform selling the ticket and a wall of complaints on Reddit is a finding.

## Food and drink

**Must-try, established:** Michelin Guide (including Bib Gourmand, which is the useful tier), World's 50 Best and its regional lists, national and city food awards, Eater city guides.

**What locals actually eat:** the local review platform, which is rarely the international one — Tabelog in Japan, Dianping in China, and the equivalent elsewhere. Local-language blogs and food media. City subreddits and food subreddits. Market and street-food guides. Neighborhood-specific searches rather than city-wide ones.

**Practicalities:** Google Maps for hours and current status (permanently-closed is common and stale lists do not know), the restaurant's own site or social for the real hours, reservation platforms and **how far ahead booking opens** — some open exactly 30 days out at a specific hour and fill in seconds. Note cash-only, no-English, no-reservation-queue-only, and closed-Mondays situations. HappyCow and equivalents for dietary constraints.

Aim for a mix: the dish the place is actually known for, the specific spot locals name for it, and at least one thing that will not appear on any English top-10 list.

## Community sentiment

**Reddit** — the highest-yield source for honest opinion. Sweep: `site:reddit.com [city] itinerary`, `[city] overrated`, `[city] worth it`, `[city] where to stay`, `[city] tourist trap`, the city or country subreddit, the local-resident subreddit (different from the travel one and more honest), r/travel, r/solotravel, r/awardtravel, r/onebag, r/flights.

**Forums:** TripAdvisor destination forums, FlyerTalk (unmatched for airline, airport, and award specifics), Rick Steves' forum (Europe), Fodor's, Lonely Planet Thorn Tree-class boards, and country-specific expat forums.

**Blogs and video:** established destination bloggers, YouTube itinerary and "what I'd skip" videos, tier lists and overrated/underrated threads.

Weight recency heavily and note it. Prices and "is it still good" both decay within a year or two. Where a heavily-marketed attraction and the local consensus disagree, report both and say which is which.

## Points and loyalty

**Award search:** the program's own site for award availability and pricing, plus award-search tools (point.me, seats.aero-class) where they cover the program. Alliance partner sites often price the same seat very differently.

**Program terms — read the fine print, this is where the value is decided:** award chart or dynamic pricing, carrier-imposed surcharges still payable in cash (these can exceed the value of the points), blackouts, minimum stays, partner-only restrictions, change/cancel/redeposit fees, points expiration and account-activity rules, family pooling, transfer minimums and increments, points-plus-cash caps.

**Transfer paths:** the transferable-currency program's own partner page for ratios and transfer times, plus current transfer-bonus announcements. Points-and-miles media (The Points Guy, Frequent Miler, One Mile at a Time and equivalents) for valuations and live bonuses — treat their point valuations as a baseline for comparison, not as fact.

**Elite benefits:** the program's own benefits page for what the user's current tier actually gets on this specific booking, and which booking channel preserves it.

## Weather and climate

**The national meteorological service is the authority for anything seasonal, and the brief should name it.** Foliage and blossom timing, monsoon onset, first snow, typhoon frequency — every one of these has an official forecaster, and commercial travel sites republishing their own guesses are directional only. Two tracks in one run returned opposite answers on autumn foliage timing because neither consulted the official source; naming it in the brief prevents that.

- Climate normals: weather service historical pages, WeatherSpark-class climate summaries, Wikipedia climate tables as a cross-check — and `archive-api.open-meteo.com` for the same data in machine-readable form
- Live forecast, only if the trip is inside forecast range, labeled as a forecast with the date pulled
- Seasonal specifics: monsoon and hurricane windows, wildfire and smoke season, snow closures on passes and trails, daylight hours (a December afternoon in Reykjavík is short), sea temperature, altitude effects
- timeanddate.com for daylight, holidays, and time zones

## Entry, money, connectivity

- **Entry:** the destination government's own immigration page as the authority, plus the user's foreign ministry page. Visa or e-visa or visa-free, passport validity rule (six months is common), blank-page requirements, onward-ticket requirements, transit visa rules — which matter enormously for the long-layover question — electronic travel authorizations (ETA/ESTA-class), and vaccination or entry-form requirements.
- **Money and payments:** current FX from a rate source with the date. Then the practical layer, which is what travellers actually need: **which card networks are accepted** — Visa and Mastercard are near-universal, Amex and Discover are refused far more often than holders expect — whether signature-only cards fail at unattended kiosks (rail machines, petrol pumps, tolls, parking), contactless and Apple/Google Pay acceptance, and **whether a local payment app is effectively mandatory**. For that last one the decisive question is not how dominant the app is but **whether a visitor can register at all**, since most require a local bank account, national ID, or phone number; where a foreign-card route exists (Alipay and WeChat now support international cards with limits), get its limits and fees. Sources: the destination's central bank or payments-authority pages, the app's own English-language help pages for foreign-visitor eligibility, recent expat and r/[country] threads for what actually works at the till, and card-network merchant-locator or acceptance pages. Plus ATM fees and which banks take foreign cards, tipping norms and whether tips can go on a card at all, and the VAT refund process.
- **Connectivity:** eSIM providers (Airalo, Holafly and equivalents) against local physical SIMs and the user's home carrier roaming pass; local transit apps and ride-hailing apps that actually work there (Grab, DiDi, Bolt, Uber's real coverage).

## Health, disease and immunizations

Get this from health authorities, not travel blogs. A wrong vaccination answer can end a trip at the check-in desk.

**Requirements and recommendations:** the destination's own health ministry, the traveller's national public-health body (CDC Travelers' Health, UK TravelHealthPro/NaTHNaC, or equivalent), and the WHO's international travel and health pages. Travel-clinic sites are useful for lead times but should be cross-checked against an authority.

**The transit trap:** yellow fever and similar requirements are frequently triggered by a **country you connect through**, not the destination. Check every country on every candidate routing, and check whether the airside-transit exemption applies at that specific airport — some airports route all connecting passengers through immigration, which voids the exemption entirely. This is the single most consequential thing in this section and the easiest to miss.

**Current outbreak data with numbers:** national epidemiological bulletins, WHO Disease Outbreak News, PAHO/ECDC regional surveillance, and current local press. Report cases, regions, dates, and trend — never a bare "risk is present."

**Region-specific:** malaria maps by region and altitude rather than by country, altitude-sickness guidance for anything above ~2,500m, and air-quality indices where relevant.

**Water and foodborne risk:** the local water utility's own quality reports and any current boil-water notices, the public-health authority's traveller guidance on water and food, and — for the street-food question specifically — informed local and expat consensus (city subreddit, expat forums, food writers who live there) rather than a generic warning aimed at every developing country at once. Ask whether street vendors are licensed and inspected, since in several countries they are, which changes the answer. Note that "safe for residents" and "safe for a visitor" differ, and that ice usually comes from a different supply than the tap. The output must be a usable verdict — safe, safe with named precautions, or risky — because the food research depends on it.

**Medications:** the destination's controlled-substances list and its embassy's guidance on carrying prescriptions. Japan, the UAE, Singapore and others restrict drugs that are routine elsewhere, and travellers are detained over it.

**Care on the ground:** nearest hospital to each base with its actual distance, clinic and pharmacy availability, emergency numbers, whether entry requires insurance, and what evacuation from a remote base would involve.

## Visas and entry, by passport

Entry rules are **passport-specific**, and travellers on one itinerary holding different passports are frequently treated differently. Never use a source that doesn't name the nationality it applies to.

- **The destination's own immigration ministry** is the authority. The traveller's foreign ministry country page is the cross-check.
- **Apply only on the official site.** Every e-visa and ETA-class system has a swarm of paid lookalike sites that charge a fee for something free or cheap, and they rank well in search. Identify the genuine government URL and warn about the copies explicitly.
- **Processing times: advertised versus actual.** Consular appointment backlogs and e-visa queues drift far from the published figure. Check recent traveller reports for the real number, and put an "apply by" date in the booking checklist — an authorization that says 72 hours and is running three weeks changes when flights should be bought.
- **Transit is separate.** Check per airport, not per country: some connections need a transit visa even airside, and some airports have no airside path at all.
- Also confirm: passport validity rule as the destination states it *and* as the airline enforces it (these differ), blank pages, onward-ticket enforcement, proof of funds and accommodation, arrival forms, departure taxes, and overstay penalties.

## Discounts, passes and loyalty beyond flights

- **City passes and tourist cards** — the city tourism board's own page for what is actually covered, then do the break-even against the real itinerary rather than trusting the marketing.
- **Rail and transit** — the operator's own railcard and advance-fare pages; multi-day passes against pay-as-you-go.
- **Car rental** — association and warehouse-club programs (AAA/CAA, Costco Travel, AARP), corporate discount codes, and whether any beats the public rate once mandatory local insurance is added.
- **Attractions** — the official site for free-admission days, combo tickets, advance-purchase discounts, and concession pricing. Check for a free day before recommending a paid ticket.
- **Dining** — airline dining programs, OpenTable-class points, restaurant weeks and prix-fixe promotions falling in the window, and lunch menus from the same kitchen at a fraction of dinner prices.
- **Card-linked offers and shopping portals** — Amex Offers, Chase Offers, airline and bank shopping portals. Account-specific: describe what typically appears, never assert the user has one.
- **Memberships already held** — AAA/CAA, Costco, AARP, alumni and union programs, employer travel schemes, and museum reciprocal memberships, which often get free entry abroad.
- **Coupons: operator-official sources only.** The operator's own promotions page or newsletter offer. Do not surface codes from scraper-aggregator sites — verify against the operator or mark `UNVERIFIED`, because a code that fails at checkout is worse than none.

## Political stability, conflict and disruption

- **Advisories** — the traveller's foreign ministry plus one other country's (US State Department, UK FCDO, Australian Smartraveller, Canada, and equivalents). Report the level *and* the reasoning, and say whether it applies to regions on the itinerary or somewhere the traveller will never go. A country-level warning driven by a distant border region should not be presented as if it covers the whole trip.
- **Conflict and organized crime** — regional detail, and whether airspace or routing is affected. Some conflicts reroute flights without the destination being unsafe.
- **Political calendar** — elections, referendums, and charged anniversaries falling in the window. These reliably produce demonstrations, road closures, transport shutdowns, alcohol bans, and occasionally curfews.
- **Strikes** — the most likely disruption in much of Europe and Latin America and the least researched. Air traffic control, airlines, rail, metro, buses, taxis, ports, museums and public-sector staff. Many countries require advance notice, so strikes are often knowable weeks out: check the national rail and transit operators' own service pages and current local press.
- **Natural hazards on the dates** — hurricane and typhoon season, wildfire, seismic and volcanic activity, flooding.
- **Practical** — embassy location and contact, traveller registration programs, and what insurance does and does not cover for unrest.

Date every claim. A year-old assessment of a fast-moving situation is not current, and "as of [date]" matters more here than anywhere else in this map.

## Law, customs and scams

**Law:** the destination government's own pages, plus the traveller's foreign ministry country page (US State Department, UK FCDO, Australian Smartraveller, Canadian travel advice — these are written precisely to keep citizens out of foreign jails and are among the highest-value sources in this whole map). Cross-read two countries' advice; they emphasise different things. Embassy and consulate pages for the destination often carry the clearest statements on drugs, drones, photography, and detention.

**Customs and etiquette:** local etiquette guides written by residents, Culture Crossing-class references, the destination's own tourism board on ceremony and temple conduct, and — best of all — the local subreddit's recurring "what do tourists do that annoys you" threads. For religious sites, the site's own visitor page.

**Scams:** the local city subreddit and r/travel scam threads, the foreign ministry's scam warnings, recent local press, and TripAdvisor forum threads. Weight recency heavily and state each source's date — scam patterns turn over fast, and a 2018 warning may describe something that no longer happens while missing what does.

**Tourist traps:** community sources only. Tourism boards will never tell you that the thing they market is disappointing.

## Maps, distances and travel times

Measure, don't estimate. Any routing service that returns a real distance and duration will do — the point is that the number comes from map data rather than intuition.

- **Driving and walking:** a mapping service for distance and duration, then add realism — parking, traffic at that hour and weekday, and the fact that mountain roads, unpaved roads, and dense old towns run well below the routing engine's assumptions.
- **Transit:** the local transit authority's own journey planner, which knows the timetable. Record **frequency and last departure**, not just journey time — a 12-minute ride with a 90-minute headway is a 90-minute journey, and the last bus is what strands people.
- **Multi-modal and intercity:** Rome2Rio-class tools for "how do people actually get from A to B", then verify against the operator.
- **Airport transfers:** the airport's own ground-transport page, which gives official times and fares by mode.
- **Terrain matters:** check elevation profile for anything walked. A 1.2km walk that climbs 90m is not a 15-minute walk.

Record for every pair: distance, mode, map time, realistic time, cost, frequency, last departure, and Sunday/holiday service.

## Fare rules, passenger rights and airports

**Ticket structure:** the booking flow itself usually reveals it — one confirmation and one PNR versus two. Meta-search results that combine carriers with no interline agreement are the tell for a self-transfer. For self-transfer products, the operator's own guarantee terms page, not its marketing page, and recent traveller reports on whether claims actually pay.

**Passenger rights:** the regulator, not a claims company. The European Commission's air passenger rights pages for EU261, the UK CAA for UK261, the Canadian Transportation Agency for APPR, and the US DOT's aviation consumer protection pages. Claims companies publish decent explainers but take a cut and overstate entitlement — use them to orient, cite the regulator. Then the airline's own conditions of carriage for schedule-change and involuntary-rebooking policy, which is where the rights that actually get used live.

**Baggage on multi-carrier tickets:** IATA interline baggage rules and the alliance's own baggage pages, then each carrier's page. The applicable allowance depends on ticketing carrier and route, and it is frequently not the cheaper carrier's.

**Airport mechanics:** the airport's own site for terminal layout, inter-terminal transfer times and whether the transfer is airside; the airport's or the border agency's published wait times where they exist. FlyerTalk is unmatched for whether a specific connection is realistic in practice, and for whether a given lounge is worth the walk.

**Lounges:** Priority Pass and equivalent directories for what a card opens, the airline's own lounge pages for what fare and status open, plus opening hours — a lounge that shuts at 9pm is useless on a 10pm departure.

## Language and communication

**What is spoken:** Ethnologue-class references and the destination's own census or statistics office for regional language distribution — national and regional languages diverge sharply in Spain, India, Switzerland, Belgium and many others, and the country-level answer hides it.

**English adoption:** the EF English Proficiency Index gives a country-level baseline only — do not stop there. The useful detail comes from **recent traveller and expat reports, context by context**: the local subreddit, r/travel, expat forums, and TripAdvisor threads asking specifically about getting by without the language. Weight recency; adoption shifts noticeably by generation and has moved fast in several countries.

**Signage and machines:** transit operator sites often show whether apps and machines have an English interface, and recent traveller photos and videos show what the signage actually looks like. YouTube walkthroughs of a specific station or airport are unusually good for this.

**Tools:** the translation app's own supported-language and offline-pack documentation — quality varies enormously by language pair, and the app that is best for Spanish is often not the best for Japanese or Thai. Check whether the destination blocks any service, which changes what to install before departure.

**Pitfalls and etiquette:** local-etiquette guides written by residents, the local subreddit's recurring "what do tourists get wrong" threads, and language-learning community discussions for register and false-friend traps. For emergency communication, the destination's emergency services page on whether English-speaking operators or interpreter lines exist.

## Search patterns that work

```
site:reddit.com [city] itinerary 2026
site:reddit.com [city] where to stay neighborhood
site:reddit.com [attraction] worth it OR overrated
site:reddit.com [city] scam OR "ripped off"
site:reddit.com [city] "what annoys you" tourists
[city] "locals" restaurant -tripadvisor
[origin] to [destination] nonstop airlines
[city] festival calendar [month] [year]
[hotel name] review -booking.com -hotels.com -expedia
[program] transfer partners ratio
[route] award availability
[country] yellow fever requirement transit
[country] dengue OR malaria cases [year] site:gov
[country] prescription medication banned controlled
[country] drone laws tourist
[country] best time to visit locals
site:reddit.com [country] "without speaking" OR "no [language]"
site:reddit.com [city] english widely spoken
[airline] conditions of carriage schedule change
[airport] terminal transfer time connection
[route] separate tickets missed connection
```

Search in the destination's language for food, transit, and events. Translate the results. The English internet's version of a city is a small and heavily commercialized subset of it.
