#!/usr/bin/env python3
"""Mission One Capital portfolio scraper -> m1c_companies.json
Source: https://m1c.vc/portfolio — Squarespace accordion: company name, category,
geography, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://m1c.vc/portfolio"
PRIMARY = "Mission One Capital"


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
    for li in s.select("li.accordion-item"):
        nm = txt(li.select_one(".accordion-item__title"))
        if not nm:
            continue
        cat = geo = None
        desc = []
        for p in li.select(".accordion-item__description p"):
            t = txt(p)
            if not t or p.find("a"):
                continue
            if t.startswith("Category:"):
                cat = clean(t.split(":", 1)[1])
            elif t.startswith("Geography:"):
                geo = clean(t.split(":", 1)[1])
            else:
                desc.append(t)
        web = next((a for a in li.select("a[href]") if site(a)), None)
        out.append(rec(nm, " ".join(desc) or None, site(web), PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], location=geo))
    finish(out, "m1c", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
