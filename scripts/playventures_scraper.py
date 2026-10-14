#!/usr/bin/env python3
"""Play Ventures portfolio scraper -> playventures_companies.json
Source: https://www.playventures.vc/portfolio — Webflow CMS .portfolio-item popups
(stage, Active/Exit status, name, tagline, description, website, category,
founders, country + region).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.playventures.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "playventures_companies.json")
PRIMARY = "Play Ventures"
SECTOR_TAG_MAP = {"gaming content": ["Gaming / Media / Entertainment"], "b2b / infrastructure": [], "games": ["Gaming / Media / Entertainment"], "gaming": ["Gaming / Media / Entertainment"],
                  "consumer": ["Consumer"], "fintech": ["FinTech / Insurance"], "web3": ["Web3 / Crypto"],
                  "health": ["Health"], "ai": [], "b2b": []}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-item"):
        def f(sel):
            el = it.select_one(sel)
            return clean(el.get_text(" ")) if el else None
        name = f(".portfolio-title")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        exit_el = it.select_one(".portfolio-exit")
        exited = bool(exit_el and "w-condition-invisible" not in (exit_el.get("class") or []))
        status_raw = f("[fs-cmsfilter-field=status]")
        a = it.select_one(".portfolio-popup-content-body a[href^=http]")
        cat = f("[fs-cmsfilter-field=category]")
        founders = f("[fs-cmsfilter-field=founders]")
        st = (status_raw or "").lower()
        status = "active" if st == "active" else ("acquired" if "acqui" in st else None)
        out.append({
            "company_name": name,
            "tagline": f(".portfolio-hover .text-block-4"),
            "description": f(".portfolio-popup-content-body .text-block-4:not(a)"),
            "company_url": clean_url(a["href"]) if a else None,
            "stage": stage_label(f(".portfolio-stage")),
            "stage_raw": f(".portfolio-stage"),
            "site_status": status_raw,
            "status": status,
            "exited": exited or st in ("exit", "exited"),
            "sectors": [cat] if cat else [],
            "founders": [clean(x) for x in re.split(r",|&| and ", founders or "") if clean(x)],
            "location": f("[fs-cmsfilter-field=country]"),
            "region": f("[fs-cmsfilter-field=region]"),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], " ".join(x for x in (r["tagline"], r["description"]) if x),
                                        r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "stage", "status", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
