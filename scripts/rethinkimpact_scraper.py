#!/usr/bin/env python3
"""Rethink Impact portfolio scraper -> rethinkimpact_companies.json
Source: https://www.rethinkimpact.com/portfolio — US impact venture firm investing in female leaders using tech to
solve big problems; Squarespace page whose filterable logo grid is built by JS (read via headless Chrome): company
name (card title / logo alt), website (card link), and the firm's own sector and theme filters for each card
(sector buttons: Health, Education & Workforce, Financial Services, Sustainability; impact themes)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.rethinkimpact.com/portfolio"
PRIMARY = "Rethink Impact"
SECTOR_MAP = {"health": ["Health"], "education & workforce": ["Future of Work"],
              "financial services": ["FinTech / Insurance"], "sustainability": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=100000), "html.parser")
    labels = {}
    for b in s.select("button[data-group][data-filter]"):
        if b["data-filter"] != "all":
            labels[(b["data-group"], b["data-filter"])] = clean(b.get_text(" ", strip=True))
    out = []
    for a in s.select("a.ri-card"):
        img = a.find("img", alt=True)
        name = clean(a.get("title")) or (clean(img.get("alt")) if img else None)
        if not name:
            continue
        sectors = [labels.get(("sector", x), x) for x in (a.get("data-sectors") or "").split()]
        themes = [labels.get(("theme", x), x) for x in (a.get("data-themes") or "").split()]
        out.append(rec(name, None, a.get("href"), PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       sector_map=SECTOR_MAP, impact_themes=themes))
    if len(out) < 35:
        raise SystemExit(f"FATAL: only {len(out)} Rethink Impact companies")
    finish(out, "rethinkimpact", ("company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
