# CLAUDE.md — VC portfolio datasets & scrapers

Guidance for working in this repo. Read this first; deeper build methodology is in
[`scripts/PLAYBOOK.md`](scripts/PLAYBOOK.md).

## What this repo is
Structured JSON datasets of VC firms' portfolio companies, plus the reusable Python
scrapers that produce them. Each dataset is one JSON array, one object per company.

Current datasets (in `data/`):
| firm | file | records | source |
|---|---|---|---|
| Lightspeed | `companies.json` | 425 | lsvp.com (built from sitemap; no script) |
| USV | `usv_companies.json` | 214 | usv.com/companies (`usv_scraper.py`) |
| Menlo Ventures | `menlo_companies.json` | 239 | menlovc.com/portfolio (`menlo_scraper.py`) |
| Insight Partners | `insight_companies.json` | 847 | insightpartners.com/portfolio (`insight_scraper.py`) |
| RRE Ventures | `rre_companies.json` | 250 | rre.com/portfolio (`rre_scraper.py`) |
| Founders Fund | `foundersfund_companies.json` | 62 | foundersfund.com/portfolio (`foundersfund_scraper.py`) |
| ICONIQ Growth | `iconiq_companies.json` | 100 | iconiq.com/growth/companies (`iconiq_scraper.py`) |
| Sequoia Capital | `sequoia_companies.json` | 412 | sequoiacap.com/our-companies (`sequoia_scraper.py`) |
| Andreessen Horowitz | `a16z_companies.json` | 849 | a16z.com/portfolio (`a16z_scraper.py`) |
| Accel | `accel_companies.json` | 766 | accel.com — own Sanity CMS API (`accel_scraper.py`) |
| Index Ventures | `index_companies.json` | 311 | indexventures.com/companies (`index_scraper.py`) |
| Kleiner Perkins | `kleinerperkins_companies.json` | 385 | kleinerperkins.com/partnerships (`kleinerperkins_scraper.py`) |
| NEA | `nea_companies.json` | 903 | nea.com — Statamic GraphQL (`nea_scraper.py`) |
| Greylock | `greylock_companies.json` | 159 | greylock.com/portfolio (`greylock_scraper.py`) |
| Bessemer | `bessemer_companies.json` | 516 | bvp.com/companies (`bessemer_scraper.py`) |
| Khosla Ventures | `khosla_companies.json` | 132 | khoslaventures.com sector pages (`khosla_scraper.py`) |
| General Catalyst | `generalcatalyst_companies.json` | 584 | generalcatalyst.com — own Algolia index (`generalcatalyst_scraper.py`) |
| Ribbit Capital | `ribbit_companies.json` | 148 | ribbitcap.com/rebels (`ribbit_scraper.py`) |
| Parkway VC | `parkway_companies.json` | 25 | parkway.vc/portfolio (`parkway_scraper.py`) |
| General Atlantic | `generalatlantic_companies.json` | 405 | generalatlantic.com/investments (`generalatlantic_scraper.py`) |
| Notable Capital | `notable_companies.json` | 127 | notablecap.com/companies (`notable_scraper.py`) |
| IVP | `ivp_companies.json` | 156 | ivp.com/portfolio `_payload.json` (`ivp_scraper.py`) |
| Dragoneer | `dragoneer_companies.json` | 29 | dragoneer.com/companies — curated subset (`dragoneer_scraper.py`) |
| Mayfield | `mayfield_companies.json` | 135 | mayfield.com/meet-our-founders (`mayfield_scraper.py`) |
| OrbiMed | `orbimed_companies.json` | 200 | orbimed.com/portfolio (`orbimed_scraper.py`) |
| Coatue | `coatue_companies.json` | 372 | coatue.com/portfolio API (`coatue_scraper.py`) |
| Spark Capital | `spark_companies.json` | 48 | sparkcapital.com/companies (`spark_scraper.py`) |
| SV Angel | `svangel_companies.json` | 150 | svangel.com/portfolio (`svangel_scraper.py`) |
| Battery Ventures | `battery_companies.json` | 343 | battery.com/company admin-ajax (`battery_scraper.py`) |
| Bedrock | `bedrock_companies.json` | 6 | bedrockcap.com/investments — full disclosure (`bedrock_scraper.py`) |
| Paradigm | `paradigm_companies.json` | 105 | paradigm.xyz/investments (`paradigm_scraper.py`) |
| Oak HC/FT | `oakhcft_companies.json` | 107 | oakhcft.com/portfolio (`oakhcft_scraper.py`) |
| Atlas Venture | `atlas_companies.json` | 79 | atlasventure.com/portfolio (`atlas_scraper.py`) |
| Venrock | `venrock_companies.json` | 250 | venrock.com — WP REST (`venrock_scraper.py`) |
| Meritech | `meritech_companies.json` | 48 | meritechcapital.com/companies (`meritech_scraper.py`) |
| Norwest | `norwest_companies.json` | 514 | norwest.com/companies (`norwest_scraper.py`) |
| CRV | `crv_companies.json` | 183 | crv.com/companies — RSC payload (`crv_scraper.py`) |
| Bain Capital Ventures | `baincapital_companies.json` | 269 | baincapitalventures.com — own Sanity API (`baincapital_scraper.py`) |
| Inflection Ventures | `inflection_companies.json` | 16 | inflectionvc.com/portfolio (`inflection_scraper.py`) |
| First Round Capital | `firstround_companies.json` | 190 | firstround.com/companies (`firstround_scraper.py`) |
| 8VC | `8vc_companies.json` | 172 | 8vc.com/companies (`8vc_scraper.py`) |
| TCV | `tcv_companies.json` | 151 | tcv.com/partnerships (`tcv_scraper.py`) |
| Lux Capital | `lux_companies.json` | 215 | luxcapital.com/companies via sitemap (`lux_scraper.py`) |
| ARCH Venture Partners | `arch_companies.json` | 128 | archventure.com/portfolio (`arch_scraper.py`) |
| Afore Capital | `afore_companies.json` | 100 | afore.vc/portfolio (`afore_scraper.py`) |
| Lerer Hippeau | `lererhippeau_companies.json` | 305 | lererhippeau.com/portfolio (`lererhippeau_scraper.py`) |
| 2048 Ventures | `2048_companies.json` | 75 | 2048.vc/companies (`2048_scraper.py`) |
| Hustle Fund | `hustlefund_companies.json` | 335 | hustlefund.vc/founders (`hustlefund_scraper.py`) |

