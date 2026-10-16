#!/usr/bin/env python3
"""Owl Ventures portfolio scraper -> owl_companies.json
Source: https://www.owlvc.com/portfolio — Webflow cards with pop-ups: name,
description, website, acquired / acquired-by, sub-category (segment) and region,
year founded, headquarters, founder/CEO/co-founders, notable co-investors.
Hidden Webflow fields (w-condition-invisible) are ignored.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, year_of, is_social
from _d50_common import rec, finish

ORIGIN = "https://www.owlvc.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Owl Ventures"
REGIONS = {"North America", "Europe", "Asia", "Latin America", "Africa", "Middle East", "India", "Global", "Australia", "South America"}
SECTOR_MAP = {"pre k-12": ["Future of Work"], "post-secondary": ["Future of Work"], "future of work": ["Future of Work"]}


def visible(el):
    while el is not None and getattr(el, "get", None):
        if "w-condition-invisible" in (el.get("class") or []):
            return False
        el = el.parent
    return True


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for c in soup.select(".portfolio-card"):
            n = c.select_one(".portfolio-name") or c.select_one(".text-block-10")
            if not n:
                continue
            facts = {}
            for h in c.select(".pop-up-right-content-holder"):
                t, v = h.select_one(".invaestment-title"), h.find("p")
                if visible(h) and t and v and clean(v.get_text()):
                    facts[clean(t.get_text())] = clean(v.get_text(" ", strip=True))
            p = c.select_one(".pop-up-left p") or c.select_one(".porfolio-card-para")
            acq_by = None
            for x in c.select(".pop-up-acquired"):
                if visible(x) and "By" in x.get_text():
                    b = x.find_next_sibling(class_="text-block-7")
                    acq_by = clean(b.get_text()) if b else None
            acquired = any(visible(x) for x in c.select(".acquired-text"))
            site = next((a["href"] for a in c.select(".pop-up-buttons-wrapper a[href^=http]")
                         if "Visit Website" in a.get_text() and not is_social(a["href"])), None)
            subs = [clean(x.get_text()) for x in c.select(".sub-category") if clean(x.get_text())]
            region = [s for s in subs if s in REGIONS]
            founders = ", ".join(v for k, v in facts.items() if k in ("Founder", "Co-Founders")) or None
            out.append(rec(n.get_text(" ", strip=True), clean(p.get_text(" ", strip=True)) if p else None, site,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=[s for s in subs if s not in REGIONS], sector_map=SECTOR_MAP,
                           region=", ".join(region) or None, status="acquired" if (acquired or acq_by) else "active",
                           acquired_by=acq_by, founded_year=year_of(facts.get("Year Founded")),
                           first_invested_year=year_of(facts.get("Initial Investment")),
                           location=facts.get("Headquarters"), founders=founders, ceo=facts.get("CEO"),
                           co_investors=facts.get("Notable Co-investors")))
    finish(out, "owl", ("description", "company_url", "status", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
