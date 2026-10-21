#!/usr/bin/env python3
"""Par Equity portfolio scraper -> parequity_companies.json
Source: https://www.parequity.com/portfolio — portfolio grid with one overlay per company (read via
headless Chrome): company name, Par Equity's location and sector labels, and the overlay's company
description."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.parequity.com/portfolio"
PRIMARY = "Par Equity"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=100000), "html.parser")
    out = []
    for h in s.select("h1.display-4.text-dgreen"):
        name = clean(h.get_text(" ", strip=True))
        box = h.parent
        if not name or box is None:
            continue
        loc = sec = None
        for chip in box.select("div.d-inline-flex"):
            icon = chip.select_one("span.material-icons")
            val = chip.select_one("span.fw-bold")
            if not icon or not val:
                continue
            kind = clean(icon.get_text())
            if kind == "fmd_good":
                loc = clean(val.get_text(" ", strip=True))
            elif kind == "business":
                sec = clean(val.get_text(" ", strip=True))
        d = box.select_one(".pv-portfolio-overlay__content--data__desc .lead") or box.select_one(".lead")
        desc = clean(d.get_text(" ", strip=True)) if d else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [], location=loc))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Par Equity companies")
    finish(out, "parequity", ("description", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
