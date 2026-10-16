#!/usr/bin/env python3
"""Axeleo Capital (AXC) portfolio scraper -> axeleo_companies.json
Source: https://axc.vc/portfolio/ — server-rendered (Astro) grid. Each card
carries data-sort-name (company), data-filter-indices (mapped through the
page's filter buttons: Greentech / Digital sector, Running companies / Exits),
a website link and, for exits, a caption such
as "Exit. Docebo".
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://axc.vc/portfolio/"
PRIMARY = "Axeleo Capital"
SECTOR_MAP = {"greentech": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    filt = {}
    for b in soup.select("button.portfolio-filter-btn[data-filter-index]"):
        filt[b["data-filter-index"]] = (clean(b.get("data-sector")), clean(b.get("data-status")))
    out = []
    for c in soup.select("[data-sort-name][data-filter-indices]"):
        name = clean(c["data-sort-name"])
        if not name:
            continue
        sectors, statuses = [], []
        for i in c["data-filter-indices"].split(","):
            sec, st = filt.get(i.strip(), (None, None))
            if sec:
                sectors.append(sec)
            if st:
                statuses.append(st)
        caption = None
        for d in c.find_all("div"):
            t = clean(d.get_text(" ", strip=True))
            if t and not d.find(["div", "h3"]) and t != name:
                caption = t
        exit_to = caption[5:].strip() if caption and caption.startswith("Exit.") else None
        a = c.find("a", href=True)
        href = urljoin(SOURCE_URL, a["href"]) if a else ""
        site = href if href.startswith("http") and "axc.vc" not in href and not is_social(href) else None
        status = "active" if "active" in statuses else ("exited" if exit_to else None)
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       status=status, exit=exit_to,
                       detail_url=href if "axc.vc" in href else None))
    finish(out, "axeleo", ("company_url", "status", "exit", "everywhere_tags"))


if __name__ == "__main__":
    main()
