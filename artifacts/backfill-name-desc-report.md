# Backfill company_name + description — 2026-10-02

**Repo:** michaeleverywhere/vc-comp  
**Scope:** `data/*_companies.json` (exclude `all_companies.json`)  
**Rule:** firm sites only; never invent; never Crunchbase/LinkedIn/PitchBook; prefer empty over guessed copy.

## Coverage (firm files)

| Field | Before | After | Δ filled |
|-------|-------:|------:|---------:|
| company_name | 100.00% (22126/22126) | 100.00% | 0 |
| description | 79.33% (17552/22126) | 79.33% | 0 |

Still missing descriptions: **4574**

## What we did
1. Inventoried empties across 128 firm datasets (22126 companies).
2. Re-scraped all 52 firms with gaps into `artifacts/rescrape_tmp/` (OUT-patched; data/ untouched until merge).
3. Merge-only empty `company_name`/`description` from fresh firm-site scrapes.
4. **Rejected 18** factory-scraper description candidates sourced from company homepages (not firm sites), including mis-matched Coinbase copy on Paradex/Routefire.
5. Firm-site rescrapes found **0** new descriptions for previously empty rows (source APIs/pages still omit them).
6. Rebuilt `all_companies.json` (22551 companies / 129 firms including Lightspeed).

## Still-missing descriptions — top firms
| Firm | Missing | N | % |
|------|--------:|--:|--:|
| gv | 646 | 646 | 100% |
| generalcatalyst | 523 | 584 | 90% |
| coatue | 372 | 372 | 100% |
| hustlefund | 335 | 335 | 100% |
| slowventures | 328 | 328 | 100% |
| norwest | 297 | 511 | 58% |
| boxgroup | 294 | 294 | 100% |
| svangel | 158 | 158 | 100% |
| ribbit | 155 | 155 | 100% |
| uncork | 154 | 175 | 88% |
| m12 | 141 | 141 | 100% |
| entreecapital | 123 | 156 | 79% |
| a16z | 122 | 860 | 14% |
| earlybird | 118 | 118 | 100% |
| reachcapital | 117 | 133 | 88% |
| resoluteventures | 112 | 112 | 100% |
| titaniumventures | 101 | 101 | 100% |
| signalfire | 100 | 100 | 100% |
| meritech | 50 | 50 | 100% |
| capitalg | 45 | 96 | 47% |
| whitestarcapital | 39 | 98 | 40% |
| blockchaincapital | 33 | 100 | 33% |
| dragoneer | 29 | 29 | 100% |
| greatoaksventurecapital | 26 | 100 | 26% |
| trueventures | 19 | 177 | 11% |

## Structural (0% description on firm site)
boxgroup, coatue, dragoneer, earlybird, gv, hustlefund, m12, meritech, resoluteventures, ribbit, signalfire, slowventures, svangel, titaniumventures

## Failed / stale scrapers (existing data retained)
- dragoneer: live site 404/403
- bessemer, greylock, iconiq, hustlefund: live parse returned 0 rows (selectors/CDN); did not overwrite
- wingvc: scrape() returned 0

## Artifacts
- `artifacts/backfill_name_desc_report.json`
- `artifacts/backfill_inventory_before.json`
- `artifacts/rescrape_parallel_results.json` / `rescrape_factory_results.json`
- `scripts/backfill_name_desc.py`
