#!/usr/bin/env python3
"""LifeX Ventures portfolio scraper -> lifex_companies.json
Source: https://lifex.vc/founders — Webflow CMS (paginated) founder cards.
The company name is only published as the logo image alt text; a few alts
carry a LifeX partner's first name after the company ("Flywire Inaki",
"Jackpocket Amol"), which is stripped. The card back gives a one-line
description and website; the small tag gives exit notes ("acquired by X").
Cards marked current-portfolio-cards vs not are kept as listed.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://lifex.vc/founders"
PRIMARY = "LifeX Ventures"
PARTNER_SUFFIX = re.compile(r"\s+(Inaki|Iñaki|Amol)$")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    pages = list(pages.values()) if isinstance(pages, dict) else pages
    out = []
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for e in soup.select(".w-condition-invisible"):
            e.decompose()
        for it in soup.select(".founders-gird-item"):
            img = it.select_one(".founders-grid-card-image img")
            name = clean(PARTNER_SUFFIX.sub("", (img.get("alt") or "").strip())) if img else None
            if not name:
                continue
            tag = it.select_one(".small-text-founders-cards .body-xs")
            tag = clean(tag.get_text(" ", strip=True)) if tag and "w-dyn-bind-empty" not in (tag.get("class") or []) else None
            d = it.select_one(".founders-grid-card-back-paragraph")
            a = it.select_one("a.founders-grid-card-back[href]")
            href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
            low = (tag or "").lower()
            out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, href, PRIMARY, SOURCE_URL, scraped_at,
                           exit_note=tag, status="acquired" if low.startswith("acq") or "acquired" in low else ("public" if "ipo" in low or "nasdaq" in low or "nyse" in low else None),
                           current_portfolio="current-portfolio-cards" in (it.get("class") or [])))
    finish(out, "lifex", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
