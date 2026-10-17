#!/usr/bin/env python3
"""Echo Health Ventures portfolio scraper -> echohealth_companies.json
Source: https://www.echohealthventures.com/companies/ — WordPress. The full company list
(name + description) comes from the site's own REST endpoint
/wp-json/wp/v2/companies; the HTML page splits cards into "Current" (with website links)
and "Alumni" (logo-only) sections, which gives website + status (current -> active,
otherwise alumni)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social, html_text
from _d50_common import rec, finish, wp_all

ORIGIN = "https://www.echohealthventures.com"
SOURCE_URL = ORIGIN + "/companies/"
PRIMARY = "Echo Health Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    current = {}
    for card in s.select("div.company-cards--current div.company-card"):
        t = card.select_one(".company-card__title")
        a = card.select_one("a.company-card__link")
        if t:
            href = (a.get("href") or "").strip() if a else ""
            current[clean(t.get_text(" ", strip=True)).lower()] = href if href.startswith("http") and not is_social(href) else None
    out = []
    for p in wp_all(ORIGIN, "companies"):
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        cur = name.lower() in current
        out.append(rec(name, html_text(p.get("content", {}).get("rendered") or p.get("excerpt", {}).get("rendered")),
                       current.get(name.lower()), PRIMARY, SOURCE_URL, scraped_at, sectors=["Healthcare"],
                       portfolio_section="Current" if cur else "Alumni", status="active" if cur else "alumni",
                       detail_url=p.get("link")))
    finish(out, "echohealth", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
