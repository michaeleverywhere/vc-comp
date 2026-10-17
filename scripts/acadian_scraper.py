#!/usr/bin/env python3
"""Acadian Ventures portfolio scraper -> acadian_companies.json
Source: https://www.acadianventures.com/companies — Webflow/Finsweet companies list: name,
category, location, current stage, entry stage, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.acadianventures.com/companies"
PRIMARY = "Acadian Ventures"


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
    for it in s.select(".companies_item-wrap"):
        f = {x.get("fs-list-field"): txt(x) for x in it.select("[fs-list-field]")}
        nm = f.get("name")
        if not nm:
            continue
        coll = it.select(".companies_meta-collapsed")
        entry = txt(coll[1].select(".tagline")[-1]) if len(coll) > 1 and coll[1].select(".tagline") else None
        dd = it.select_one(".companies_item-dropdown-content > div")
        stg = f.get("stage") or ""
        out.append(rec(nm, txt(dd), site(it.select_one("a.companies_link")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[f["category"]] if f.get("category") else [], location=f.get("location"), current_stage=stg or None,
                       entry_stage=entry, status="exited" if stg.lower() == "exited" else None))
    finish(out, "acadian", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
