# Private Comps backfill (resume) — 2026-10-02

**Repo:** michaeleverywhere/vc-comp  
**Commit SHA:** `536deed4ed023590f9503ef1531f0c3f3b993064` (short `536deed`; tip `5aa96ea`)  
**Pushed:** yes → origin/main (`michaeleverywhere/vc-comp`)  
**Scope:** blank `description` + empty `everywhere_tags` across firm `data/*_companies.json`  
**Sources ALLOWED:** company sites, Wikidata, Clearbit domain suggest, DuckDuckGo IA, public pages  
**FORBIDDEN:** Crunchbase, LinkedIn, PitchBook; inventing; overwriting non-empty; Anthropic/Haiku for tags  

## Before → After (firm files, excl. all_companies)

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| description coverage | 90.24% (19967/22126) | 92.98% (20573/22126) | +606 filled |
| blank descriptions | 2159 | 1553 | |
| untagged (empty everywhere_tags) | 1985 | 878 | +1107 tagged |

## all_companies.json

| Metric | Value |
|--------|------:|
| companies | 22551 |
| description coverage | 93.1% |
| blank descriptions | 1556 |
| untagged | 879 |

## Method
1. Resume web description fill (`scripts/fill_descriptions_web.py`) — official meta, Wikidata, Clearbit+site, DDG IA. Name-only firms (gv, slowventures, ribbit, earlybird, …) careful search; leave empty if uncertain.
2. Reject parked/VC-self/false-friend blurbs; never overwrite non-empty.
3. Tags: `tags.fill_empty` keyword classifier + assertive judgment (fixed 17-tag set, max 4). No Anthropic/Haiku.
4. Rebuild `all_companies.json` via `master_builder`.

## Still missing (top)
**Descriptions:** {'gv': 363, 'slowventures': 215, 'hustlefund': 178, 'uncork': 95, 'ribbit': 84, 'earlybird': 83, 'generalcatalyst': 80, 'norwest': 65, 'reachcapital': 63, 'coatue': 60, 'boxgroup': 29, 'resoluteventures': 25, 'titaniumventures': 23, 'greatoaksventurecapital': 21, 'a16z': 20, 'blockchaincapital': 20, 'entreecapital': 19, 'm12': 18, 'trueventures': 10, 'parkway': 9}
**Untagged:** {'gv': 335, 'slowventures': 230, 'earlybird': 53, 'canaan': 35, 'entreecapital': 33, 'notioncapital': 28, 'northzone': 22, 'm12': 16, 'whitestarcapital': 14, 'tribe': 13, 'mucker': 12, 'targetglobal': 11, 'boxgroup': 10, 'threshold': 10, 'resoluteventures': 9, 'redpoint': 8, 'unusual': 8, 'projecta': 5, 'tmtinvestments': 5, 'sapphire': 4}

## Artifacts
- `artifacts/private_comps_backfill_final.json`
- `artifacts/fill_descriptions_web_report.json`
- `artifacts/assertive_tag_fill_report.json`
- `artifacts/before_desc_tag_stats.json`
