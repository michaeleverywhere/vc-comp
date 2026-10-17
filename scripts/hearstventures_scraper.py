#!/usr/bin/env python3
"""Hearst Ventures portfolio scraper -> hearstventures_companies.json
Source: https://www.hearst.com/ventures — Liferay brand-card grid under "Current
Investments": company name (card data-Title, logo alt as fallback), website (card link), and a
"City — description" cutline split into location + description. The "Key Prior
Investments" section is a single logo-collage image (no text), so it is not scraped."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.hearst.com/ventures"
PRIMARY = "Hearst Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8", "replace")
    cut = html.find("Key Prior Investments")
    if cut > 0:
        html = html[:cut]
    s = BeautifulSoup(html, "html.parser")
    out = []
    for card in s.select("div.three-col-brand-div"):
        title = clean(re.sub(r":?\s*Brand (?:Block|Card)\s*$", "", card.get("data-title") or card.get("data-Title") or "", flags=re.I))
        logo = card.select_one(".white-logo img") or card.select_one(".black-logo img")
        name = title or (clean(logo.get("alt")) if logo else None)
        if not name:
            continue
        a = card.select_one("a.brand-card-link")
        href = (a.get("href") or "").strip() if a else ""
        url = href if href.startswith("http") and "hearst.com" not in href and not is_social(href) else None
        p = card.select_one(".subCutlineDiv")
        cut_txt = clean(p.get_text(" ", strip=True)) if p else None
        loc, desc = None, cut_txt
        if cut_txt:
            m = re.match(r"^([A-Z][\w .'’\-]{1,40}?)\s+[—–]\s+(.*)$", cut_txt)
            if m:
                loc, desc = clean(m.group(1)), clean(m.group(2))
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at, location=loc, status="active"))
    finish(out, "hearstventures", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
