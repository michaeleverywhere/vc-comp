#!/usr/bin/env python3
"""Indico Capital Partners portfolio scraper -> indico_companies.json
Source: https://www.indicocapital.com/our-companies — Webflow companies grid: company name, year,
description, category, Past/Unicorn/Pre-Indico/RIP badges and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.indicocapital.com/our-companies"
PRIMARY = "Indico Capital Partners"


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
    for a in s.select("a.work-card[href]"):
        nm = txt(a.select_one("[fs-cmsfilter-field=name]"))
        if not nm:
            continue
        badges = [txt(x) for x in a.select(".company-category-wrapper") if txt(x)]
        cats = [txt(x) for x in a.select("[fs-cmsfilter-field=category]") if txt(x) and txt(x).lower() != "all"]
        uni = bool(a.select_one(".company-category-wrapper.unicorn"))
        out.append(rec(nm, txt(a.select_one("div.text-color-lightslategray:not(.text-size-small)")), None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=cats, vintage_year=txt(a.select_one("[fs-cmsfilter-field=year]")), badges=", ".join(badges) or None, unicorn=uni or None,
                       status="exited" if any(b in ("Past",) for b in badges) else ("defunct" if "RIP" in badges else None),
                       detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "indico", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
