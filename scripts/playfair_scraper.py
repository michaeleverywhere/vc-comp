#!/usr/bin/env python3
"""Playfair Capital portfolio scraper -> playfair_companies.json
Source: https://playfair.vc/portfolio.php — portfolio grid (company slug, website and
stage) plus each /companies/<slug> page for the company name (page title) and
meta description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://playfair.vc/portfolio.php"
PRIMARY = "Playfair Capital"


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
    items = []
    for c in s.select("div.portfolio-company-container"):
        a = c.select_one("a[href*='/companies/']")
        if not a:
            continue
        items.append((urljoin(SOURCE_URL, a["href"]), clean(c.get("data-link")), txt(c.select_one("p.stage"))))
    pages = fetch_many([u for u, _, _ in items])
    for u, web, stg in items:
        html = pages.get(u)
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        t = txt(d.title) or ""
        t = re.sub(r"\s*[–-]\s*Playfair Portfolio\s*$", "", t)
        nm = clean(re.split(r":|\s[–-]\s", t, maxsplit=1)[0])  # "<Name>: <tagline>" or "<Name> - <tagline>"
        md = d.select_one("meta[name=description]")
        if not nm:
            continue
        out.append(rec(nm, clean(md.get("content")) if md else None, web if web and web.startswith("http") else None, PRIMARY,
                       SOURCE_URL, scraped_at, stage=stg, detail_url=u))
    finish(out, "playfair", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
