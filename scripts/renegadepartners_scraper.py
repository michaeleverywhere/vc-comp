#!/usr/bin/env python3
"""Renegade Partners portfolio scraper -> renegadepartners_companies.json
Source: https://www.renegadepartners.com/companies — Webflow tabs (All, AI & ML,
Fintech, Infra, Enterprise, Vertical SaaS, Consumer). Each card links to the
company's own site and shows Renegade's round label, e.g. "Led Series A",
"Co-Led Series B", "Seed" — or "Acquired". The round becomes `stage`
(the round Renegade invested in); "Acquired" becomes status. The site has no
descriptions; they are back-filled from company websites separately.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, round_label

SOURCE_URL = "https://www.renegadepartners.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "renegadepartners_companies.json")
PRIMARY = "Renegade Partners"
SECTOR_TAG_MAP = {"fintech": ["FinTech / Insurance"], "infra": ["Dev Tools / Cloud"], "consumer": ["Consumer"]}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    tabs = {a.get("data-w-tab"): clean(a.get_text(" ")) for a in soup.select("a[data-w-tab]")}
    try:
        with open(OUT, encoding="utf-8") as fh:
            prev = {x["company_name"].lower(): x for x in json.load(fh)}
    except (OSError, ValueError):
        prev = {}
    recs = {}
    for pane in soup.select("div[data-w-tab]"):
        tab = tabs.get(pane.get("data-w-tab"))
        for c in pane.select("a.companies-card:not(.w-condition-invisible)"):
            t = c.select(".card-text-holder > div")
            name = clean(t[0].get_text(" ")) if t else None
            if not name:
                continue
            label = clean(t[1].get_text(" ")) if len(t) > 1 else None
            r = recs.setdefault(name.lower(), {"name": name, "url": (c.get("href") or "").strip(), "label": label, "cats": []})
            if tab and tab != "All" and tab not in r["cats"]:
                r["cats"].append(tab)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for key, r in recs.items():
        label = r["label"] or ""
        old = prev.get(key) or {}
        desc = old.get("description")
        acquired = label.lower() == "acquired"
        out.append({
            "company_name": r["name"],
            "description": desc,
            "company_url": r["url"] if r["url"].startswith("http") else None,
            "status": "acquired" if acquired else None,
            "stage": None if acquired else round_label(label),
            "investment_stage_raw": label or None,
            "renegade_led": ("led" in label.lower()) if label and not acquired else None,
            "sectors": r["cats"],
            "everywhere_tags": old.get("everywhere_tags") or tags_for(r["name"], desc, r["cats"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
