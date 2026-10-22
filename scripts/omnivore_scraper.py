#!/usr/bin/env python3
"""Omnivore portfolio scraper -> omnivore_companies.json
Source: https://omnivore.vc/portfolio — Mumbai-based agritech / climate / rural-fintech venture firm; client-rendered
Next.js portfolio grid (read via headless Chrome): company name, the firm's one-line description, website
("Visit site") and the EXITED badge (+ "Exited to:" acquirer when shown) on each card."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://omnivore.vc/portfolio"
PRIMARY = "Omnivore"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=50000), "html.parser")
    out = []
    for p in s.select("p.text-textColor2"):
        cls = p.get("class") or []
        if "md:text-2xl" not in cls:
            continue
        name = clean(p.get_text(" ", strip=True))
        card = p
        for _ in range(4):  # name row -> text block -> overlay -> card
            card = card.parent
        if not name or card is None:
            continue
        ps = [clean(x.get_text(" ", strip=True)) for x in card.select("p.text-textColor2") if x is not p]
        desc = next((x for x in ps if x), None)
        a = next((a for a in card.select("a[href^=http]") if "visit site" in a.get_text(" ", strip=True).lower()), None)
        strs = [clean(x) for x in card.stripped_strings]
        exited = "EXITED" in strs
        acq = None
        if "Exited to:" in strs:
            i = strs.index("Exited to:")
            acq = strs[i + 1] if i + 1 < len(strs) and strs[i + 1] not in ("Visit site", name) else None
        out.append(rec(name, desc, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       acquirer=acq, status="exited" if exited else "active"))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Omnivore companies")
    finish(out, "omnivore", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
