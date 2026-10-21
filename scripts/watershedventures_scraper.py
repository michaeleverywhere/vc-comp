#!/usr/bin/env python3
"""Watershed Ventures portfolio scraper -> watershedventures_companies.json
Source: https://portfolio.watershed.vc/companies — Watershed's own portfolio board (Getro-hosted; read via
headless Chrome, pressing the page's own "Load more" button, then scrolling, until all companies are listed): company
name, Watershed's one-line description, industry tags and the stage label where published."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_jsclick import dom_jsclick

SOURCE_URL = "https://portfolio.watershed.vc/companies"
PRIMARY = "Watershed Ventures"
STAGE = re.compile(r"^(Pre-Seed|Seed|Series [A-Z]\+?|Growth|IPO|Acquired)$", re.I)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = dom_jsclick(SOURCE_URL, "[...document.querySelectorAll('button')].find(b => /^\\s*load more\\s*$/i.test(b.innerText))",
                       "document.querySelectorAll('span.company-name-text').length", settle_s=10, step_s=3, scroll=True)
    s = BeautifulSoup(html, "html.parser")
    out = []
    for nm in s.select("span.company-name-text"):
        name = clean(nm.get_text(" ", strip=True))
        card = nm
        while card.parent is not None and len(card.parent.select("span.company-name-text")) == 1:
            card = card.parent
        chips = [clean(x.get_text(" ", strip=True)) for x in card.select("div") if not x.find("div")]
        chips = [c for c in chips if c and c != name and not re.match(r"(?i)^(view \d+ jobs?|view company|\d+ jobs?|\+ \d+ more)$", c)]
        desc = max((c for c in chips if len(c) > 40), key=len, default=None)
        tags = [c for c in chips if c != desc and len(c) <= 40]
        stage = next((c for c in tags if STAGE.match(c)), None)
        sectors = [c for c in tags if c != stage]
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, stage=stage))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Watershed companies")
    finish(out, "watershedventures", ("description", "sectors", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
