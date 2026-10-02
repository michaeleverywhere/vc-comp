# Description web backfill — 2026-10-02

**Repo:** michaeleverywhere/vc-comp  
**Commit SHA:** `536deed4ed023590f9503ef1531f0c3f3b993064` (short `536deed`)  
**Pushed:** yes → origin/main  
**Scope:** empty `description` (and missing `company_name` if any) across `data/*_companies.json`  
**Sources ALLOWED:** official company websites (og/meta description), Wikidata (domain-verified or strict exact-label+org), other public non-paywalled pages  
**FORBIDDEN:** Crunchbase, LinkedIn, PitchBook; inventing copy; overwriting non-empty descriptions  
**Rejected:** parked domains, VC-firm self pages, clear Wikidata false friends (e.g. Clever→EV, Amper→Finnish bus, Bem→medal, Alchemy→video game)

## Coverage (firm files, excl. all_companies)

| Field | Before | After | Δ filled |
|-------|-------:|------:|---------:|
| description | 79.33% (17552/22126) | 90.24% (19967/22126) | 2415 |

Still missing descriptions: **2159**

## all_companies.json

| Metric | Value |
|--------|------:|
| companies | 22551 |
| firms | 129 |
| description coverage | 90.41% (20389/22551) |

## Method
1. Inventory empties (4574 / 79.33% cov).
2. Prefer official-site `og:description` / `meta name=description` when `company_url` present.
3. Else Wikidata English description with P856 domain verification when URL known; no-URL path requires exact label/alias match + org-typed P31 and rejects games/medals/places.
4. Never overwrite non-empty; introduce `description` key only when a verified blurb is found (coatue/hustlefund/svangel/ribbit schemas).
5. Audit: restore firm-site HEAD blurbs if touched; clear mis-attributions.
6. Rebuild `all_companies.json` via `master_builder.build()` write.

## Still-missing descriptions — top firms
| Firm | Missing | N | % |
|------|--------:|--:|--:|
| gv | 628 | 646 | 97% |
| slowventures | 318 | 328 | 97% |
| hustlefund | 194 | 335 | 58% |
| uncork | 150 | 175 | 86% |
| ribbit | 148 | 155 | 95% |
| reachcapital | 116 | 133 | 87% |
| earlybird | 112 | 118 | 95% |
| generalcatalyst | 80 | 584 | 14% |
| norwest | 65 | 511 | 13% |
| coatue | 62 | 372 | 17% |
| boxgroup | 27 | 294 | 9% |
| resoluteventures | 26 | 112 | 23% |
| titaniumventures | 23 | 101 | 23% |
| greatoaksventurecapital | 21 | 100 | 21% |
| a16z | 20 | 860 | 2% |
| blockchaincapital | 20 | 100 | 20% |
| entreecapital | 19 | 156 | 12% |
| dragoneer | 18 | 29 | 62% |
| m12 | 18 | 141 | 13% |
| parkway | 14 | 27 | 52% |
| trueventures | 10 | 177 | 6% |
| svangel | 9 | 158 | 6% |
| signalfire | 8 | 100 | 8% |
| whitestarcapital | 6 | 98 | 6% |
| meritech | 5 | 50 | 10% |
| canaan | 4 | 345 | 1% |
| foundrygroup | 4 | 55 | 7% |
| mosaicventures | 4 | 79 | 5% |
| index | 3 | 329 | 1% |
| bessemer | 2 | 528 | 0% |

## Artifacts
- `scripts/fill_descriptions_web.py`
- `artifacts/fill_descriptions_web_report.json`
- `artifacts/backfill_logs/fill_desc_web_priority.log`
- `artifacts/backfill_logs/fill_desc_web_all.log`
- `artifacts/wd_desc_audit.json`
