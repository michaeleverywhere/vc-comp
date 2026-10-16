#!/usr/bin/env python3
"""Samsung Catalyst Fund portfolio scraper -> samsungcatalyst_companies.json
Source: https://samsungcatalyst.com/ — portfolio grid: <a class="portfolio-company"
data-name> with website link, description on the card back and sector category slug.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://samsungcatalyst.com/"
PRIMARY = "Samsung Catalyst Fund"
SECTOR_MAP = {"healthcare": ["Health"], "digital health": ["Health"], "mobility": ["Transportation / Mobility"],
              "security": ["Cybersecurity"], "climate": ["Climate / Sustainability"], "robotics": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    out = []
    for a in soup.select("a.portfolio-company"):
        name = clean(a.get("data-name")) or (clean(a.select_one(".name").get_text()) if a.select_one(".name") else None)
        d = a.select_one(".company__content")
        cat = a.select_one(".category")
        cats = [c.strip() for c in (clean(cat.get_text()) or "").split(",") if c.strip()] if cat else []
        if "lp-fund-investments" in cats:
            continue  # fund-of-funds LP commitments, not portfolio companies
        secs = [c.replace("-", " ").title().replace("Ai ", "AI ") for c in cats]
        href = a.get("href") or ""
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, href if href.startswith("http") else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP))
    finish(out, "samsungcatalyst", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
