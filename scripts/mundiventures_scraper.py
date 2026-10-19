#!/usr/bin/env python3
"""Mundi Ventures portfolio scraper -> mundiventures_companies.json
Source: https://mundiventures.com/portfolio/ — the "Full portfolio" table (Framer; rows
beyond the first page appear only after the page's own "Load more" button, so it is read
via headless Chrome with load-more clicking, scripts/_chrome_click.py): company name,
purpose (one-line description), location (city), Mundi category (Insur Tech / Deep Tech /
Impact Tech / Climate Tech / Fin Tech), Mundi stage bucket (Early / Growth Stage) and
website ("Visit" link)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_click import dom_loadmore

SOURCE_URL = "https://mundiventures.com/portfolio/"
PRIMARY = "Mundi Ventures"
SECTOR_MAP = {"insur tech": ["FinTech / Insurance"], "fin tech": ["FinTech / Insurance"], "deep tech": ["Deeptech / Robotics / AR/VR"],
              "climate tech": ["Climate / Sustainability"], "impact tech": [], "others": []}


def cell(k):
    return clean(" ".join(p.get_text(" ", strip=True) for p in k.find_all(["h4", "p"])))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = dom_loadmore(SOURCE_URL, count_js="document.querySelectorAll('h4').length")
    s = BeautifulSoup(html, "html.parser")
    out = []
    for h in s.find_all("h4"):
        row = h.parent.parent.parent if h.parent and h.parent.parent else None
        kids = row.find_all(recursive=False) if row else []
        if len(kids) < 7 or kids[0].find("h4") is not h:
            continue
        name = clean(h.get_text(" ", strip=True))
        a = row.find("a", href=re.compile(r"^https?://"))
        href = a["href"] if a and not is_social(a["href"]) else None
        purpose, loc, cat = cell(kids[1]), cell(kids[2]), cell(kids[3])
        bucket = next((cell(k) for k in kids if re.fullmatch(r"(Early|Growth) Stage", cell(k) or "")), None)
        out.append(rec(name, purpose, href, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], sector_map=SECTOR_MAP,
                       location=loc, stage_focus=bucket))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Mundi companies (load-more may have failed)")
    finish(out, "mundiventures", ("description", "company_url", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
