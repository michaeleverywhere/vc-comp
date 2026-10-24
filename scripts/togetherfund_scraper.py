#!/usr/bin/env python3
"""Together Fund portfolio scraper -> togetherfund_companies.json
Source: https://www.together.fund/portfolio — Together Fund, early-stage AI-focused venture fund (India/US). The
Webflow listing gives each company's name, one-liner, year invested, entry stage ("When we partnered"), sector and an
exited banner; each /portfolio/<slug> detail page adds the company website and founder names."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, clean_url
from _d50_common import rec, finish

SOURCE_URL = "https://www.together.fund/portfolio"
PRIMARY = "Together Fund"


def visible(el):
    return el is not None and "w-condition-invisible" not in (el.get("class") or [])


def detail(html):
    s = BeautifulSoup(html, "html.parser")
    site = None
    for info in s.select(".portfolio_temp_info"):
        t = info.select_one(".portfolio_temp_info-title")
        if t and clean(t.get_text()) == "Website" and visible(info):
            a = info.find("a", href=True)
            site = clean_url(a["href"]) if a else None
    founders = [clean(x.get_text()) for x in s.select(".contact_reach_contact") if clean(x.get_text())]
    return site, founders


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items = []
    for it in soup.select(".portfolio_main_item"):
        name_el = it.select_one(".main-text[fs-cmsfilter-field=name]") or it.select_one("[fs-cmsfilter-field=name]")
        name = clean(name_el.get_text()) if name_el else None
        if not name:
            continue
        desc = clean(it.select_one("p.portfolio_main_copy").get_text()) if it.select_one("p.portfolio_main_copy") else None
        det = {}
        for d in it.select(".portfolio_main_detail_item, .portfolio_main_detail_item2"):
            k, v = d.select_one(".portfolio_main_detail_title"), d.select_one(".portfolio_main_detail")
            if k and v:
                det[clean(k.get_text())] = clean(v.get_text())
        sectors = sorted({clean(x.get_text()) for x in it.select("[fs-cmsfilter-field=sector]") if clean(x.get_text())})
        exited = visible(it.select_one(".portfolio_exited_banner"))
        a = it.find("a", href=lambda h: h and "/portfolio/" in h)
        items.append((name, desc, det, sectors, exited, urljoin(SOURCE_URL, a["href"]) if a else None))
    pages = fetch_many([i[5] for i in items if i[5]])
    out = []
    for name, desc, det, sectors, exited, link in items:
        site, founders = detail(pages[link]) if pages.get(link) else (None, [])
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       status="Exited" if exited else "Active", year_invested=det.get("Year Invested"),
                       stage=det.get("When we partnered"), founders=founders or None, profile_url=link))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Together Fund companies")
    finish(out, "togetherfund", ("description", "company_url", "status", "stage", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
