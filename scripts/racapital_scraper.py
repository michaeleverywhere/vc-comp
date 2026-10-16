#!/usr/bin/env python3
"""RA Capital Management portfolio scraper -> racapital_companies.json
Source: https://www.racap.com/portfolio — listing links to /portfolio/<slug>
detail pages, each with description, Domain, Status, Stage of Initial
Investment, Initial Investment Year and Website.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, year_of, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://www.racap.com/portfolio"
PRIMARY = "RA Capital Management"
SECTOR_MAP = {"healthcare": ["Health", "BioTech"], "planetary health": ["Climate / Sustainability"]}
LABELS = ("Domain", "Vertical", "Status", "Stage of Initial Investment", "Initial Investment Year", "Website", "LinkedIn", "Twitter")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    names = {}
    for a in soup.select("article[v-show] a[href*='/portfolio/']"):
        h3 = a.select_one("h3")
        nd = h3.find("div") if h3 else None
        names[a["href"]] = clean((nd or h3).get_text(" ", strip=True)) if h3 else None
    urls = sorted(names)
    pages = fetch_many(urls, workers=6, pause=0.1)
    missing = [u for u, h in pages.items() if not h]
    if missing:
        pages.update(fetch_many(missing, workers=2, pause=0.5))
    out = []
    for u, html in pages.items():
        if not html:
            continue
        ds = BeautifulSoup(html, "html.parser")
        main_el = ds.find("main") or ds
        h1 = main_el.find("h1")
        divs = h1.find_all("div", recursive=False) if h1 else []
        name = names.get(u) or (clean(divs[0].get_text("", strip=True)) if divs else None)
        note = clean(divs[1].get_text(" ", strip=True)) if len(divs) > 1 else None
        dl = {}
        for dt in main_el.select("dt"):
            dd = dt.find_next_sibling("dd")
            if dd:
                dl[clean(dt.get_text(" ", strip=True)).lower()] = clean(dd.get_text(" ", strip=True))
        desc = None
        if h1:
            for t in h1.find_all_next(string=True):
                t = clean(t)
                if not t or t in ("Domain", "Status", "Website"):
                    if t in ("Domain", "Status", "Website"):
                        break
                    continue
                if len(t) > 40 and t != note and not t.startswith("Acquired by"):
                    desc = t
                    break
        site = None
        for a in main_el.select("a[href^=http]"):
            if clean(a.get_text(" ", strip=True)) == "Website":
                site = a["href"]
                break
        status = dl.get("status")
        st = (status or "").lower()
        exit_link = None
        if site and ("acquired" in st or "ipo" in st) and len(urlparse(site).path.strip("/")) > 0:
            exit_link, site = site, None
        stage = dl.get("stage of initial investment")
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in (dl.get("domain"), dl.get("vertical")) if x], sector_map=SECTOR_MAP,
                       status_detail=status, exit_note=note, acquirer=dl.get("acquired by"),
                       ipo_year=year_of(dl.get("ipo date")), exit_link=exit_link,
                       status="active" if "current" in st else ("acquired/ipo" if ("ipo" in st or "acquired" in st) else None),
                       initial_investment_stage=stage, stage=stage_label(stage),
                       first_invested_year=year_of(dl.get("initial investment year"))))
    finish(out, "racapital", ("description", "company_url", "acquirer", "stage", "first_invested_year", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
