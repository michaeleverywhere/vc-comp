#!/usr/bin/env python3
"""S2G Investments (S2G Ventures) portfolio scraper -> s2g_companies.json
Source: https://www.s2ginvestments.com/companies — server-rendered (Wix) company
cards: name, "Exit" badge, description, sector and investment type links, and
company page link.
"""
import os, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.s2ginvestments.com/companies"
PRIMARY = "S2G Ventures"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
SECTOR_MAP = {"food & agriculture": ["CPG", "Climate / Sustainability"], "oceans": ["Climate / Sustainability"],
              "energy": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for h in soup.find_all(["h2", "h3", "h4", "h5"]):
        name = clean(h.get_text(" ", strip=True))
        box = h
        while box.parent is not None and not box.select('a[href*="?sector="]') and len(box.parent.get_text(" ", strip=True)) < 1500:
            box = box.parent
        if not name or not box.select('a[href*="?sector="]'):
            continue
        sectors = [clean(a.get_text(" ", strip=True)) for a in box.select('a[href*="?sector="]')]
        itype = [clean(a.get_text(" ", strip=True)) for a in box.select('a[href*="investmentType="]')]
        st = [clean(t) for t in box.stripped_strings]
        desc = max((t for t in st if t not in sectors and t != name and len(t) > 40), key=len, default=None)
        link = box.select_one('a[href*="/companies/"]')
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       status="exited" if "Exit" in st else "active", investment_type=", ".join(itype) or None,
                       detail_url=link["href"] if link else None))
    finish(out, "s2g", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
