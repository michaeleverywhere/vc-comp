#!/usr/bin/env python3
"""NextGen Venture Partners portfolio scraper -> nextgen_companies.json
Source: https://nextgenvp.com/portfolio — portfolio grid: company name
(logo alt), description, website and exited marker."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://nextgenvp.com/portfolio"
PRIMARY = "NextGen Venture Partners"


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
    for it in s.select("div.portfolio-items"):
        body = it.select_one(".portfolio-info-body")
        img = body.find("img") if body else None
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        ex = it.select_one(".exited-mark")
        out.append(rec(nm, txt(body.find("article")), site(body.find("a")), PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if ex else None))
    finish(out, "nextgen", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
