# Traveler profile template

Schema for `traveler-profile.md` in the skill root. Copy this structure when creating it on a first run; update in place afterward rather than appending new versions.

The file's absence is the first-run signal — do not create it as an empty placeholder.

Keep it terse. It is read at the start of every run, so it should be scannable, and it should hold only things that stay true between trips. Trip-specific answers belong in the trip's own notes, not here.

---

```markdown
# Traveler profile

Last updated: YYYY-MM-DD

## Identity and basics
- Preferred display currency: USD
- Languages spoken: (and rough level — gates whether the language agent runs at all)
- Home airports: (primary, plus drive-radius alternates with drive time)
- **Sleeping arrangements:** (how many separate beds, and who shares — *not* answered by headcount. A group of adults is not couples unless stated, and this decides the whole lodging budget.)

## Travellers

One record per person, **referenced by handle**. A later run opens with *"same four as last time — Sam, Alex, Jo and Rae?"* instead of re-interrogating.

| Handle | Age / range | Passport | Mobility | Health concerns | Dietary | Saved? |
|---|---|---|---|---|---|---|
| | | (one visa row per nationality — never generalised across a party) | (lifts, step-free, walking limit) | (asthma, cardiac, pregnancy — gates air quality, altitude, food) | | yes / declined |

**Ask per person, not as a blanket yes.** Anyone who declines is planned for normally this run and stored nowhere — do not keep a record marked "declined" containing their details, just the fact that they declined.

These fields are load-bearing rather than decorative: **age** gates rail passes, discounts and licence minimums; **mobility** gates lodging and day trips; **health** gates the air-quality finding, altitude, and the street-food verdict; **passport** drives one entry-table row per nationality.

## Activities and experiences

Gathered in **Phase 5**, after the destinations are settled — asked at intake it returns generic answers about places nobody has chosen yet.

- **Enjoys:** (categories — food and drink, motorsport, hiking, live music, museums, nightlife, golf, markets…)
- **Named must-sees:** (specific things asked for by name. **Each one gets its own subsection in the deliverable**, however small.)
- **Not interested in:** (as useful as the positives — saves whole tracks)

## Constraints
- Hard avoids:

## APIs configured
| Service | What it covers | Key stored? | Notes |
|---|---|---|---|
| | | yes / declined | (rate limit, tier caveats) |

Record declines too, so later runs re-confirm rather than re-ask. Keys live in `~/.claude/settings.json`, never here.

## Booking rules learned the hard way
Durable, cross-trip lessons — the mistakes worth never repeating. One line each, with the *why*, because a rule without its reason gets dropped the first time it's inconvenient.

## Loyalty programs
| Program | Type | Tier | Approx balance | Notes |
|---|---|---|---|---|
| | airline / hotel / rail / transferable card points | | | |

Cards held with travel perks: (free-night certs, hotel credits, primary rental insurance, lounge access)

## Wishlist
Ranked. The *why* matters as much as the place — "Iceland for the aurora" and "Iceland for the road trip" are opposite seasons.

1. Place — why
2. Place — why

## Subagent models
- Assignment: sonnet → A, C, G, H, I, J, K · haiku → B, D, E, F, L
- Lineup this was chosen against: (list the models available at the time)
- Chosen: YYYY-MM-DD

## Standing preferences
Accumulated over time — seat preference, departure times they refuse, minimum lodging standard, pace, hotel vs. rental, willingness to drive abroad, appetite for long layovers.

## Trips planned
- YYYY-MM — destination — travellers: (handles) — artifact URL
```

---

## Maintenance rules

**Read every run.** Before the gate round.

**Re-confirm, do not re-interrogate.** Show the stored travellers, loyalty programs, activities and wishlist back and ask only whether anything changed. Asking the full set again every trip is the fastest way to make the skill annoying enough to stop using. **Travellers especially** — offering four handles to confirm is one question; re-asking six fields about four people is twenty-four.

**Write travellers back only with consent, asked per person.** A record kept for someone who declined is a worse failure than not having the record.

**Ask fresh, not pre-filled, when:**
- It is a first run (no file).
- The available model lineup has changed since `Lineup this was chosen against` — a new model exists, or a stored one is gone. Ask the model question again with a note on which of the now-available models suits which track, then rewrite the assignment. Otherwise the skill quietly pins itself to a superseded generation.

**Write back** at the end of any run where something durable changed — a new loyalty program, a wishlist item added or crossed off, a preference learned ("no more 6am departures"), a model reassignment, or the trip appended to the trip log.

**Do not store** account numbers, passwords, passport numbers, card numbers, or exact point balances. Rough balances are enough to answer the burn-or-earn question, and this is a plain-text file on disk.
