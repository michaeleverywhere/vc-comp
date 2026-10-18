#!/usr/bin/env python3
"""Overlook Ventures portfolio scraper -> overlook_companies.json
Source: https://www.overlook.vc/portfolio — client-rendered (React) grid read from the
rendered DOM via headless Chrome (_chrome_dom.py). Each card links to the company
website and gives name, one-line description, stage (round Overlook invested in),
year (first invested) and city/country code. The site notes some investments
predate Overlook (partners' prior investments); they are not distinguished per card."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.overlook.vc/portfolio"
PRIMARY = "Overlook Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=50000), "html.parser")
    out, seen = [], set()
    for a in s.select("a[href]"):
        h3, p = a.find("h3"), a.find("p")
        if not h3 or not p:
            continue
        name = clean(h3.get_text(" ", strip=True))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        meta = [clean(x.get_text(" ", strip=True)) for x in a.select("div > span")]
        meta = [m for m in meta if m and m != "·"]
        yr = next((int(m) for m in meta if re.fullmatch(r"(19|20)\d\d", m)), None)
        stage = meta[0] if meta and not re.fullmatch(r"\d{4}", meta[0]) else None
        loc = meta[-1] if len(meta) >= 3 else None
        href = a["href"].strip()
        out.append(rec(name, clean(p.get_text(" ", strip=True)), href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, stage=stage, first_invested=yr, location=loc))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Overlook companies")
    finish(out, "overlook", ("description", "company_url", "stage", "first_invested", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
