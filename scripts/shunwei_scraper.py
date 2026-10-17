#!/usr/bin/env python3
"""Shunwei Capital portfolio scraper -> shunwei_companies.json
Source: https://en.shunwei.com/portfolio — Portfolio grid (English site): company name,
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://en.shunwei.com/portfolio"
PRIMARY = "Shunwei Capital"


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
    seen = set()
    for it in s.select("div.masonry__item"):
        nm = txt(it.select_one("h3")) or txt(it.select_one("a.modal-trigger p"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        d = it.select_one("p.text-justify")
        desc = clean(d.get_text(" ", strip=True)) if d else None
        if desc and len(desc) > 400:
            desc = desc[:400].rsplit(" ", 1)[0] + "…"
        web = next((site(a) for a in it.select(".modal-content a[href^=http]") if site(a)), None)
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "shunwei", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
