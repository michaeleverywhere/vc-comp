"""Map data/accelerators/{slug}_companies.json -> Airtable "Accelerator Data" rows.

Writes artifacts used by both write paths:
  - REST upsert (airtable_upsert.py, needs a PAT with access to the base): PATCH
    with performUpsert on fieldsToMergeOn=[Name, Investors] -> idempotent re-runs.
  - CSV for Airtable's "Import CSV into existing table" (same columns).
Description is capped at DESC_CAP chars (sentence boundary) in Airtable; the full
published text stays in the JSON on GitHub.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "accelerators")
DESC_CAP = 250
COLS = ["Name", "Amount Raised", "Round", "Description", "Everywhere Sectors", "Verticles",
        "Team", "Investors", "Date of Announcement", "Source", "Website", "LinkedIn"]
# Website / LinkedIn (url fields) were requested 2026-10-06 but could not be created:
# the Airtable connector returned "requires authentication" on create_field. They are
# in the JSON + CSV; create them in Airtable (type URL) and set URL_FIELDS=1 for REST.
URL_FIELDS = os.environ.get("URL_FIELDS") == "1"
FIELD_IDS = {"Name": "fldFLQtq9YzcCRN8S", "Amount Raised": "fldUsjLahrjtnzAi8",
             "Round": "fldvX8BL6fMbAriwS", "Description": "fldNvFOIbUYq5MNvF",
             "Everywhere Sectors": "fldKNVrs4Teboh0pD", "Verticles": "fldNj3OAWrKGmq2HK",
             "Team": "fldMpAnb0Fow70UC7", "Investors": "fldL1HvlVQXcMoXfd",
             "Date of Announcement": "fldHhi9c9Oika0lSj", "Source": "fld2kaKXbbMFAJ8uE",
             "Website / Linkedin": "fldK9Co1ADuoHpcIa"}
# Michael added a single URL field "Website / Linkedin" (2026-10-06): website, else LinkedIn.
COMBINED_URL = os.environ.get("COMBINED_URL", "1") == "1"
ROUND_OK = {"Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Series D", "Series E", "Growth"}


def cap(s, n=DESC_CAP):
    s = (s or "").strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    k = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return (cut[:k + 1] if k > n * 0.5 else cut.rsplit(" ", 1)[0] + "…")


def rows(slug, csv_mode=False):
    d = json.load(open(os.path.join(DATA, f"{slug}_companies.json")))
    out = []
    for r in d["companies"]:
        f = {"Name": r["name"], "Amount Raised": r.get("amount_raised") or "",
             "Round": r.get("round") if r.get("round") in ROUND_OK else "",
             "Description": cap(r.get("description")),
             "Everywhere Sectors": r.get("everywhere_tags") or [],
             "Verticles": r.get("verticals") or "", "Team": r.get("team") or "",
             "Investors": r["investors"], "Date of Announcement": r.get("date") or "",
             "Source": r["source"]}
        if COMBINED_URL and not csv_mode:
            f["Website / Linkedin"] = r.get("website") or r.get("linkedin_url") or ""
        if URL_FIELDS or csv_mode:
            f["Website"] = r.get("website") or ""
            f["LinkedIn"] = r.get("linkedin_url") or ""
        out.append({k: v for k, v in f.items() if v})
    return out


def by_id(row):
    return {FIELD_IDS[k]: v for k, v in row.items()}


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "airtable_csv"), exist_ok=True)
    for slug in sys.argv[1:]:
        rs = rows(slug, csv_mode=True)
        with open(os.path.join(HERE, "airtable_csv", f"{slug}.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS)
            w.writeheader()
            for r in rs:
                w.writerow({**r, "Everywhere Sectors": ",".join(r.get("Everywhere Sectors", []))})
        print(slug, len(rs))
