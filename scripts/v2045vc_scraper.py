#!/usr/bin/env python3
"""2045 Ventures portfolio scraper -> v2045vc_companies.json
Source: https://www.2045vc.com/2045-portfolio-investments — Wix portfolio columns: company
name, category headline, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.2045vc.com/2045-portfolio-investments"
PRIMARY = "2045 Ventures"


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
    for h in s.select("h2.font_2"):
        col = h.find_parent(class_="wixui-column-strip__column")
        if col is None:
            continue
        ss = [clean(x) for x in col.stripped_strings if clean(x)]
        img = col.select_one("img[alt]")
        nm = ss[0] if ss and ss[0] != txt(h) else (clean(img.get("alt")) if img else None)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        cat = txt(h)
        d = next((x for x in ss if x not in (nm, cat) and len(x) > 25), None)
        out.append(rec(nm, d, site(col.select_one("a[href^=http]")), PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else []))
    finish(out, "v2045vc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