**Firms verified to publish NO portfolio on their own site** (no dataset possible under the
no-third-party-sources rule): Benchmark, Thrive Capital, DST Global, Tiger Global, Altimeter,
Sutter Hill Ventures, Greenoaks. Each was exhaustively checked (sitemaps, guessed paths,
embedded JS) — their sites are minimal brochures / gated LP portals.

**Network note (2026-07-01):** this machine intermittently cannot route to Webflow's current
CDN IP (`cdn.webflow.com` → 198.202.211.1). Affected scrapers (`parkway`, `khosla`, `spark`,
`oakhcft`, `8vc`, `lux`, `dragoneer`, also existing `rre`/`iconiq`) implement a fallback chain:
direct HTTPS → legacy-IP pin (75.2.70.75) → `r.jina.ai` read-only relay of the same page. On a
healthy network they use the direct route. Datasets fetched relay-only at build time: 8VC, Lux,
Dragoneer, Spark (spot-checked correct; re-run to refresh when routing is healthy). Afore
(`afore_companies.json`, added 2026-07-22) was transcribed from afore.vc's own portfolio page via
a read-only fetch relay for the same reason — its `afore_scraper.py` carries the standard
direct→legacy-IP→r.jina.ai fallback chain and re-derives straight from the source HTML on a
healthy network (verify the Finsweet card selectors against live markup on the first clean re-run).

