#!/usr/bin/env python3
"""OnePrime Capital portfolio scraper -> oneprimecapital_companies.json
Source: https://oneprimecapital.com/ipos-ma — OnePrime's published "IPOs and M&A" milestones list (the
firm states its full public listing is its exits): one card per company — company name (site-authored
logo alt text), exit type (IPO / Acquired / SPAC), ticker where shown and the exit month."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://oneprimecapital.com/ipos-ma"
PRIMARY = "OnePrime Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for item in s.select("div.project-card-left"):
        img = item.select_one("img.investment-img")
        name = clean(img.get("alt")) if img else None
        if not name:
            continue
        labels = [clean(x.get_text(" ", strip=True)) for x in item.select("div.text-401")]
        labels = [x for x in labels if x]
        tick = item.select_one("div.ticker")
        etype = labels[0] if labels else None
        edate = labels[1] if len(labels) > 1 else None
        out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at, exit_type=etype,
                       ticker=clean(tick.get_text(" ", strip=True)) if tick else None, exit_date=edate,
                       status="acquired" if etype and "acquired" in etype.lower() else ("ipo" if etype else None)))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} OnePrime companies")
    finish(out, "oneprimecapital", ("exit_type", "ticker", "exit_date", "everywhere_tags"))


if __name__ == "__main__":
    main()
