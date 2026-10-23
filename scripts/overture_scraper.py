#!/usr/bin/env python3
"""Overture portfolio scraper -> overture_companies.json
Source: https://www.overture.vc/portfolio — Overture, climate and industrial-transformation venture capital firm;
the rendered portfolio grid gives each company's name, Overture's one-line description, its category (Energy /
Industrial Transformation / Resilience) and the company website from the card's link."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, clean_url
from _chrome_dom import dom
from _d50_common import rec, finish

SOURCE_URL = "https://www.overture.vc/portfolio"
PRIMARY = "Overture"
CATS = {"ENERGY": "Energy", "INDUSTRIAL": "Industrial Transformation", "RESILIENCE": "Resilience"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(dom(SOURCE_URL, 15000, tries=3, min_len=100000), "html.parser")
    out = []
    for co in soup.select("div.co"):
        n = co.select_one("div.co-name")
        if n:
            for s in n.select("span.arrow"):
                s.decompose()
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name or name.lower() == "stealth":  # unnamed stealth placeholder card: not a company record
            continue
        d = co.select_one("div.co-desc")
        cats = clean(co.select_one("div.co-cats").get_text(" ", strip=True)) if co.select_one("div.co-cats") else None
        sectors = [CATS.get(c.strip().upper(), c.strip().title()) for c in re.split(r"[,/|]", cats or "") if c.strip()]
        m = re.search(r"window\.open\('([^']+)'", co.get("onclick") or "")
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, clean_url(m.group(1)) if m else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=sectors))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Overture companies")
    finish(out, "overture", ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
