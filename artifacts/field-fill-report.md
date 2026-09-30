# Private Comps company field fill — 2026-09-30

**Repo:** michaeleverywhere/vc-comp  
**Scope:** fill empty company fields in firm `*_companies.json` + rebuild `all_companies.json`  
**Sources used:** existing scrape fields (harvest), firm portfolio re-scrape (Accel Sanity API), Wikidata via `scripts/enrich.py` helpers (`enrich_location.py`, `enrich_sectors.py`)  
**Not used:** Crunchbase, LinkedIn, PitchBook; no fabricated LAST FINANCING / TOTAL RAISED / ARR / VALUATION / TEAM SIZE / TRACKED BY

## Actions

| Pass | What | Fills |
|------|------|------:|
| Harvest (`scripts/fill_empty_fields.py`) | tagline→description; status synonym→active\|live\|acquired when clear; derive empty status from acquirer / “Acquired by” / is_active | 30 + 10 + 7 |
| Accel re-scrape | Refresh portfolio via Sanity API; tags restored via `tags.carry_forward` | 0 net HQ (site still empty) |
| Wikidata location | P159 → empty `location`/`headquarters` (domain-verified match only) | **85** |
| Wikidata sectors/meta | P452/P112/P571/P414 → empty sectors/founders/year/ticker | **187** |
| `master_builder` | Export `primary_investor`, `location`, `stage`, `first_invested`, `status` into `all_companies.json`; derive status from exit/active flags when firm schema has no `status` key | schema expand |

## Firm-file fill rates (conceptual columns)

| Field | Before | After | Δ filled | Still empty / why |
|-------|-------:|------:|---------:|-------------------|
| COMPANY / name | 100.0% (18637) | 100.0% | 0 | — |
| DESCRIPTION | 86.9% (16200) | 86.9% | 0\* | 1049 firms omit description key; ~1388 empty on firm site (e.g. GC Algolia has null descriptions) |
| WEBSITE / company_url | 90.2% (16810) | 90.2% | 0 | Firm CMS has null `external_url` (NEA/Insight/Lux/Venrock many); profile pages often lack outbound website |
| PRIMARY INVESTOR | 100% (firm from file) | 100% | 0 | Always the owning firm |
| SECTOR / everywhere_tags | 99.9% (18626) | 99.9% | 0 | 11 junk/non-startup leftovers from prior tag sweep |
| LOCATION | 18.1% (3369) | **18.5% (3454)** | **+85** | 14427 records have no location key in site-tailored schema; remaining empties unpublished on firm site + no Wikidata domain match |
| STAGE | 37.0%† | 37.2%† | +0 real | Most firms never publish stage on portfolio pages |
| FIRST INVESTED | 39.3% (7328) | 39.3% | 0 | Not on firm pages for majority of datasets |
| STATUS (firm key) | 59.6% (11106) | 59.6% (11113) | **+7** derived | 6038 records have no `status` key; Public/Private/Prior/Alumni/RIP left as-is (not clearly active\|live\|acquired) |

\*30 tagline→description fills applied; before metric already counted `tagline` as description.  
†Before snapshot omitted Lightspeed `current_stage`; after includes it (+37 measurement, not new scrape data).

## `all_companies.json` fill rates (after rebuild)

| Field | Fill % | Filled | Empty |
|-------|-------:|-------:|------:|
| name | 100.0 | 18637 | 0 |
| description | 86.9 | 16200 | 2437 |
| url | 90.2 | 16810 | 1827 |
| primary_investor | 100.0 | 18637 | 0 |
| everywhere_tags | 99.9 | 18626 | 11 |
| location | 18.5 | 3454 | 15183 |
| stage | 37.2 | 6935 | 11702 |
| first_invested | 39.3 | 7328 | 11309 |
| status | **67.4** | **12555** | 6082 |
| exited | 100.0 | 18637 | 0 |

Status rises vs firm files because the builder maps `is_acquired` / `is_active` / `is_current_investment` / exit words → `acquired`\|`active` when the firm schema has no `status` column (e.g. General Catalyst).

## What stayed empty (and why)

- **Financials** (LAST FINANCING, TOTAL RAISED, ARR, VALUATION, TEAM SIZE, TRACKED BY): never present on firm portfolio JSON for these datasets; left untouched by design.
- **Website gaps (~1827):** firm CMS nulls; re-checked NEA GraphQL/profile HTML — no company URL published for those rows.
- **Location gaps (~15k):** vast majority of firm schemas intentionally omit location (site never publishes it). Wikidata only fills when official-website domain matches (85 hits).
- **Stage / first invested:** only ~¼–⅖ of firms expose these on their own portfolio pages; cannot invent.
- **Status values like Public / Private / Prior Investment / RIP / Unicorn:** left unchanged — not unambiguously `active`\|`live`\|`acquired`.
- **Descriptions (GC ~520, Norwest ~288, …):** source APIs return null; inventing copy is forbidden.

## Code / artifacts

- `automation/master_builder.py` — richer all_companies columns
- `scripts/enrich.py` — location + founded_year support, expanded FILES
- `scripts/fill_empty_fields.py`, `scripts/enrich_location.py`, `scripts/enrich_sectors.py`
- `artifacts/fill_rates_before.json`, `fill_rates_after.json`, `field_fill_report.json`, `enrich_location.log`, `enrich_sectors.log`
