#!/usr/bin/env python3
"""Mischief portfolio scraper -> mischief_companies.json
Source: https://mischief.vc/ — investment cards on the home page (JS-rendered, read via
headless Chrome): company name (card data-name / logo alt), Mischief sector tags,
one-line description and website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://mischief.vc/"
PRIMARY = "Mischief"
SECTOR_MAP = {"ai": [], "infra": ["Dev Tools / Cloud"], "health": ["Health"], "consumer": ["Consumer"],
              "security": ["Cybersecurity"], "fintech": ["FinTech / Insurance"], "crypto": ["Web3 / Crypto"],
              "gtm": [], "physical": ["Deeptech / Robotics / AR/VR"], "privacy": ["Cybersecurity"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=10000), "html.parser")
    out = []
    for a in s.select("a.inv-card"):
        img = a.select_one("img.inv-logo-big[alt]")
        name = clean(a.get("data-name") or (img.get("alt") if img else None))
        if not name:
            continue
        tags = [clean(t.get_text(" ", strip=True)) for t in a.select(".inv-tag")]
        desc = a.select_one(".inv-card-desc")
        href = a.get("href") or ""
        out.append(rec(name, clean(desc.get_text(" ", strip=True)) if desc else None,
                       href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[t for t in tags if t], sector_map=SECTOR_MAP))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Mischief companies")
    finish(out, "mischief", ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
