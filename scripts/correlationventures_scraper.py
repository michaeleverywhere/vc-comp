#!/usr/bin/env python3
"""Correlation Ventures portfolio scraper -> correlationventures_companies.json
Source: https://correlationvc.com/companies/ — the company archive (JS-rendered, read via
headless Chrome): company name, Correlation's sector term (Consumer / Enterprise / Software /
Biopharma / Aerospace ...) and the site's own outcome label (IPO / acquired -> status). The
archive shows the firm's listed (mostly exited) companies; no descriptions or websites."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://correlationvc.com/companies/"
PRIMARY = "Correlation Ventures"
SECTOR_MAP = {"consumer": ["Consumer"], "biopharma": ["BioTech"], "aerospace": ["Deeptech / Robotics / AR/VR"],
              "digital health & hc services": ["Health"], "financial services": ["FinTech / Insurance"],
              "software": [], "enterprise": [], "hardware": ["Deeptech / Robotics / AR/VR"],
              "medical devices": ["Health"], "energy": ["Climate / Sustainability"]}
STATUS = {"ipo": "IPO", "acquired": "Acquired"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=20000), "html.parser")
    out = []
    for c in s.select(".l-CompanyArchive__cell"):
        n = c.select_one(".l-CompanyArchive__name")
        if not n:
            continue
        lab = c.select_one(".l-CompanyArchive__label")
        lab = clean(lab.get_text(" ", strip=True)).lower() if lab and clean(lab.get_text()) else None
        secs = [clean(t.get_text(" ", strip=True)) for t in c.select(".l-CompanyArchive__term")]
        out.append(rec(n.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in secs if x], sector_map=SECTOR_MAP,
                       status=STATUS.get(lab, lab.title() if lab else None)))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Correlation companies")
    finish(out, "correlationventures", ("sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
