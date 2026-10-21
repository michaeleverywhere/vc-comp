#!/usr/bin/env python3
"""ArcTern Ventures portfolio scraper -> arcternventures_companies.json
Source: https://www.arcternventures.com/portfolio/ — Toronto climate-tech venture firm; server-rendered WordPress
portfolio grid: one card per company (company name from the card's "View portfolio <name>" label, the
one-line tagline and the site's "Exited" marker); each /portfolio/<slug>/ page adds the description and the
"Company Website" link."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.arcternventures.com/portfolio/"
PRIMARY = "ArcTern Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = {}
    for a in s.select("a.item[href]"):
        lab = clean(a.get("aria-label")) or ""
        m = re.match(r"View portfolio (.+)$", lab)
        if not m or "/portfolio/" not in a["href"]:
            continue
        ps = [clean(p.get_text(" ", strip=True)) for p in a.select(".text p")]
        cards.setdefault(a["href"], dict(name=clean(m.group(1)), tagline=next((p for p in ps if p and p != "Exited"), None),
                                         exited=bool(a.select_one("p.exited"))))
    pages = fetch_many(list(cards), workers=3, pause=0.3)
    out = []
    for u, c in cards.items():
        desc = web = None
        h = pages.get(u)
        if h:
            d = BeautifulSoup(h, "html.parser")
            for t in d(["script", "style", "nav", "footer", "header"]):
                t.decompose()
            ps = [clean(p.get_text(" ", strip=True)) for p in d.find_all("p")]
            ps = [p for p in ps if p and p != c["tagline"] and len(p) > 40]
            desc = ps[0] if ps else None
            for a in d.find_all("a", href=True):
                if clean(a.get_text(" ", strip=True)) == "Company Website" and not is_social(a["href"]):
                    web = a["href"]
                    break
        out.append(rec(c["name"], desc or c["tagline"], web, PRIMARY, SOURCE_URL, scraped_at, tagline=c["tagline"],
                       profile_url=u, status="exited" if c["exited"] else "active"))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} ArcTern companies")
    finish(out, "arcternventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
