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
| status | `queued` -> not scraped yet; `tracked` -> rows in Airtable; `no-public-output` -> no public portfolio (demo-day / announcement view); `unresolved` -> name from Michael's list not confidently identified (see `candidates`) |
| last_run, count | set by the routines (ISO timestamp, rows written) |
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
Key people / official contact pages per accelerator live in Airtable **Accelerator Contacts**
or, if that table is unavailable, `contacts.csv` here. Sources: accelerators' own sites and
official announcements only (no LinkedIn/Crunchbase/PitchBook). Emails are recorded only when
published verbatim; never guessed.
