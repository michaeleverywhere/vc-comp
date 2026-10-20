#!/usr/bin/env python3
"""Black Tech Nation Ventures portfolio scraper -> blacktechnation_companies.json
Source: https://www.btn.vc/portfolio — BTN.vc's Webflow portfolio list: company name, one-line intro,
industry, stage (funding round), founded year, founders, website and the pop-out description."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, round_label
from _d50_common import rec, finish

SOURCE_URL = "https://www.btn.vc/portfolio"
PRIMARY = "Black Tech Nation Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in s.select(".portfolio-item.w-dyn-item"):
        h = it.select_one("h2") or it.select_one("h3")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        intro = it.select_one("a.portfolio-link-grid p.paragraph.tight")
        info = {}
        for b in it.select(".portfolio-info-block-white"):
            k = b.select_one(".portfolio-info-block-title-white")
            v = b.select_one("p")
            if k and v and clean(v.get_text(" ", strip=True)):
                info[clean(k.get_text(strip=True)).lower()] = clean(v.get_text(" ", strip=True))
        pop = it.select_one(".portfolio-item-pop-out > p.paragraph.tight")
        long_desc = clean(pop.get_text(" ", strip=True)) if pop else None
        web = info.get("website")
        if web and not web.startswith("http"):
            web = "https://" + web
        if web and is_social(web):
            web = None
        founders = info.get("founder(s)")
        yr = info.get("founded")
        out.append(rec(name, long_desc or (clean(intro.get_text(" ", strip=True)) if intro else None), web,
                       PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[info["industry"]] if info.get("industry") else None,
                       tagline=clean(intro.get_text(" ", strip=True)) if intro else None,
                       stage=round_label(info.get("stage")) or info.get("stage"),
                       founded_year=int(yr) if yr and yr.isdigit() else None,
                       founders=[clean(x) for x in founders.replace(" and ", ",").split(",") if clean(x)] if founders else []))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} BTN companies")
    finish(out, "blacktechnation", ("description", "company_url", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
