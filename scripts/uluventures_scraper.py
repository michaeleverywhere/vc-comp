#!/usr/bin/env python3
"""Ulu Ventures portfolio scraper -> uluventures_companies.json
Source: https://uluventures.com/companies/ — Ulu Ventures, Palo Alto seed-stage venture capital firm (early
investor in Palantir, SoFi and Figure) backing diverse founders. The companies grid gives each portfolio
company's logo (name in the image alt text), website link and an "Exited" label where applicable.
Logos whose alt text is all-lowercase (no reliable company-name casing) are skipped rather than guessed."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://uluventures.com/companies/"
PRIMARY = "Ulu Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select("div.masonryPostGridItem"):
        img = it.select_one("img[alt]")
        alt = clean(img.get("alt")) if img else None
        if not alt or not re.search(r"[A-Z]", alt):
            continue
        name = clean(re.sub(r"\s+logo\b.*$", "", alt.replace("_", " "), flags=re.I))
        if not name or len(name) < 2:
            continue
        a = it.select_one("a[href]")
        href = a.get("href").replace("#new_tab", "") if a else None
        if href and "uluventures.com" in href:
            href = None
        txt = it.select_one(".masonryPostGridItemText")
        t = clean(txt.get_text(" ")) if txt else None
        out.append(rec(name, None, href, PRIMARY, SOURCE_URL, scraped_at,
                       status="Exited" if t else "Active", exit_note=t if t and t != "Exited" else None))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Ulu Ventures companies")
    finish(out, "uluventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
