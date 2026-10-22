#!/usr/bin/env python3
"""Blue Horizon portfolio scraper -> bluehorizon_companies.json
Source: https://bluehorizon.com/ecosystem/ — Zurich-based future-of-food / sustainable-protein venture investor;
WordPress "ecosystem" page with one flip card per portfolio company: name (card title), the firm's one-line
description, "Invested at:" stage (Seed / Venture / Growth / Roll-Up) or "Exited:" stage, and the company website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://bluehorizon.com/ecosystem/"
PRIMARY = "Blue Horizon"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for card in soup.select("div.flip-card-back"):
        t = card.select_one(".title")
        name = clean(t.get_text(" ", strip=True)) if t else None
        if not name:
            continue
        b = card.select_one("p.body-text")
        desc = clean(b.get_text(" ", strip=True)) if b else None
        inv = card.select_one("p.invested")
        inv = clean(inv.get_text(" ", strip=True)) if inv else None
        exited = bool(inv and inv.lower().startswith("exited"))
        stage_raw = clean(re.sub(r"(?i)^(invested at|exited)\s*:\s*", "", inv)) if inv else None
        a = card.select_one("a.url[href]")
        out.append(rec(name, desc, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       invested_at=stage_raw, stage=stage_label(stage_raw) if stage_raw else None,
                       status="exited" if exited else "active"))
    if len(out) < 50:
        raise SystemExit(f"FATAL: only {len(out)} Blue Horizon companies")
    finish(out, "bluehorizon", ("description", "company_url", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
