#!/usr/bin/env python3
"""Fluent Ventures portfolio scraper -> fluent_companies.json
Source: https://www.fluent.vc/portfolio — Webflow CMS portfolio cards: company
name, Fluent fund and year, current/historical flag, country, business-model
tags and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.fluent.vc/portfolio"
PRIMARY = "Fluent Ventures"


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
    for it in s.select("div.w-dyn-item[class*='project-card']"):
        nm = txt(it.select_one(".blog-card-title"))
        if not nm:
            continue
        fy = [txt(x) for x in it.select(".text-100") if txt(x) and not x.get("fs-cmsfilter-field") and txt(x) != "/"]
        yr = next((year_of(x) for x in fy if year_of(x)), None)
        fund = next((x for x in fy if not year_of(x)), None)
        tags = [txt(x) for x in it.select("[fs-cmsfilter-field='model']") if txt(x)]
        a = it.select_one("a.project-item")
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, fund=fund, year=yr,
                       holding=txt(it.select_one("[fs-cmsfilter-field='current']")),
                       country=txt(it.select_one("[fs-cmsfilter-field='country']")),
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None))
    finish(out, "fluent", ("fund", "country", "everywhere_tags"))


if __name__ == "__main__":
    main()
