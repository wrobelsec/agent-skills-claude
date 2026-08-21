# API compatibility, by destination

**A key that authenticates is not a key that works *here*.** This file records where a configured provider has been observed to fail for a specific destination, so the next run doesn't rediscover it — and so a provider that fixes support can be promoted back.

Run **`run_tests.py` once per destination at the start of every run**, before any research is dispatched. It takes a real address in the destination's own script and checks the answer against a bounding box. It exits non-zero when a provider returns coordinates outside the expected area.

```bash
python references/scripts/run_tests.py --country Japan \
  --address "大阪市浪速区恵美須東1-6-8" \
  --romanized "1-6-8 Ebisuhigashi, Naniwa-ku, Osaka, Japan" \
  --bbox 24 122 46 154
```

## Why this test exists rather than a general "check your keys" note

The failure it catches is not an error. **Geoapify authenticates correctly, returns HTTP 200, and gives coordinates in the wrong country** — a Japanese-script Osaka address resolved to Germany, a Ginza address to Utah, and a Hiroshima address to Moscow. Nothing in the response signals a problem. A Latin-script control across three continents resolved within 0.006°, so neither the key nor the service is broken in general.

That is the worst shape a failure can take: **a confident wrong answer survives review in a way a blank never does.** It is only detectable by checking the answer against something already known to be true — which is what this test does, and why it has to run per destination rather than once per machine.

**The keyless Nominatim returns an honest empty for the same queries, and that is the better behaviour.** Prefer a provider that admits it doesn't know.

---

## Known failures

**Re-test before trusting any row here.** These are observations on a date, not permanent properties — providers do fix coverage, and a stale exclusion costs capability just as a stale inclusion costs accuracy. **Re-run the test suite for any destination whose row is more than a few months old**, and promote a provider back the moment it passes.

| Destination | Provider | Failure | Observed | Re-test status |
|---|---|---|---|---|
| **Japan** | **Geoapify geocoding** | **Local-script addresses resolve to the wrong country — three different wrong countries so far.** `大阪市浪速区恵美須東1-6-8` → Germany. `東京都中央区銀座4-3-7` → Utah. `広島市中区大手町1-5-8` → **Moscow, Russia** (55.7615, 37.5506). With `filter=countrycode:jp` it lands in Japan but ~600 km off, in Hokkaido. **Romanized addresses mostly work** — the same Hiroshima address romanized resolved to within ~90 m — but are not reliable either, since a romanized Osaka address once resolved to Tokyo | 2026-08-14, re-confirmed 2026-08-15 | **Open, and now confirmed across three independent probes in three cities.** Not an edge case in one dataset — treat Geoapify geocoding as unusable for Japanese script |
| **Japan** | Nominatim geocoding | Returns empty for granular Japanese addresses. **Not a defect for our purposes** — an honest empty is safe, and it is recorded here only so nobody mistakes it for a broken key | 2026-08-14 | Expected behaviour; no action |
| **Any** | **Sherpa Requirements API** | Key rejected as `INVALID_ARGUMENT: API key not valid` on **both** the v2 `GET /entry-requirements` and the current **v3 `POST /trips`**, with the correct `x-api-key` header. A Bearer header produces a *different* error (`UNAUTHENTICATED`, no key seen), which confirms the header shape is right and the key itself is being read and refused. **Integration is correct; the credential is not provisioned** | 2026-08-14 | **Open.** Two keys tried. Re-request access before spending more time on it |

## What works, and is worth recording too

| Destination | Provider | Note | Observed |
|---|---|---|---|
| **Japan** | **Google Places (New)** | Reliable on both local-script and romanized addresses; both probes landed within ~150 m of truth. `business_status` correctly reports `CLOSED_PERMANENTLY` on a venue that closed in 2023 | 2026-08-14 |
| Any | Google Places → Geoapify **routing** | Geoapify's *routing* between coordinates is sound; only its *geocoding* is affected. **Resolve coordinates with Places, then route with Geoapify** — that combination produced the measured distance matrix | 2026-08-14 |
| Any | **SerpApi `google_hotels`** | **Works, and is the only route found to dated lodging rates.** Takes `check_in_date`, `check_out_date`, `adults`, `children`, `currency`; returns per-night and stay-total figures plus rating and amenities. Verified across two unrelated markets and currencies. **Free plan is 250 searches per MONTH across all engines** — `lib/serpapi.py` caches every response and `lib/quota.py` refuses a batch that would exhaust it. Returns **no** rate for sold-out properties, which is a finding, not a gap. **Does not return bed configuration at any occupancy** | 2026-08-20 |
| Any | Open-Meteo **archive** · Nager.Date | Keyless and reliable. The archive endpoint rate-limits (HTTP 429) under rapid sequential calls — back off exponentially rather than reducing the query | 2026-08-15 |
| Any | **Frankfurter** (FX) | Works, but returned an intermittent **403** during a burst of calls. Keep a fallback chain — `api.frankfurter.app`, `open.er-api.com` — rather than treating one FX provider as authoritative | 2026-08-15 |

### Newly broken since the last run

| Provider | Failure | Observed | Replacement |
|---|---|---|---|
| **sunrise-sunset.org** | Now returns **HTTP 403** to a plain fetcher for any query. Previously the recommended keyless daylight source | 2026-08-15 | **Open-Meteo's `daily=sunrise,sunset`.** One caveat: the *forecast* endpoint returns **HTTP 400** for dates beyond its ~16-day horizon, so for a trip months out use the **archive** endpoint against the same calendar dates a year earlier — solar times for a fixed date move under a minute year to year. Label the result **derived**, not observed |

---

## Adding a destination

Pick a probe address that is **real, granular, and in the destination's own script** — a street address, not a landmark, since landmarks resolve by name and hide exactly the failure this catches. Give a bounding box generous enough for the whole country. Then record the outcome above with the date, whether it passed or failed.

**A passing row is as useful as a failing one**: it is what lets a later run use a provider confidently instead of re-testing from scratch.
