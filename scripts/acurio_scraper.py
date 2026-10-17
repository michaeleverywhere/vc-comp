#!/usr/bin/env python3
"""Acurio Ventures portfolio scraper -> acurio_companies.json
Source: https://www.acurio.vc/portfolio — Webflow portfolio items with filter fields
(name, status, business model, sector, HQ) and pop-up card: description, website, founded
year, initial/latest round and city."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.acurio.vc/portfolio"
PRIMARY = "Acurio Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select("div.team-collection-item"):
        pop = it.select_one(".popup-wrapper")
        if pop is not None:
            pop.extract()
        f = {x.get("fs-cmsfilter-field"): txt(x) for x in it.select("[fs-cmsfilter-field]")}
        nm = f.get("Name")
        if not nm:
            continue
        g = {}
        if pop is not None:
            for b in pop.select(".div-block-33"):
                k, v = txt(b.select_one(".heading-3")), txt(b.select_one(".body-big"))
                if k and v:
                    g[k] = v
        st = f.get("status") or ""
        out.append(rec(nm, txt(pop.select_one(".textcontent p.body-big")) if pop is not None else None,
                       site(pop.select_one("a.link-block-2")) if pop is not None else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in (f.get("Business Model"), f.get("Sector")) if x], hq_region=f.get("HQ"), location=g.get("City"),
                       founded_year=year_of(g.get("Founded")), initial_round=g.get("Our initial investment"), latest_round=g.get("Latest round"),
                       portfolio_status=st or None, status=st.lower() if st else None))
    finish(out, "acurio", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
