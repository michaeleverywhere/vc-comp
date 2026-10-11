#!/usr/bin/env python3
"""Endiya Partners portfolio scraper -> endiya_companies.json
Source: https://www.endiya.com/portfolio — Webflow CMS list
(.portfolio-list-items). Each card has the name (logo alt), Endiya's sector
(Enterprise / Agritech / Intelligent Mobility / ...), sub-tags, a one-line
description, a hidden category, a hidden stage label (Early / Growth — not a
funding round, kept in endiya_stage) and status (Active / Acquired). Detail
pages (/portfolio/<slug>) add a longer description, the company website,
founders and Milestones ("Partnered in YYYY", "Series A in YYYY", ...).
first_invested = Partnered year; stage = the latest funding round named in the
milestones. status: Active -> active, Acquired -> acquired.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, fetch_many, clean, tags_for, clean_url, year_of, stage_label,
                             prune_substring_tags, apply_tag_overrides, is_social)
from _d20_common import write_out

SOURCE_URL = "https://www.endiya.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "endiya_companies.json")
PRIMARY = "Endiya Partners"
SECTOR_TAG_MAP = {
    "agritech": ["Climate / Sustainability"], "intelligent mobility": ["Transportation / Mobility"],
    "healthcare": ["Health"], "life sciences": ["BioTech"], "fintech": ["FinTech / Insurance"],
    "consumer": ["Consumer"], "deeptech": ["Deeptech / Robotics / AR/VR"], "pharma": ["BioTech"],
}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "WATER®": ["Deeptech / Robotics / AR/VR"],
}
ROUND_RX = re.compile(r"\b(pre-seed|seed|pre-series [a-h]|series [a-h])\b", re.I)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio-list-items.w-dyn-item"):
            img = it.select_one("img")
            name = clean(img.get("alt")) if img else None
            a = it.select_one("a.portfolio-link[href]")
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            sec = [clean(x.get_text(" ")) for x in it.select(".company_sector[fs-cmsfilter-field=category]")]
            sec = [s for s in sec if s and s != "#"]
            tags = [clean(x.get_text(" ")) for x in it.select(".company_sector[fs-cmsfilter-field=tag]") if clean(x.get_text(" "))]
            d = it.select_one(".company_description-text")
            stg = it.select_one(".company-stage-hidden")
            st = it.select_one(".company-status-hidden")
            rows.append({"name": name, "href": urljoin(SOURCE_URL, a["href"]) if a else None,
                         "sectors": list(dict.fromkeys(sec + tags)), "tagline": clean(d.get_text(" ")) if d else None,
                         "endiya_stage": clean(stg.get_text(" ")) if stg else None,
                         "status": clean(st.get_text(" ")) if st else None})
    pages = fetch_many([r["href"] for r in rows if r["href"]], workers=4)
    out = []
    for r in rows:
        desc = site = None
        founders, partnered, stage, milestones = [], None, None, []
        html = pages.get(r["href"])
        if html:
            d = BeautifulSoup(html, "html.parser")
            for t in d(["script", "style", "nav", "footer"]):
                t.decompose()
            strings = [clean(s) for s in d.stripped_strings]
            strings = [s for s in strings if s]
            if "Milestones" in strings:
                i = strings.index("Milestones")
                for s in strings[i + 1:i + 12]:
                    if s in ("Website", "Founders", "Investment Team", "Sector"):
                        break
                    milestones.append(s)
            for m in milestones:
                if m.lower().startswith("partnered"):
                    partnered = year_of(m)
                rm = ROUND_RX.search(m)
                if rm:
                    stage = stage_label(rm.group(1))
            if "Founders" in strings:
                i = strings.index("Founders")
                for s in strings[i + 1:i + 8]:
                    if s in ("Investment Team", "Milestones", "Website", "Sector"):
                        break
                    founders.append(s)
            w = d.select_one("a.companies_website[href^=http]")
            if w and not is_social(w["href"]):
                site = clean_url(w["href"])
            # longer description: paragraph right after the company name heading
            for p in d.select("p"):
                t = clean(p.get_text(" "))
                if t and len(t) > 60 and t != r["tagline"] and "@" not in t:
                    desc = t
                    break
        st = (r["status"] or "").lower()
        rec = {
            "company_name": r["name"],
            "description": desc or r["tagline"],
            "tagline": r["tagline"],
            "company_url": site,
            "sectors": r["sectors"],
            "stage": stage,
            "endiya_stage": r["endiya_stage"],
            "milestones": milestones,
            "first_invested": partnered,
            "founders": founders,
            "site_status": r["status"],
            "status": "active" if st == "active" else ("acquired" if st == "acquired" else None),
            "location": None,
            "everywhere_tags": tags_for(r["name"], " ".join(x for x in (r["tagline"], desc) if x), r["sectors"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": r["href"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "stage", "first_invested", "founders", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
