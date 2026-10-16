#!/usr/bin/env python3
"""Remarkable Ventures portfolio scraper -> remarkable_companies.json
Source: https://www.remarkable.vc/portfolio — Webflow CMS portfolio cards: company name,
category labels, stage labels and detail page /portfolio/<slug>."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.remarkable.vc/portfolio"
PRIMARY = "Remarkable Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select(".portfoliol_item.w-dyn-item"):
        nm = txt(it.select_one(".para3"))
        if not nm:
            continue
        cats = [txt(c) for c in it.select("[fs-cmsfilter-field='category']") if txt(c)]
        stages = [txt(c) for c in it.select(".label.is--blue .tagsmall") if txt(c)]
        a = it.select_one("a[href]")
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, stage=", ".join(stages) or None,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "remarkable", ("stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
