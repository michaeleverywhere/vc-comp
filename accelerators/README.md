# Accelerator tracking

`queue.json` is the registry/queue for the **Accelerator Data** table
(Airtable base `appdSRg0657zG3oef`, table `tblM2JO3HToYoV1Bi`; one row per company that
went through an accelerator).

## Entry fields
| field | meaning |
|---|---|
| name, slug | display name; unique slug |
| official_site | the accelerator's own site (verified live 2026-10-05) |
| portfolio_url | public portfolio / cohort / company directory, or `null` |
| priority_tier | `list1` (priority; deep history incl. past years), `list2`, `abroad` |
| status | `queued` -> not scraped yet; `tracked` -> rows in Airtable; `no-public-output` -> no public portfolio (demo-day / announcement view); `unresolved` -> name from Michael's list not confidently identified (see `candidates`); `scraped-airtable-pending` -> scraped and committed (`data_file`, `airtable_csv`) but not yet in Airtable; import the CSV or run `airtable_upsert.py` with a base-scoped PAT, then flip to `tracked` (daily add skips it) |
| last_run, count | set by the routines (ISO timestamp, companies scraped) |
| airtable_rows, commit, data_file, airtable_csv | rows currently in Airtable, repo commit of the data, JSON / CSV paths |
| notes, input_name, region, parent, candidates | context; `input_name` is Michael's original spelling |

## Routines (start 2026-10-06)
- **Daily add, 10:06am ET**: take the next 10 `queued` entries in file order (list1 -> list2 -> abroad),
  scrape, write rows, set `status=tracked`, `last_run`, `count`. Entries with `portfolio_url=null`
  should be checked and flipped to `no-public-output` if nothing public exists.
- **Refresh, 6:06pm ET**: refresh ~1.67% of `tracked` entries per day (oldest `last_run` first) so
  every accelerator cycles every 60 days.
- Skip `unresolved` until Michael confirms the name.
- Sub-programs (`parent` set, e.g. HAX under SOSV) must be de-duplicated against the parent portfolio.

## Contacts
Key people / official contact pages per accelerator are in `contacts.csv` (columns match the
planned Airtable table **Accelerator Contacts**: Name, Title or Role, Accelerator, Email,
Contact Page URL, Source URL, Notes). On 2026-10-05 the Airtable table could not be created
(the Airtable connector returned "requires authentication" on table creation), so the CSV is
the system of record until it is imported (Airtable > Add table > Import CSV; set Email=email,
URL columns=url). Sources: accelerators' own sites and
official announcements only (no LinkedIn/Crunchbase/PitchBook). Emails are recorded only when
published verbatim; never guessed.

## Website / LinkedIn (2026-10-06)
JSON and CSVs carry `website` and `linkedin_url`. LinkedIn URLs come only from the accelerator's
listing (YC, Techstars, SOSV/HAX) or a link on the company's own site (`linkedin_source`); LinkedIn
itself is never fetched. The Airtable fields **Website** and **LinkedIn** (type URL) still need to be
created (create_field returned "requires authentication"); then run `URL_FIELDS=1 airtable_upsert.py`.

