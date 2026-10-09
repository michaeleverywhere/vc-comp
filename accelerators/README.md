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
- **2026-10-09 daily add** (`scrapers/batch_oct9.py`): Startup Wise Guys 311, Antler 1,087, EWOR 50,
  Accelerace 32 (public selection), Norrsken Evolve (formerly Norrsken Accelerator) 87, 8200 EISP 220
  (names only), UpWest 47, SOSA 10 (ILPN dealbook), Surge (Peak XV) 154, Axilor Ventures 58 = 2,056 rows.
  APX -> `no-public-output` (portfolio app gone); Rockstart left queued (sgcaptcha, not bypassed).
  Master `all_accelerator_companies.json`: 18,082 -> 20,138 rows. Junior-POC emails not published on
  sites were taken from Apollo (verified) and are flagged as such in `contacts.csv` Notes.
