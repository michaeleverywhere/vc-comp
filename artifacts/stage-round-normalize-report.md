# Stage → funding-round normalize — 2026-09-30

**Repo:** michaeleverywhere/vc-comp

## Rule
Map `stage` / `type` / `investment_stage` / `first_invested*` / related firm-site fields to a clear funding-round label when the value already encodes one (Pre-Seed, Seed, Series A/B/C/…, Angel, Secondary, Series C+, and similar). Non-rounds (Early, Growth, Venture, partner names, Private, exit labels, years) → empty. Never invent. Prefer first-invested keys over `current_stage`; never replace a good round with a worse bucket.

## Counts (`all_companies.json`)
- Total companies: **18637** across **99** firms
- Stage with round: **3906**
- Stage blank: **14731**
- Fill rate (rounds only): **21.0%**

## Top rounds
- 1758 × `Seed`
- 1289 × `Series A`
- 413 × `Series B`
- 131 × `Pre-Seed`
- 114 × `Series C`
- 68 × `Series C+`
- 41 × `Series D`
- 36 × `Pre-Seed / Seed`
- 21 × `Series E`
- 11 × `Secondary`
- 8 × `Series F`
- 5 × `Angel`
- 4 × `Seed / Series A`
- 2 × `Series G`
- 1 × `Pre-Series A / Series A`
- 1 × `Series I`
- 1 × `Series H`
- 1 × `Angel / Seed`
- 1 × `Series B+`

## Per-firm field edits
- Files touched: 31
- Values rewritten to canonical rounds: 1714
- Non-round values cleared: 4213
- Already-good round labels left alone: 2765

## Code
- `scripts/normalize_stages.py` — in-place normalizer
- `automation/master_builder.py` — export `stage` via best clear round only