## Run log
- **2026-10-26 refresh** (`scrapers/launch_refresh.py`, `scrapers/venturekick_cdp_list.py` + `scrapers/venturekick_refresh.py`, never-remove): LAUNCH Accelerator 107 -> 115 (+8 from LA37, Cohort 37 · September 2026: LineLint, Hank, Steve AI, Maverick, Listabid, Hermetiq, Church AI, LEVA; LA37 is now most_recent_batch). Venture Kick 1,044 -> 1,050 (+6: ExomIQ, Direc Recycling, dotted space, EasyDash, Sanafin, Synameta Therapeutics; SimCase SA renamed Simmy - SimCase SA; 215 companies no longer on the 835-entry public listing kept and marked listed_on_site=false). Master `all_accelerator_companies.json`: 39,426 -> 39,440 rows.
- **2026-10-20 late-night add, chunk D** (`scrapers/batch_oct20d.py`): Founders, Inc. 192, Sting 334, Bethnal Green Ventures 105, SpinLab - The HHL Accelerator 144, Taiwan Tech Arena (TTA) 1,233, YES!Delft 15, Hatch Blue 73, AngelPad 41, NSRCEL (IIM Bangalore) 23, Village Capital 357 = 2,517 rows. Village Capital alumni paged with the site's own Next button in headless Chrome (scrapers/cdp.py). Master `all_accelerator_companies.json`: 35,500 -> 38,017 rows.
- **2026-10-20 late-night add, chunk C** (`scrapers/batch_oct20c.py`): Elemental Impact 144, JFDI.Asia 50, Urban Future Lab 149, UnternehmerTUM 24, Ag Startup Engine 39, Plug and Play APAC 348, LabCentral 95 = 849 rows. Plug and Play APAC directory loaded in headless Chrome (scrapers/cdp.py) by pressing the page's Load More. Master `all_accelerator_companies.json`: 34,651 -> 35,500 rows.
- **2026-10-20 late-night add, chunk B** (`scrapers/batch_oct20b.py`): gener8tor 2,131, Berkeley SkyDeck 358, Harvard Innovation Labs 869, Founder Institute 101, MIT delta v 263, Melbourne Accelerator Program (MAP) 127 = 3,849 rows. gener8tor and SkyDeck lists are loaded the way the sites load them in a browser (headless Chrome, scrapers/cdp.py). Master `all_accelerator_companies.json`: 30,802 -> 34,651 rows.
- **2026-10-20 late-night add, chunk A** (`scrapers/batch_oct20a.py`): Capital Factory 832, Dreamit Ventures 122, Greentown Labs 743, ERA (Entrepreneurs Roundtable Accelerator) 384, Blue Startups 57, AI Grant 92, Agoranov 529 = 2,759 rows. Master `all_accelerator_companies.json`: 28,043 -> 30,802 rows.
- **2026-10-20 restore (never-remove rule)**: Michael's standing rule (2026-10-20): refreshes never remove companies; companies no longer on the source site stay with all their data and are marked `listed_on_site: false`, `delisted_date`, `last_seen` (`first_seen` where known). Restored from git history: Seedcamp 318 -> 334 (the 16 dropped in 75dc013), Alchemist 509 -> 513 (EDEN, Simularge, nCorium, Grandeur, dropped in fd96b8d), Y Combinator 6,177 -> 6,178 (hiloop, dropped from YC's index in eb81765; SuperRadiant was a rename to Primordiant and is already present). Betaworks' 8 nav/junk rows removed in 2806e01 were not restored. Master `all_accelerator_companies.json`: 28,022 -> 28,043 rows.
- **2026-10-20 refresh** (`scrapers/batch_oct6_b.py entrepreneursfirst seedcamp`, scraped to a temp file, diffed and merged onto the existing files so earlier enrichment is kept): Entrepreneurs First 48 -> 48 (public portfolio unchanged; no cohort labels). Seedcamp 327 -> 318: +7 now listed (Solvera, Vessla, Neywa Labs, Marble, Awear and Depi in Seedcamp 2026, plus Caveman, name only); 16 no longer on Seedcamp's page were removed (Lupin & Holmes, Crowd.dev, Rosita, kitch, Skew, Passbase, Speechly, Parla, Fleksy, Lateral, Pointy, ShareLaTex, Server Density, Talasim, ubervu, rentmineonline); Pento's website now points to hibob.com per Seedcamp. Master `all_accelerator_companies.json`: 28,031 -> 28,022 rows.
- **2026-10-19 refresh** (`scrapers/batch_oct6_b.py longbeachaccelerator alchemist`, scraped to a temp file, diffed and merged onto the existing files so earlier enrichment is kept): Long Beach Accelerator 46 -> 46 (portfolio unchanged; earlier funding enrichment kept; a LinkedIn link offered as SolarView's website was not used). Alchemist Accelerator 513 -> 509: EDEN, Simularge, nCorium and Grandeur are no longer returned by Alchemist's public portfolio API and were removed; no new companies (newest portfolio labels still Classes 123 and 125); Alchemist's own text updated for 6 companies (descriptions/teams, e.g. Luce Labs, Frontier Bio, Kaspix, redfly.ai) and Kaspix's published raise $1.15M -> $1.3M. Master `all_accelerator_companies.json`: 28,035 -> 28,031 rows.
- **2026-10-18 refresh** (`scrapers/batch_oct6_b.py grishinrobotics agihouse`, scraped to a temp file and diffed against the existing files): Grishin Robotics 26 -> 26 and AGI House 24 -> 24; no new, renamed or dropped companies and no field changes, so existing files and enrichment were left unchanged. Master `all_accelerator_companies.json`: 28,035 rows (unchanged).
- **2026-10-17 refresh** (`scrapers/batch_oct6_b.py gravitylabs defy`, diffed and merged onto the existing files so earlier funding enrichment is kept): Gravity Labs 9 -> 9 (studio portfolio unchanged). Defy VC 77 -> 78 (+Town, "The AI assistant that does the work."); websites filled for 36 companies from links on their Defy company pages; scraper now skips X, YouTube and news-article links as websites. Defy publishes no cohorts. Master `all_accelerator_companies.json`: 28,034 -> 28,035 rows.
- **2026-10-16 refresh** (`scrapers/small.py betaworks` and `scrapers/emersoncollective.py`, diffed and merged onto the existing files so earlier enrichment is kept): Betaworks Camp 101 -> 101 (no new camp cohort published; AI Camp: The New Agent Economy applications open; descriptions filled from company sites for Graze Social and Earplay, refreshed for PillPilot and Armilla; Earplay LinkedIn from its own site). Emerson Collective 67 -> 67 (published selection unchanged). Master `all_accelerator_companies.json`: 28,034 rows (unchanged).
- **2026-10-15 refresh** (`scrapers/small.py seraphimspace catalystaccelerator`, diffed against the existing files): Seraphim Space Accelerator 92 -> 92 and Catalyst Accelerator 179 -> 179; no new, renamed or dropped companies (Catalyst's newest cohorts, BMC3I TAP Lab Cohort 4 Spring 2026 and Investment Readiness Boot Camp Fall 2026, already loaded); existing files and enrichment left unchanged. Master `all_accelerator_companies.json`: 28,034 rows (unchanged).
- **2026-10-14 refresh** (`scrapers/small.py pearvc`, merged onto the existing file so earlier website/LinkedIn enrichment is kept): Pear VC 212 -> 213 (+Phinity Labs, Pre-Seed, autonomous chip design); no dropped or renamed companies; Pear publishes no cohort labels. Master `all_accelerator_companies.json`: 28,033 -> 28,034 rows.
- **2026-10-13 refresh** (`scrapers/small.py zfellows`): Z Fellows 19 -> 19 (same homepage alumni; no new, renamed or dropped companies; earlier full-name team/funding enrichment kept). Master `all_accelerator_companies.json`: 28,033 rows (unchanged).
- **2026-10-12 refresh** (`scrapers/small.py southparkcommons`): South Park Commons 202 -> 202 (Preference Models renamed to Preference Model, `former_name` kept; no new companies; founded-2026 cohort of 10 already loaded). Master `all_accelerator_companies.json`: 28,033 rows (unchanged).
- **2026-10-09 daily add** (`scrapers/batch_oct9.py`): Startup Wise Guys 311, Antler 1,087, EWOR 50,
  Accelerace 32 (public selection), Norrsken Evolve (formerly Norrsken Accelerator) 87, 8200 EISP 220
  (names only), UpWest 47, SOSA 10 (ILPN dealbook), Surge (Peak XV) 154, Axilor Ventures 58 = 2,056 rows.
  APX -> `no-public-output` (portfolio app gone); Rockstart left queued (sgcaptcha, not bypassed).
  Master `all_accelerator_companies.json`: 18,082 -> 20,138 rows. Junior-POC emails not published on
  sites were taken from Apollo (verified) and are flagged as such in `contacts.csv` Notes.
- **2026-10-09 refresh** (`scrapers/techstars_refresh.py`): Techstars 5,662 -> 5,663 (+Tessera Defense Systems,
  Techstars Space 2026; BeautyGoGO -> Vylvet and TawkitAI -> CopilotKit renamed in Techstars' index, `former_name` kept).
  Master `all_accelerator_companies.json`: 20,138 -> 20,139 rows.
- **2026-10-10 daily add** (`scrapers/batch_oct10.py`, headless-Chrome helper `scrapers/cdp.py`): Rockstart 247,
  Venture Catalysts 233, Iterative 191, AppWorks 115, SparkLabs 185, Open Network Lab 205, Brinc 94, Startmate 317,
  Cicada Innovations 77, Creative HQ (Lightning Lab) 402 = 2,066 rows. T-Hub and MiraclePlus -> `no-public-output`
  (no public company list / only 12 representative names). Master `all_accelerator_companies.json`: 20,139 -> 22,205 rows.
- **2026-10-10 refresh** (`scrapers/sosv_refresh.py`, merges a fresh `sosv.py` pull onto the existing file, keeping
  earlier enrichment): SOSV 781 -> 781 (HAX 211, IndieBio 240 unchanged); no new companies (newest cohorts HAX Seed 2026,
  IBSF 25H2, IndieBio NY 2025 H2 already loaded). Field updates: Upright and Allied Microbiota `founded_year`, Neurode website.
  Master `all_accelerator_companies.json`: 22,205 rows (unchanged).
- **2026-10-11 daily add** (`scrapers/batch_oct11.py`): Start-Up Chile 516 (BIG/generation announcement posts +
  featured portfolio; listed `todas-las-startups` URL is 404), Platanus 93, NXTP Ventures 56 (names from company sites),
  Parallel18 531, Cubo Itaú 511 (Cubo's own startup API), Flat6Labs 133 (portfolio now published by F6 Ventures, f6.vc,
  + 9 Riyadh Seed Program startups on flat6labs.com), MEST Africa 36, CcHUB 45, Founders Factory Africa 40, Hub71 316
  = 2,277 rows. QBO Innovation Hub -> `no-public-output` (only 8 INQBATION 2020 pitch winners listed). Master
  `all_accelerator_companies.json`: 22,205 -> 24,482 rows. Junior-POC emails not on sites came from Apollo (verified).
- **2026-10-12 daily add** (`scrapers/batch_oct12.py`): Creative Destruction Lab 1,907, DMZ 279,
  Velocity (University of Waterloo) 89, Next Canada 484, Centech 9 (Été 2026 featured cohort only),
  Accelerator Centre 634, District 3 149 = 3,551 rows. Communitech -> `no-public-output` (no public
  company portfolio on communitech.ca). Queue emptied (0 remaining queued). Master
  `all_accelerator_companies.json`: 24,482 -> 28,033 rows. Junior-POC emails not on sites came from
  Apollo (verified) and are flagged in `contacts.csv` Notes.
