#!/usr/bin/env python3
"""Leo Capital portfolio scraper -> leocapital_companies.json
Source: https://leo.capital/portfolio/ — portfolio cards (name, blurb, country, sector tags,
target market) plus each /portfolio/<slug>/ page for the company website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://leo.capital/portfolio/"
PRIMARY = "Leo Capital"


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
    for c in s.select("a.pf-card"):
        nm = txt(c.select_one(".pf-name"))
        if nm:
            items.append((nm, c, urljoin(SOURCE_URL, c["href"])))
    pages = fetch_many([u for _, _, u in items])
    for nm, c, u in items:
        d = BeautifulSoup(pages.get(u) or "", "html.parser")
        w = next((a for a in d.select("a[href^='http']") if (txt(a) or "").startswith("Visit ")), None)
        tags = [txt(t) for t in c.select(".pf-tag:not(.geo)") if txt(t)]
        secs = [clean(x) for t in tags for x in t.split("·") if clean(x)]
        out.append(rec(nm, txt(c.select_one(".pf-blurb")), site(w), PRIMARY, SOURCE_URL, scraped_at, sectors=secs,
                       location=txt(c.select_one(".pf-tag.geo")), target_market=txt(c.select_one(".pf-target-value")), detail_url=u))
    finish(out, "leocapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
