#!/usr/bin/env python3
"""Sandbox Industries portfolio scraper -> sandboxindustries_companies.json
Source: https://www.sandboxindustries.com/portfolio — Sandbox Industries, Chicago venture firm (Blue Venture Fund with
the Blue Cross Blue Shield plans, Clinical Ventures, Insurtech Ventures). The listing gives each company's name,
strategy/fund tag, one-liner and an Exited tag; each /portfolio/<slug> page adds the website and company overview."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, clean_url
from _d50_common import rec, finish

SOURCE_URL = "https://www.sandboxindustries.com/portfolio"
PRIMARY = "Sandbox Industries"
# strategy tag -> sector as the site frames each strategy
SECTOR = {"Blue Venture Fund": "Healthcare", "Clinical Ventures": "Healthcare", "Insurtech Ventures": "Insurtech"}


def detail(html):
    s = BeautifulSoup(html, "html.parser")
    site = None
    for a in s.find_all("a", href=True):
        if "View company website" in a.get_text(" ") and a["href"].startswith("http"):
            site = clean_url(a["href"])
            break
    overview = None
    h = s.find(lambda t: t.name in ("h2", "h3") and clean(t.get_text()) == "Company overview")
    if h:
        p = h.find_next("p")
        overview = clean(p.get_text(" ")) if p else None
    return site, overview


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items = []
    for card in soup.select(".portfolio_grid_item .card_company_wrap"):
        h3 = card.find("h3")
        name = clean(h3.get_text()) if h3 else None
        if not name:
            continue
        tags = [clean(x.get_text()) for x in card.select("[fs-list-field=categories]") if clean(x.get_text())]
        txt = card.select_one(".card_company_text")
        a = card.select_one("a.clickable_link[href]")
        items.append((name, [t for t in tags if t != "Exited"], "Exited" in tags,
                      clean(txt.get_text()) if txt else None, urljoin(SOURCE_URL, a["href"]) if a else None))
    pages = fetch_many([i[4] for i in items if i[4]])
    out = []
    for name, strategies, exited, one_liner, link in items:
        site, overview = detail(pages[link]) if pages.get(link) else (None, None)
        out.append(rec(name, one_liner or overview, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sorted({SECTOR[t] for t in strategies if t in SECTOR}),
                       strategy=", ".join(strategies) or None, status="Exited" if exited else "Active",
                       overview=overview, profile_url=link))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Sandbox Industries companies")
    finish(out, "sandboxindustries", ("description", "company_url", "strategy", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
