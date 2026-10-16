#!/usr/bin/env python3
"""BlueYard Capital portfolio scraper -> blueyard_companies.json
Source: https://blueyard.com/ — Nuxt-rendered portfolio card grid: company name
(card header), BlueYard's one-line note on the company and "Visit site" link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://blueyard.com/"
PRIMARY = "BlueYard Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for card in soup.select("div.card"):
        top = card.select_one(".card__buffer-top")
        name = clean(top.get_text(" ", strip=True)) if top else None
        if not name:
            img = card.select_one("img[alt$=' logo']")
            name = img["alt"][:-5] if img else None
        if not name:
            continue
        t = card.select_one(".card__tile-text")
        a = card.select_one(".card__tile-button a[href^=http]")
        out.append(rec(name, clean(t.get_text(" ", strip=True)) if t else None, a["href"] if a else None,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "blueyard", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
