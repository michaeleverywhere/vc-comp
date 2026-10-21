#!/usr/bin/env python3
"""VoLo Earth Ventures portfolio scraper -> voloearthventures_companies.json
Source: https://www.voloearth.com/portfolio — climate-tech venture firm; server-rendered Webflow portfolio grid
whose per-company lightbox carries the company name, year founded, website link and Volo's description
paragraphs (plus the card's category label when filled)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, webflow_pages
from _d50_common import rec, finish

SOURCE_URL = "https://www.voloearth.com/portfolio"
PRIMARY = "VoLo Earth Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        s = BeautifulSoup(html, "html.parser")
        for it in s.select("div.portfolio-item.w-dyn-item"):
            w = it.select_one(".portfolio-image-wrapper")
            if not w:
                continue
            h = w.select_one("h1.heading-3")
            name = clean(h.get_text(" ", strip=True)) if h else None
            if not name or name.lower() == "stealth":  # unnamed stealth placeholder
                continue
            year = web = None
            for sub in w.select("h1.subheader"):
                lab = clean(sub.get_text(" ", strip=True))
                if lab == "YEAR FOUNDED":
                    v = sub.find_next_sibling("h1")
                    year = clean(v.get_text(" ", strip=True)) if v else None
                elif lab == "WEBSITE":
                    a = sub.find_next_sibling("a", href=True)
                    web = a["href"] if a else None
            desc = " ".join(x for x in (clean(p.get_text(" ", strip=True)) for p in w.select("p.paragraph")) if x) or None
            cats = [clean(c.get_text(" ", strip=True)) for c in it.select("h1.catgeory-heading")
                    if "w-dyn-bind-empty" not in (c.get("class") or [])]
            cats = [c for c in cats if c and c != "Industry"]
            out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, year_founded=year))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Volo companies")
    finish(out, "voloearthventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
