# Research rules

The standards every agent works to, and that you hold their findings to during synthesis. The per-track instructions are in [agent-briefs.md](agent-briefs.md); the sources are in [source-map.md](source-map.md). This file is the *why* and the bar — read it before spawning agents, and again when a finding looks too clean.

## Contents

- [Sourcing](#sourcing)
- [Money](#money)
- [Time](#time)
- [Health and safety](#health-and-safety)
- [Legal and cultural exposure](#legal-and-cultural-exposure)
- [Transport](#transport)
- [Communication](#communication)
- [Reporting findings](#reporting-findings)

---

## Sourcing

**Live only.** Every price, schedule, opening hour, fare rule, award chart, and closure comes from a search or fetch performed **this session**, carried with its source URL and the date accessed. Never fill a gap from training data. This is the single biggest failure mode of the whole skill: a confidently stated stale price is worse than no price, because the user acts on it.

**`UNVERIFIED` is a valid answer and a guess never is.** Anything you could not confirm live gets labeled `UNVERIFIED` with a note on what you tried. An honest hole is more useful than a plausible invention, and it tells the user exactly where to spend their own five minutes. Never invent flight numbers, gate times, addresses, phone numbers, opening hours, or prices. In the health, entry, and legal sections an invented fact is not just unhelpful, it is dangerous.

**Links you may emit.** The rule above is a prohibition; this is the procedure that enforces it, and it exists because an agent on this skill fabricated a table of sources and the entire track had to be discarded and re-run twice.

- **Never print a URL you did not fetch, or see returned in a live search result, this session.** A plausible-looking URL is a fabricated one.
- **Never construct a shortened link.** Real short links are opaque random strings; a readable one — `goo.gl/maps/SomePlaceName` — is invented by definition. Give the **verified full street address** instead, or write `address UNVERIFIED`.
- **Scan your own output before returning it.** Duplicate IDs or near-identical URLs across different entries are the signature of invention; that is precisely how the failure above was caught.
- Where a page is fetch-blocked, a **search-result snippet is citable — provided it is labelled as a snippet** rather than presented as a fetched page.

**A short honest table beats a long padded one.** Six solid rows plus a plain statement of what blocked you is a success. Twenty rows where fourteen are plausible-looking guesses is a failure that discredits the other six.

**Don't substitute a weaker source class for the one that defines the track.** If the sources that give a piece of research its purpose are unreachable — forums for community sentiment, the operator for fares, the ministry for law — say so and return less. A secondhand summary standing in for the primary source is worse than an empty section, because it looks complete. This has happened: a sentiment sweep that could not reach the forums used a blog's summary of them instead, which is not a degraded version of that research, it is a different and near-worthless one.

**When a source won't load, diagnose before retrying.** Four failures look alike and need opposite responses — bot protection that will never clear, rate limiting caused by your own sibling agents, a JS-rendered page that needs a browser rather than a fetcher, and a site that is simply broken. The taxonomy and the response for each are in [source-map.md](source-map.md) under *When a source won't load*. Conflating them wastes budget retrying the unretryable and writes off domains that were only partly blocked.

**Direct plus aggregator, always.** Check the operator's own site alongside every aggregator and report the delta: price differences, direct-booking perks, cancellation terms that differ by channel, and points or elite recognition that OTA bookings forfeit. Low-cost carriers and many local operators are absent from meta-search entirely — checking only the aggregator means missing them.

**Triangulate before recommending.** An aggregator listing plus community sentiment before anything is called must-see. When a top-10 list and the local subreddit disagree, that disagreement *is* the finding — surface it rather than quietly picking a side.

**Independent reviews, not just the listing.** For lodging and excursions, the selling platform's own reviews are the least trustworthy source available — they are filtered, and the platform has an interest. Cross-check Google Maps (rating *and* volume *and* recency), Reddit, forums, blogs, and local-language reviews. Report the **specific recurring complaint themes**, not a number: "thin walls and lift noise" is actionable, "8.4" is not.

**Recency is a fact about the source, and it gets stated.** A 2019 consensus about a neighbourhood, a restaurant, or a scam is not current. Date every community source you lean on. Prices and "is it still good" both decay within a year or two, and scam patterns turn over faster than that.

**Search in the local language** for food, transit, events, and anything municipal, then translate. The English-language internet's version of a place is a small and heavily commercialized subset of it.

**Authority hierarchy.** For anything with consequences — entry rules, vaccination requirements, law, transit legality — the destination government's own page is the authority and the traveller's foreign ministry is the cross-check. Never rest a consequential claim on a travel blog or a visa-service site, and never trust a summary that does not name the nationality it applies to.

**When sources conflict, say so.** Give the reason to trust one over the other: recency, whether it is the operator's own page, whether it is one review or forty, whether one is a tourism board with an interest. Do not average two numbers into a third that nobody reported.

## Money

**Both currencies, always, with a dated rate.** Every price appears in the local currency and the user's preferred currency — `¥18,000 (~$118)` — with the FX rate and its lookup date stated once at the top of the report. A rate quoted without a date is worthless a month later.

**All-in, not headline.** The advertised number is almost never the number. Get to the real total: airline bag and seat fees, resort fees and tourist taxes on lodging, homeshare cleaning and service fees spread over the actual number of nights, mandatory rental insurance, service charges and VAT on restaurant bills, carrier surcharges on award tickets. **Flag the false floors explicitly** — the fare that is cheapest until a bag is added, the hotel that is cheapest until the taxi is added, the award that is free until the surcharge is added.

**Read the validity window printed on the page.** Fare tables, passes, and tourist cards routinely carry a "valid through" date, and cached or superseded versions of those pages rank well in search. This is the commonest way a stale number enters a plan — a Hakone pass showed ¥6,100 on a page valid only through the previous September, against ¥7,100 live. If a price page states a validity period that has passed, the number is wrong no matter how official the source looks.

**Look for the discount before quoting the price.** Not just flights and hotels: city passes with the break-even actually calculated against this itinerary rather than assumed, railcards, association and warehouse-club rates, corporate rental codes, operator-direct versus marketplace pricing, museum free days, concession pricing, lunch menus from the same kitchen, dining programs, shopping portals, and memberships the user may already hold. Only surface offers verified on the operator's own page — a promo code that fails at checkout is worse than none.

**Price the thing they will actually book.** Three adults is not one adult × 3 for lodging, and per-person tour pricing often has group breaks. Search the real occupancy and party size.

## Time

**Check the actual dates and weekdays.** Public holidays, school holidays, monsoon, Ramadan, siesta hours, Monday museum closures, shoulder-season shutdowns, and local festivals all change what is possible and what it costs. A plan built on generic opening hours breaks on a Monday.

**Date flexibility changes what the research is for.** Locked dates still get priced ±1–2 days so the cost of being fixed is visible — sometimes it is zero, which is worth knowing. Flexible-by-days gets a window scan and a number for what the flexibility is worth. Flexible-by-weeks makes **best-time-to-visit part of the job**: weather by month, seasonal pricing, crowds, what is only available then, what shuts, and the months locals themselves name. A trip moved three weeks is often a materially better trip for less money, and that finding is worthless once the flights are booked.

**Distances and travel times are measured, not eyeballed.** Every recommendation carries how far it is and how long it takes **from where the user will actually be**, taken from map data. Real travel time is not the map's number: add parking, waiting for the service, the walk to and from the stop, traffic at that hour on that weekday, and the fact that mountain roads and dense old towns run well below what routing engines assume.

**Never chain map times.** Three legs of "20 minutes" is not an hour; it is closer to ninety minutes once you count getting out of the door each time. And flag any pair the plan treats as adjacent but isn't — two sights "both in the old town" can be forty minutes apart uphill. That is precisely the finding that saves a day.

**Frequency and last departure matter as much as journey time.** A 12-minute ride with a 90-minute headway is a 90-minute journey. The last bus is what strands people.

## Health and safety

**Health is researched, never assumed.** Required and recommended vaccinations with their lead times, current outbreak data **with case numbers, regions, and dates** rather than "risk is present", malaria and altitude by region rather than by country, prescriptions that are controlled locally, and the nearest real hospital to each base.

Two things make this load-bearing rather than boilerplate:

- **Requirements are frequently triggered by a country transited, not the destination.** Yellow fever is the classic case. Check every country on every candidate routing — and check whether the airside-transit exemption actually applies at that airport, because some airports route all connecting passengers through immigration, which voids it. This has decided flight choices before.
- **Anything with a lead time is a scheduling constraint.** A vaccine needing ten days goes at the *top* of the booking checklist, above the flights, not into the packing list.

**Water and street food get a verdict, not a hedge.** Is the tap drinkable *for a visitor* — a different question from whether residents drink it, and say which you are answering. What about ice, which usually comes from a different supply than the tap, and fountains, and brushing teeth.

Then the street-food question, answered as **broadly safe / safe with named precautions / genuinely risky**. "Be careful with street food" is not a finding and helps nobody. This matters because across much of Asia, Latin America and the Middle East the street food *is* the cuisine, and steering a traveller into restaurants out of vague caution costs them the best eating in the destination. Where it is safe, it becomes a proper tier in the food recommendations. Where precautions apply, they attach to **specific entries** — this stall turns over fast, this is cooked to order in front of you, skip the raw herbs and the ice — rather than floating as general anxiety. Where it is genuinely risky, say so with the reason and point to the same dishes in a safer setting.

Flag water-dependent items wherever the tap is not potable: ice, drinks mixed with tap water, salads and raw herbs, unpeeled fruit, fresh juices. These appear at every price level, and a smart restaurant is not automatically safer than a stall.

**State the water and street-food verdict twice** — in the health section and again at the top of the food matrix. That duplication is deliberate. The food section is where someone is actually deciding what to put in their mouth, and a warning three sections away is a warning that did not land.

## Legal and cultural exposure

**Entry rules are passport-specific.** Answer per nationality, and separately for each when the party holds different passports, since they are frequently treated differently on one itinerary. Cover the destination and every country transited. Where an application is needed: the **official** URL — every e-visa and ETA system is shadowed by paid lookalike sites that rank well and charge for something free — the cost, the documents, and **advertised versus actual processing time**, since consular and e-visa backlogs drift badly from the published figure. Anything requiring an application gets an "apply by" date in the checklist. A visa running three weeks against an advertised 72 hours is a flight-booking constraint, not paperwork.

Also confirm the passport validity rule **as the destination states it and as the airline enforces it** — these differ, and the mismatch strands people at check-in — plus blank pages, onward-ticket enforcement, proof of funds and accommodation, arrival forms, departure taxes, and overstay penalties.

**Scams and traps, named specifically.** Not generic caution. Which scams are actually run here, how each opens, and what the tell is. Plus the legal-but-bad-value traps: what is heavily marketed and consistently disappointing, and what locals say to do instead. Tourism boards will never tell you this; community sources will.

**Customs, for how not to be rude.** Greetings, tipping norms **including where tipping insults**, dining etiquette, shoes, queueing, gift-giving, whether haggling is expected or offensive and roughly what discount is normal where it is, religious observance visitors are expected to accommodate, and conduct at anything ceremonial on the itinerary.

**Laws, for how not to be arrested.** The section most often missing and the one with the worst downside. Drugs — including substances legal where the traveller lives, which catches people constantly — restricted prescriptions, alcohol rules, drones, photography around government and military sites and around people, vaping bans, currency import and export limits, customs restrictions in both directions, dress codes with legal force, LGBTQ+ legal status, protest rules, whether to carry the passport itself, and what actually happens when stopped by police.

**Stability, reported factually.** Current advisories with the **actual reasoning** behind the level and whether it applies to the itinerary or to a region the traveller will never see — a country-level warning driven by a border region 900km away is not a warning about the beach town. Plus conflict and organized crime by region, unrest, elections and charged anniversaries falling in the window, announced **strikes** (the likeliest disruption in much of Europe and Latin America, and usually knowable weeks ahead because many countries require advance notice), and seasonal natural hazards.

The failure runs both ways here, and both directions are real: a plan that ignores a live conflict is negligent, and one that treats every protest and every country-level advisory as a crisis is useless and unfair to the place. The test is whether a well-informed resident would recognize the description.

## Transport

**Prefer non-stop, but always show the trade.** Non-stop is the default recommendation, and it still gets presented next to the one-stop options with cost, **total door-to-door time**, and layover laid out. A long layover in an interesting city is a mini-destination — research it under all these same rules rather than writing it off as dead time. And check whether leaving that airport is even legal for this passport before recommending it.

**Price every fare class, not just the cheapest.** Basic economy through business, each with what the fare actually includes. Basic economy is routinely a false floor once bags and seats are added back, and business is occasionally a much smaller premium than expected on a specific route. Neither is visible unless they sit side by side.

**Compare modes, not just carriers.** Air against rail against driving against bus against ferry for the same leg. Rail wins more often than people expect once airport transfers and security are counted — and driving unlocks stops that no flight does.

**Door-to-door is the only honest number.** Flight time is not travel time. Include the airport transfer at both ends, the check-in buffer, and the ride into town.

**A price without its ticket structure is not a comparison.** Establish whether each itinerary is one ticket or **separate tickets** before ranking it. On one ticket a missed connection is the airline's problem — they rebook, and on a long delay they owe care. On separate tickets it is entirely the traveller's: no rebooking, fare gone, bags not through-tagged, buy a new ticket at the walk-up price. Meta-search sells self-transfer routings that look like ordinary connections and are not, so a cheaper row is sometimes buying real exposure. Say which, every time.

**Compensation regime is part of the fare.** EU261, UK261, APPR and DOT rules attach by carrier and departure point, not by the traveller's nationality, and a long delay under EU261 can be worth several hundred euros per person. An itinerary that sits outside every regime is worse than one inside it at the same price — flag it, because no fare comparison will ever show it.

## Communication

**English adoption is answered by context, never as one number.** "English is widely spoken" is simultaneously true of hotel receptions and false of pharmacies almost everywhere, which makes the country-level claim useless. Rate front desk, restaurants, taxis, rail staff, pharmacies, police, shops, and rural areas separately, from what recent travellers report. The gaps that matter most are the ones with consequences: not reading a menu is an inconvenience, not being understood in a pharmacy or by emergency services is not.

**Signage and machines determine independence.** Whether transit signage is romanized or bilingual, whether ticket machines have an English mode, and whether menus are translated decide how freely someone can move around without help. Check them rather than inferring them from the English-adoption answer — plenty of countries have excellent signage and little spoken English, and the reverse.

**Report the communication pitfalls, not just the phrasebook.** Where speaking English changes the price quoted. Formal versus informal register, where a phrasebook hands over the wrong one. False friends and gestures that read as offensive. Whether refusal is stated plainly or implied. How to get help in an emergency with no shared language. These are the things that cause actual problems, and no mainstream guide covers them.

## Reporting findings

**Every row traces to a source.** URL plus the date accessed. Where a cell could not be verified, write `UNVERIFIED` rather than a plausible number.

**Source links and action links are different things, and a row needs both.** The *source* is where you learned it — the review thread, the climate table, the forum post. The *action link* is where the reader goes to do something about it: book the room, reserve the table, buy the ticket, read the rule. A row with only a source makes the reader search for a thing you already found, which is the single most common way a research document wastes the reader's time.

**Every recommended item carries its own link, inline, next to the item.** Flights to the carrier's own booking page, lodging to the property's direct site (and the OTA alongside it where the comparison matters), restaurants to the venue's own page or reservation platform, tours to the operator direct rather than only the marketplace, rentals to the supplier, rail and bus to the operator's booking page, attractions to the official ticketing page. A Sources list at the end does not substitute for this — nobody scrolls to the bibliography to find the booking link for row four.

Prefer the **operator's own URL** over an aggregator's, since that is the one that survives and the one that carries the direct-booking terms. Where an official page cannot be found, say so in the cell rather than linking something that merely looks official — a link to a lookalike visa site or a scraper is actively harmful.

**Complex topics get a further-reading link beside the summary.** Where the report compresses something genuinely intricate into a paragraph — visa application mechanics, EU261 compensation, award transfer rules, vaccination requirements, driving and insurance rules, tax refund processes — the summary is not the whole truth and the reader may need the whole truth. Put the authoritative link right there, at the point of the summary, and label what it is: *the regulation itself*, *the airline's conditions of carriage*, *the ministry's own page*. Not a blog explaining it — the thing itself.

**Every matrix ends with a recommendation and why.** A matrix without a pick is homework, not advice. Say when something is genuinely close and what would tip it.

**Mark the traps as well as the picks.** The row that looks cheapest and isn't deserves to be visibly flagged, or someone will choose it.

**Surface contradictions rather than resolving them silently.** If two agents came back with different numbers, say so and give the reason to trust one.

**One fact, one owner.** Where two tracks will both plausibly touch the same fact, the briefs name which one owns it and which defers. Without that, both research it shallowly and neither resolves it — two tracks in one run returned opposite answers on when autumn foliage peaks, neither consulted the national meteorological service, and the contradiction survived into synthesis. For anything seasonal, forecast-based, or otherwise owned by an official body, **name the authoritative source in the brief** rather than leaving each agent to find its own and land somewhere different.

**Write like an agent who will hear about it if the recommendation is wrong.** Give the pick, then the reasoning. Say when a popular thing is not worth it and what the sources say instead. Never smooth over a gap.
