#!/usr/bin/env python3
"""K9 Ventures portfolio scraper -> k9ventures_companies.json
Source: https://www.k9ventures.com/startups/ — K9 Ventures, Palo Alto-based pre-seed/seed venture firm (Manu Kumar)
focused on technology startups. Each portfolio modal gives the company name, location, website, "About" description,
exit note (e.g. "Acquired by ..."), founders and the K9 investment year/fund."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.k9ventures.com/startups/"
PRIMARY = "K9 Ventures"


def after_h3(m, label):
    h = m.find("h3", string=lambda s: s and clean(s) == label)
    if not h:
        return None
    p = h.find_next_sibling("p")
    return clean(p.get_text(" ")) if p else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for m in soup.select("div.modal.company-details"):
        h1 = m.find("h1")
        name = clean(h1.get_text(" ")) if h1 else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        h5 = m.find("h5")
        w = m.select_one("li.website a[href]")
        bold = m.select_one("p.bold")
        note = clean(bold.get_text(" ")) if bold else None
        status = "Exited" if note and re.search(r"acquired|ipo|merged|public", note, re.I) else \
            ("Closed" if note and re.search(r"shut|closed|defunct", note, re.I) else "Active")
        inv = after_h3(m, "K9 Investment")
        yr = re.search(r"\b(19|20)\d{2}\b", inv or "")
        founders = after_h3(m, "Founders")
        out.append(rec(name, after_h3(m, "About"), w["href"] if w else None, PRIMARY, SOURCE_URL, scraped_at,
                       location=clean(h5.get_text(" ")) if h5 else None, status=status, exit_note=note,
                       founders=[f.strip() for f in founders.split(",") if f.strip()] if founders else None,
                       k9_investment=inv, year_invested=yr.group(0) if yr else None))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} K9 companies")
    finish(out, "k9ventures", ("description", "website", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
