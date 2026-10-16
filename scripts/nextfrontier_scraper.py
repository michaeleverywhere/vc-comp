#!/usr/bin/env python3
"""Next Frontier Capital portfolio scraper -> nextfrontier_companies.json
Source: https://nextfrontiercapital.com/portfolio — Framer static page; each
company card shows name, sector, fund ("Fund IV") and "Invested in <year>",
linking to the company website; exited companies carry an "Exited" badge. Cards are located from their "Invested in"
heading; Framer breakpoint duplicates are removed by name.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://nextfrontiercapital.com/portfolio"
PRIMARY = "Next Frontier Capital"
SECTOR_MAP = {"national security": ["Deeptech / Robotics / AR/VR"]}


def card_of(h):
    node = h
    while node.parent is not None:
        par = node.parent
        if len([x for x in par.find_all("h2") if clean(x.get_text()).startswith("Invested in")]) > 1:
            return node
        node = par
    return node


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for h in soup.find_all("h2"):
        if not (clean(h.get_text()) or "").startswith("Invested in"):
            continue
        card = card_of(h)
        strs = [clean(s) for s in card.stripped_strings if clean(s)]
        if len(strs) < 3:
            continue
        badge = None
        if strs[0] in ("Exited", "Acquired", "IPO"):
            badge = strs.pop(0)
        name = strs[0]
        fund = next((s for s in strs if re.fullmatch(r"Fund [IVX]+", s)), None)
        mid = [s for s in strs[1:] if s != fund and not s.startswith("Invested in")]
        a = card.find("a", href=True) if card.name != "a" else card
        href = a["href"] if a else ""
        out.append(rec(name, None, href if href.startswith("http") and not is_social(href) else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=mid[:2], sector_map=SECTOR_MAP, fund=fund,
                       first_invested_year=year_of(clean(h.get_text())),
                       status="exited" if badge else None))
    finish(out, "nextfrontier", ("company_url", "fund", "first_invested_year", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