## Layout
```
VC comps/
├── CLAUDE.md                 ← this file
├── railway.toml              ← Railway build/cron config (repo root; see §Automation)
├── requirements.txt          ← repo-root deps for Railway (requests, bs4)
├── data/                     ← ALL JSON (datasets + reports)
│   ├── companies.json + 47× <firm>_companies.json   (one per firm — see table above)
│   ├── + 6 generic-discovered thin datasets (felicis, amplifypartners, homebrew,
│   │     signalfire, foundrygroup, wingvc — name+url only, no bespoke scraper yet)
│   ├── enrichment_report.json          ← provenance for enrich.py fills
│   └── everywhere_tagging_report.json  ← Lightspeed tagging report
├── scripts/                  ← per-firm scrapers (47 bespoke; source in each docstring)
│   ├── enrich.py             ← Wikidata back-fill of empty fields
│   └── PLAYBOOK.md           ← how to scrape a new firm / per-source cheat-sheet
└── automation/               ← nightly Railway pipeline (see §Automation below)
```
Scripts resolve `../data` relative to their own file, so run from the repo root:
`python3 scripts/usv_scraper.py` (writes `data/usv_companies.json`). Each scraper has a
`--limit N` flag for quick test runs. Deps: `pip install requests beautifulsoup4`.

## Core principles (do not violate)
- **Site-tailored schema.** Only include fields the source actually exposes. Don't force
  every firm into the same shape; each `*_companies.json` has its own field set.
- **Never fabricate.** Missing scalar → `null`; missing list → `[]`. If the site doesn't
  publish it, leave it empty.
- **`scraped_at`** = the real run timestamp (ISO-8601 UTC). If genuinely unknown, `null` —
  never a guessed/today's date passed off as the scrape time. (Lightspeed `companies.json`
  has `scraped_at = null` for this reason.)
- **No Crunchbase / LinkedIn / PitchBook / investor databases.** External enrichment is
  Wikidata-only (see below).
- Most empty cells are **legitimately N/A** (e.g. exit/acquirer/ticker for active
  companies; sector when the firm never tags it). That is not "missing data" to invent.
- **Empty ≠ absent.** Before declaring a field N/A, check whether the data is *denormalized*
  into the **name suffix** (`Foo (Acquired)`, `Bar (NYSE: TICK)`) or **description prose**
  ("Acquired by X in YYYY"). A structured field that's empty for *every* record is a cue to
  go look there, not proof the site omits it. (See PLAYBOOK §Recon "Empty ≠ absent".)

## `everywhere_tags` taxonomy (exactly these 17 — verbatim spelling)
```
BioTech
Health
Cybersecurity
Dev Tools / Cloud
Consumer
Future of Work
Transportation / Mobility
FinTech / Insurance
RegTech/Gov/Legal
Deeptech / Robotics / AR/VR
Data & Analytics
Logistics / Supply Chain
Web3 / Crypto
PropTech
Gaming / Media / Entertainment
CPG
Climate / Sustainability
```
Rules:
- **AI alone is not a category** — classify an AI company by the *market it serves*
  (AI for devs → Dev Tools / Cloud; for work → Future of Work; for health → Health; etc.).
- Include a **vertical + enabling-tech** tag only when both clearly apply (e.g. health data
  → `Health` + `Data & Analytics`); if one is much weaker, drop it.
- Don't use **Consumer** or **Future of Work** as catch-alls.
- Order most→least relevant; **cap at 4**; no duplicates; every value must be one of the 17.
- Derive from the firm's own sector tags first (when present), else keyword-classify the
  name + description. Tagging is keyword-based (no LLM) and intentionally coarse — a few
  untagged stragglers / over-tags are acceptable.

## Enrichment (`scripts/enrich.py`)
Back-fills empty fields in `companies.json`, `menlo_companies.json`, `usv_companies.json`
from **Wikidata** (free + attributable):
- **Fills ONLY empty fields; never overwrites** a non-empty value.
- Matches a company to its Wikidata item by **verified official-website (P856) domain** —
  ambiguous name-only matches are skipped (prevents wrong data).
