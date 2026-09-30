# Tag Sweep Report — michaeleverywhere/vc-comp Private Comps

**Date:** 2026-09-30 (America/New_York)  
**Repo:** michaeleverywhere/vc-comp (working clone `/workspace/vc-comp-me`)  
**Commit SHA:** _(filled after push)_

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Companies (firm files) | 18212 | 18212 |
| Untagged | 1186 (6.5%) | 611 (3.4%) |
| Tagged this run | — | **575** |

- Pass A (keyword `fill_empty` on name/description/sectors): **12**
- Pass B (homepage fetch → keyword classify): **563** firm-file fills (562 also hit `all_companies.json` during the script run; rebuilt afterward)
- LLM (Haiku) stage: **SKIPPED** — `ANTHROPIC_API_KEY` missing
- Status normalizations to `active` / `live` / `acquired`: **8828** (+12 misspelled `Aquired…` → `acquired`)
- Invented financials: **none**. Crunchbase/LinkedIn/PitchBook: **not used**.

## Per-firm tag fills (sorted by tags filled)

| Firm | Filled | Untagged after | Total cos |
|------|--------|----------------|-----------|
| comcastventures | 104 | 28 | 212 |
| floodgate | 40 | 9 | 116 |
| seedcamp | 35 | 12 | 327 |
| canaan | 35 | 46 | 345 |
| trueventures | 34 | 12 | 177 |
| capitalg | 28 | 13 | 96 |
| redpoint | 26 | 7 | 234 |
| balderton | 23 | 6 | 205 |
| pear | 21 | 7 | 211 |
| mubadalacapital | 21 | 4 | 85 |
| madronaventuregroup | 17 | 19 | 213 |
| greatoaksventurecapital | 14 | 12 | 100 |
| iriscapital | 12 | 5 | 52 |
| initialized | 12 | 2 | 184 |
| fikaventures | 12 | 3 | 94 |
| crosslinkcapital | 12 | 6 | 147 |
| blockchaincapital | 12 | 13 | 100 |
| eniacventures | 11 | 2 | 100 |
| tmtinvestments | 10 | 12 | 56 |
| episode1ventures | 10 | 3 | 84 |
| prosusventures | 8 | 3 | 125 |
| propelventurepartners | 7 | 6 | 44 |
| notation | 7 | 7 | 78 |
| upwest | 6 | 3 | 48 |
| scalevp | 6 | 0 | 117 |
| craft | 6 | 0 | 40 |
| gradientventures | 5 | 3 | 135 |
| khosla | 4 | 1 | 116 |
| cambridgeinnovationcapital | 4 | 0 | 24 |
| questventurepartners | 3 | 1 | 29 |
| felicis | 3 | 13 | 279 |
| meritech | 2 | 0 | 50 |
| kleinerperkins | 2 | 7 | 392 |
| index | 2 | 2 | 329 |
| hummingbirdvc | 2 | 0 | 69 |
| generalcatalyst | 2 | 8 | 584 |
| battery | 2 | 0 | 356 |
| baincapital | 2 | 0 | 280 |
| accel | 2 | 6 | 778 |
| a16z | 2 | 1 | 860 |
| uncork | 1 | 146 | 175 |
| svangel | 1 | 2 | 158 |
| norwest | 1 | 5 | 511 |
| matrixpartners | 1 | 0 | 45 |
| insight | 1 | 2 | 857 |
| firstround | 1 | 1 | 195 |
| emergence | 1 | 0 | 86 |
| coatue | 1 | 20 | 372 |
| bessemer | 1 | 2 | 528 |

## Still-untagged leftovers

**Count:** 611

**Top firms:**
- uncork: 146/175
- canaan: 46/345
- highalpha: 41/93
- comcastventures: 28/212
- ribbit: 26/155
- homebrew: 22/162
- coatue: 20/372
- madronaventuregroup: 19/213
- nea: 16/917
- felicis: 13/279
- blockchaincapital: 13/100
- capitalg: 13/96
- seedcamp: 12/327
- trueventures: 12/177
- greatoaksventurecapital: 12/100
- tmtinvestments: 12/56
- floodgate: 9/116
- generalcatalyst: 8/584
- kleinerperkins: 7/392
- redpoint: 7/234
- pear: 7/211
- notation: 7/78
- accel: 6/778
- balderton: 6/205
- crosslinkcapital: 6/147

**Why still empty (approx):**
- No description AND no company_url: 196
- No description (has URL; homepage fetch failed / parked / JS shell / no keyword match): 65
- Has description, no URL, keywords missed: 136
- Has description + URL but no confident taxonomy match (and LLM skipped): 214

Largest leftover pockets (uncork 146, highalpha 41, canaan 46, ribbit 26, homebrew 22) are mostly name-only / JS-heavy portfolio cards where homepage fetch yielded little usable text and Haiku was unavailable.

## Lead status (`status` field)

Repo convention uses existing key `status` (not `lead_status`). Normalized clear synonyms only:

- → `active`: Active, Current, Current Investment
- → `live`: Live
- → `acquired`: Acquired, Exited, Exit, M&A, Merged, Public/Acquired, Acquired by X, Aquired… typos

Left alone (ambiguous / not in the three allowed values): Public, Private, IPO, Prior, Past, Alumni, Unicorn, RIP, inactive, ticker symbols, etc. Empty status left empty (no guessing).

## Screenshots

Saved under `artifacts/tag-sweep-screenshots/` (15 firm portfolio pages):

- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/balderton.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/blockchaincapital.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/canaan.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/capitalg.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/comcastventures.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/floodgate.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/greatoaksventurecapital.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/highalpha.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/madronaventuregroup.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/pear.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/redpoint.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/ribbit.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/seedcamp.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/trueventures.png`
- `/workspace/vc-comp-me/artifacts/tag-sweep-screenshots/uncork.png`

## Airtable

Base `appdSRg0657zG3oef` table **Private Comps** (`tblTZuZ9jFfdFWRL8`).
Will update per-firm tag Number columns + Record count + Last commit after push.
No dedicated Untagged column exists in schema — untagged counts noted here only.
Notes raw URLs: leave / set to michaeleverywhere (never ruszinn).

## Blockers

1. **No ANTHROPIC_API_KEY** — LLM stage skipped; ~611 leftovers that need model knowledge or better homepage signal remain.
2. Pass B's `collect()` also walks `all_companies.json` (doubled fetch work); firm fills are correct and `all_companies.json` was rebuilt via `master_builder.py`.
