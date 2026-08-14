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
- Passport nationality: (drives every visa answer)
- Languages spoken: (and rough level — gates whether the language agent runs at all)
- Home airports: (primary, plus drive-radius alternates with drive time)
- Party usually travelling: (solo / couple / family with ages)
- **Sleeping arrangements:** (how many separate beds, and who shares — *not* answered by headcount. A group of adults is not couples unless stated, and this decides the whole lodging budget.)

## Constraints
- Dietary:
- Mobility:
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
- YYYY-MM — destination — artifact URL
```

---

## Maintenance rules

**Read every run.** Before the gate round.

**Re-confirm, do not re-interrogate.** Show the stored loyalty programs and wishlist back and ask only whether anything changed. Asking the full set again every trip is the fastest way to make the skill annoying enough to stop using.

**Ask fresh, not pre-filled, when:**
- It is a first run (no file).
- The available model lineup has changed since `Lineup this was chosen against` — a new model exists, or a stored one is gone. Ask the model question again with a note on which of the now-available models suits which track, then rewrite the assignment. Otherwise the skill quietly pins itself to a superseded generation.

**Write back** at the end of any run where something durable changed — a new loyalty program, a wishlist item added or crossed off, a preference learned ("no more 6am departures"), a model reassignment, or the trip appended to the trip log.

**Do not store** account numbers, passwords, passport numbers, card numbers, or exact point balances. Rough balances are enough to answer the burn-or-earn question, and this is a plain-text file on disk.
