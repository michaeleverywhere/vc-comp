#!/usr/bin/env python3
"""Next47 (Siemens-backed venture firm) portfolio scraper -> next47_companies.json
Source: https://www.n47.com/portfolio — Webflow grid cards (name, exit note, year
founded, year + round partnered, sector, location) plus each company page for
founders ("builders"), Next47 lead, website and description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, year_of, label_after, is_social
from _d50_common import rec, finish, page_strings

ORIGIN = "https://www.n47.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Next47"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a.pf-grid-item"):
            if a.find("h2") and a.get("href", "").startswith("/"):
                cards.append(a)
    pages = fetch_many([ORIGIN + a["href"] for a in cards], workers=6, pause=0.1)
    out = []
    for a in cards:
        url = ORIGIN + a["href"]
        st = [clean(t) for t in a.stripped_strings if clean(t)]
        dst, dsoup = page_strings(pages.get(url) or "")
        b = a.select_one(".pf-grid-item__investment")
        note = clean(b.get_text(" ", strip=True)) if b else None
        exit_note = note if note and (note.startswith("IPO") or note.lower().startswith("acquired")) else None
        partnered = label_after(st, "partnered") or label_after(dst, "partnered")
        rnd = partnered.split(",", 1)[1].strip() if partnered and "," in partnered else None
        sector = a.get("data-filter-sector") or label_after(st, "sector")
        site = next((x["href"] for x in dsoup.select("a[href^=http]") if "n47.com" not in x["href"] and not is_social(x["href"])), None)
        desc = None
        if "Website" in dst:
            rest = dst[dst.index("Website") + 1:]
            desc = rest[0] if rest and len(rest[0]) > 30 else None
        if not desc and st and len(st[-1]) > 40:
            desc = st[-1]
        status = None
        if exit_note:
            status = "ipo" if exit_note.startswith("IPO") else "acquired"
        out.append(rec(a.find("h2").get_text(" ", strip=True), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sector] if sector else None,
                       founders=label_after(dst, "builders"), lead_partner=label_after(dst, "lead"),
                       founded_year=year_of(label_after(st, "founded")),
                       first_invested_year=year_of(partnered), entry_round=rnd,
                       location=a.get("data-filter-location") or None,
                       exit_note=exit_note, status=status or "active", detail_url=url))
    finish(out, "next47", ("description", "company_url", "first_invested_year", "lead_partner", "everywhere_tags"))


if __name__ == "__main__":
    main()
