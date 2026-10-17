#!/usr/bin/env python3
"""Stage Venture Partners portfolio scraper -> stagevp_companies.json
Source: https://www.stage.vc/companies — Webflow case-study cards: company name,
sector, tagline, exit badge and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.stage.vc/companies"
PRIMARY = "Stage Venture Partners"


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
    for a in s.select("a.case-study-card"):
        nm = txt(a.select_one("h4"))
        if not nm:
            continue
        sec = txt(a.select_one("h6"))
        ex = a.select_one(".exit-badge") is not None
        out.append(rec(nm, txt(a.select_one("p:not(.paragraph-4)")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       status="exited" if ex else None, detail_url=urljoin(SOURCE_URL, a.get("href") or "")))
    finish(out, "stagevp", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
