#!/usr/bin/env python3
"""BC Partners portfolio scraper -> bcpartners_companies.json
Sources (WP REST on https://www.bcpartners.com):
- `portfolio` post type (current portfolio page): name, investment_status /
  sector / strategy / region term slugs from class_list; description from the
  company detail page (lead heading + paragraphs before "Team involved").
- `investment` post type (full investment history list): name + sector /
  region slugs; added when not already on the portfolio page (no status given).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, clean, fetch_many
from _d50_common import rec, finish, wp_all

ORIGIN = "https://www.bcpartners.com"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "BC Partners"
PRETTY = {"tmt": "TMT", "services-industrials": "Services & Industrials",
          "partially-realised-publicly-traded": "Partially Realised (Publicly Traded)"}
SECTOR_MAP = {"healthcare": ["Health"]}
STATUS = {"unrealised": "active", "realised": "realized", "partially-realised-publicly-traded": "active"}


def pretty(slug):
    return PRETTY.get(slug) or " ".join(w.capitalize() for w in slug.split("-"))


def terms(p, pre):
    return [c[len(pre):] for c in p.get("class_list") or [] if c.startswith(pre)]


def detail_desc(html):
    main = BeautifulSoup(html or "", "html.parser").find("main")
    if not main:
        return None
    h1 = main.find("h1")
    parts = []
    for el in (h1.find_all_next(["h2", "p"]) if h1 else []):
        t = clean(el.get_text(" ", strip=True))
        if el.name == "h2" and t and t.lower().startswith("team"):
            break
        if t:
            parts.append(t)
    return " ".join(parts) or None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pf = wp_all(ORIGIN, "portfolio")
    pages = fetch_many([p["link"] for p in pf])
    out = []
    for p in pf:
        st = (terms(p, "investment_status-") or [None])[0]
        out.append(rec(html_text(p["title"]["rendered"]), detail_desc(pages.get(p["link"])), None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[pretty(s) for s in terms(p, "sector-")], sector_map=SECTOR_MAP,
                       region=", ".join(pretty(s) for s in terms(p, "region-")) or None,
                       strategy=", ".join(pretty(s) for s in terms(p, "strategy-")) or None,
                       portfolio_status=pretty(st) if st else None, status=STATUS.get(st), detail_url=p.get("link")))
    for p in wp_all(ORIGIN, "investment"):
        out.append(rec(html_text(p["title"]["rendered"]), None, None, PRIMARY, ORIGIN + "/investment/", scraped_at,
                       sectors=[pretty(s) for s in terms(p, "sector-")], sector_map=SECTOR_MAP,
                       region=", ".join(pretty(s) for s in terms(p, "region-")) or None))
    finish(out, "bcpartners", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
