#!/usr/bin/env python3
"""Stellaris Venture Partners portfolio scraper -> stellaris_companies.json
Source: https://www.stellarisvp.com/portfolio — Webflow + Finsweet CMS filter,
one page. Each card: name, status (Active / Inactive / Exited), one-line
description, theme(s) and entry stage (Idea / Seed / Series A). Each
/portfolio/<slug> page adds founders, PARTNERED year, co-investors and the
Stellaris team. The site links companies only via social profiles, so
company_url stays null.
Status: Active -> active, Exited -> acquired, Inactive -> null (raw kept).
"Idea" is Stellaris' pre-seed bucket label, not a named round -> stage null,
raw kept in entry_stage.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, year_of, stage_label, apply_tag_overrides

SOURCE_URL = "https://www.stellarisvp.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "stellaris_companies.json")
PRIMARY = "Stellaris Venture Partners"
SECTOR_TAG_MAP = {
    "healthcare": ["Health"], "fintech": ["FinTech / Insurance"], "sustainability": ["Climate / Sustainability"],
    "mobility": ["Transportation / Mobility"], "deeptech": ["Deeptech / Robotics / AR/VR"], "brands": ["CPG"],
    "commerce": ["Consumer"], "consumer tech": ["Consumer"],
}


def lines_after(st, label, stop):
    out, on = [], False
    for s in st:
        if s.strip().lower() == label.lower():
            on = True
            continue
        if on:
            if s.strip().lower() in stop:
                break
            out.extend(x for x in (clean(y) for y in s.split("\n")) if x)
    return list(dict.fromkeys(out))


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "PlatinumRx": ["Health"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for it in soup.select(".portfolio_company-wrap"):
        g = lambda f: clean(it.select_one(f"[fs-cmsfilter-field={f}]").get_text(" ")) if it.select_one(f"[fs-cmsfilter-field={f}]") else None
        name = g("name")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = it.select_one(".portfolio_company-details .text-weight-light")
        a = it.select_one("a[href^='/portfolio/']")
        themes = [clean(x.get_text()) for x in it.select("[fs-cmsfilter-field=theme]") if clean(x.get_text())]
        rows.append({"name": name, "status": g("status"), "desc": clean(d.get_text(" ")) if d else None,
                     "themes": themes, "stage": g("stage"), "href": urljoin(SOURCE_URL, a["href"]) if a else None})
        if limit and len(rows) >= limit:
            break
    details = fetch_many([r["href"] for r in rows if r["href"]])
    stops = {"partnered", "entry stage", "co-investor", "co-investors", "stellaris team", "why we invested", "journey"}
    out = []
    for r in rows:
        founders, year, coinv, team = [], None, [], []
        html = details.get(r["href"]) if r["href"] else None
        if html:
            st = list(BeautifulSoup(html, "html.parser").stripped_strings)
            founders = lines_after(st, "Founder", stops) or lines_after(st, "Founders", stops)
            year = year_of(label_after(st, "PARTNERED"))
            coinv = lines_after(st, "CO-INVESTOR", stops)
            team = lines_after(st, "STELLARIS TEAM", stops)
        stt = (r["status"] or "").lower()
        status = "active" if stt == "active" else ("acquired" if stt == "exited" else None)
        out.append({
            "company_name": r["name"],
            "description": r["desc"],
            "company_url": None,
            "company_profile_url": r["href"],
            "status": status,
            "site_status": r["status"],
            "entry_stage": r["stage"],
            "stage": stage_label(r["stage"]),
            "first_invested": year,
            "founders": founders,
            "co_investors": coinv,
            "stellaris_team": team,
            "sectors": r["themes"],
            "everywhere_tags": tags_for(r["name"], r["desc"], r["themes"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "status", "stage", "first_invested", "founders", "co_investors", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
