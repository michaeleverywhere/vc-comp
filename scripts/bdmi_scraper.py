#!/usr/bin/env python3
"""BDMI (Bertelsmann Digital Media Investments) portfolio scraper -> bdmi_companies.json
Source: https://bdmifund.com/portfolio — Squarespace list sections: featured and
current portfolio (name, tagline linked to the website, sector) and the exits list
(name, tagline, exit type M&A/IPO). Logo-only co-investor and testimonial lists skipped.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://bdmifund.com/portfolio"
PRIMARY = "BDMI"
EXIT_TYPES = {"M&A", "IPO", "SPAC"}
SECTORS = {"Fintech", "Next Gen Media", "Web3", "Enterprise Saas", "Enterprise SaaS"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "next gen media": ["Gaming / Media / Entertainment"], "web3": ["Web3 / Crypto"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for ul in soup.select("ul[class*=user-items-list]"):
        items = ul.find_all("li", recursive=False)
        rows = []
        for li in items:
            t = li.select_one(".list-item-content__title")
            name = clean(t.get_text(" ", strip=True)) if t else None
            if not name or name.startswith("“"):
                continue
            d = li.select_one(".list-item-content__description")
            st = [clean(x) for x in (d.stripped_strings if d else []) if clean(x)]
            a = d.find("a", href=True) if d else None
            rows.append((name, st, a["href"] if a and a["href"].startswith("http") else None))
        is_exit = any(s in EXIT_TYPES for _, st, _ in rows for s in st)
        for name, st, url in rows:
            tag = [s for s in st if s not in EXIT_TYPES and s not in SECTORS]
            sec = [s for s in st if s in SECTORS]
            ext = [s for s in st if s in EXIT_TYPES]
            out.append(rec(name, tag[0] if tag else None, url, PRIMARY, SOURCE_URL, scraped_at, sectors=sec, sector_map=SECTOR_MAP,
                           status="exited" if is_exit else "active", exit_type=ext[0] if ext else None))
    # featured list precedes the full current list, so the first occurrence keeps the same status
    finish(out, "bdmi", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