- Pulls founders (P112), founding year (P571), industry→sectors (P452), ticker (P414/P249).
- Records every fill + source Q-id in `data/enrichment_report.json`.
- Coverage is partial by design (well-known companies match; long-tail private startups
  won't). Re-runnable and idempotent.

## Conventions
- Politeness: custom User-Agent, timeouts, retries/back-off, small sleeps between requests.
- **Remote: `https://github.com/michaeleverywhere/vc-comp` (public) — the manager's
  account, since 2026-07-24.** `ruszinn` is a Write collaborator; `origin` points there
  and plain `git push` works. The old `ruszinn/vc-comp` still exists but is retired —
  don't push to it. Because Railway commits data nightly, the remote is often ahead:
  **always `git pull origin main --no-rebase --no-edit` before pushing.**
- **Commit and push only when the user asks.** Concise message; NO co-author trailer
  (user preference, 2026-07-24). Commits use
  `git -c user.email="ruszinfilay@gmail.com" -c user.name="rus.perish"`.
- Use `/tmp` (or the session scratchpad) for recon HTML/temp files, not the repo.

## Quickstart: add a new VC firm
Preferred: add `{firm_name, homepage}` to `automation/candidates.json`, push, and let the
discovery service handle it (finds the portfolio page, scrapes, adds to Airtable, and the
scraper factory attempts a bespoke scraper). Manual path (for hard sites):
1. Recon the portfolio page (`curl` raw HTML; identify the data source). See PLAYBOOK §Recon.
2. Write `scripts/<firm>_scraper.py` following the shared template (PLAYBOOK §Template);
   output `data/<firm>_companies.json` with a site-tailored schema + `everywhere_tags`.
3. Test with `--limit`, then full run; validate (PLAYBOOK §Validation).
4. Optionally `python3 scripts/enrich.py` (add the file to its list) to Wikidata-fill gaps.

## Automation (`automation/` — Railway → Airtable, built 2026-07-23/24)
One self-contained pipeline; **no Zapier anywhere** (evaluated, then removed). Core idea:
a new firm is just a firm whose previous dataset is empty, so one loop handles both
discovery and refresh. Modes: `python3 automation/pipeline.py --mode discover|refresh|all`.

**Data flow:** roster (dedup once, keyed on `data/<slug>_companies.json` filenames) →
per firm: scrape (bespoke script | generic extractor) → diff vs GitHub (added/dropped/
exited + health; `safe_to_commit` guard blocks empty/>20%-crater overwrites) → commit to
GitHub → **direct Airtable upsert** (`airtable_writer.py`, matched on `Data file`) with
auto-fill of every blank metadata cell (Name, Source URL, Notes, Source type, Scraper
module — via `names.py`; nothing is ever entered by hand, existing values never overwritten).

**Airtable:** base `Comps - Automations` (`appdSRg0657zG3oef`), table **`Private Comps`**
(NOT "Portfolio Companies" — that table exists but was cut from scope; `backfill_airtable.py`
is legacy). Table = 1 row per firm: registry metadata + Record/Prev/Delta count, `Scraper
health` (new/grew/same/shrank/count-drop/broke), Status (+`needs-scraper`,`broke`), Last
run/commit, and **17 per-tag Number columns** (exact taxonomy names; note `Health` the tag
≠ `Scraper health`) holding how many portfolio companies carry each tag (double-counting
across tags is intended). `create_at_fields.py` created the schema; `fix_dupes.py`/`audit_at.py`
repaired a dup incident (trailing-whitespace Data-file keys — root cause fixed).

**Railway** (project on user's account, deploys from `michaeleverywhere/vc-comp`, root dir
= repo root): service 1 "discovery" — `--mode discover`, cron daily `0 7 * * *`, LIVE and
verified (added Amplify 124 / Homebrew 106 / SignalFire 103 / Foundry Group / Wing VC;
6 JS-heavy sites correctly flagged needs-scraper: emergence, foundation, uncork, craft,
boldstart, costanoa — they retry every run until scraped or removed from candidates.json).
Railway vars: GITHUB_TOKEN (fine-grained, **must be created on michaeleverywhere**,
Contents r/w on the one repo), GITHUB_REPO=michaeleverywhere/vc-comp, GITHUB_BRANCH,
GITHUB_DATA_DIR, AIRTABLE_PAT (data.records read+write), AIRTABLE_BASE_ID, AIRTABLE_TABLE.
Local `automation/.env` mirrors these (git-ignored; Airtable schema-write PAT stays
laptop-only). Data commits from Railway land as `Nightly: <slug> …`.

**Scraper factory** (`scraper_gen/guard/runner/factory.py`, wired into discover mode):
auto-generates BESPOKE rich scrapers via Claude API — user chose **no human approval**, so
three machine gates replace review: AST allowlist (no env/subprocess/eval/open/getattr…),
sandboxed run with token-scrubbed env, output validation (≥10 recs, ≥50% of generic
baseline, ≥95% names, ≥60% urls, ≥30% descriptions, no stringified lists/dicts). Pass → commit scraper (trusted
runnable footer) + rich dataset; the push triggers Railway rebuild so the firm becomes
bespoke. Generate-once per firm; `GEN_MAX_PER_RUN=3`; targets = the 6 thin datasets first
(proven scrapeable), then needs-scraper candidates. Accepted residual risk: subtly-wrong
values can pass validation (revert the firm's commit if so). All gates verified offline;
**never yet run live**.
**Attempt memory + burst retries (added 2026-07-26, burst 2026-07-27;**
`automation/gen_state.py`**):** per user decision, a firm gets its WHOLE generation
budget the first night it's tried: `attempt()` bursts up to `GEN_MAX_ATTEMPTS` (default 3)
tries in one run — site context fetched once, each retry prompted with the burst's
earlier failure reasons + last code so it varies its approach; the context block is
cache-marked (prompt caching: retries pay ~10% input on it, usage printed per call)
— and if none passes the
gates the firm is **retired the same night** (no rolling backlog; every targeted firm
leaves the queue as bespoke or retired). Failures are logged to `data/gen_attempts.json`
(committed via the store like a dataset, so ephemeral Railway runs read it back; local
runs use the file directly); retired/`"skip": true` firms are filtered out of `targets()`
*before* the `[:GEN_MAX_PER_RUN]` slice (`GEN_MAX_PER_RUN` still caps FIRMS per run).
`generation error:` API-transport flukes abort the burst uncounted (firm retries next
run). Manual `"skip": true` = "legitimately thin, leave it alone"; success deletes the
firm's entry; re-arm a retired firm by deleting/editing its entry.

**State at session end (2026-07-24):**
- DONE: pipeline + direct Airtable write live; discovery service live & verified; Private
  Comps fully populated (53 firm rows + auto-named/auto-filled); repo moved to
  michaeleverywhere; Source-URL back-fill fix deployed.
- PENDING (next session picks up here):
  1. Push the scraper factory (`git add automation/ && git commit -m "Add scraper factory" 
     && git pull --no-rebase && git push`) — may already be pushed; check `git log`.
  2. Add `ANTHROPIC_API_KEY` (+ optional GEN_*) to the discovery service on Railway
     (user sets a spend limit in the console), then Run Now and review `[factory]` log lines.
  3. Create Railway service 2 "refresh": same repo/vars, Start Command override
     `python3 automation/pipeline.py --mode refresh`, cron `0 8 1 * *` (monthly). NOT yet created.
  4. Optional cleanup: retire `railway_service`-era leftovers (`backfill_airtable.py`,
     "Portfolio Companies" table), decide fate of the 6 needs-scraper rows (factory may
     convert some), prune stale candidates from `candidates.json`.
- Docs debt: `automation/PIPELINE.md`/`README.md` still describe the retired Zapier flow
  in places; this section is authoritative where they conflict.
- Context: repo stays **public** (dashboard agent reads raw.githubusercontent.com links
  tokenlessly; raw links + private repo are incompatible). The user's manager (Michael)
  owns the repo + a dashboard agent that consumes the raw JSON links.
