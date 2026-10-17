#!/usr/bin/env python3
"""1Flourish Capital portfolio scraper -> oneflourish_companies.json
Source: https://www.1flourish.com/portfolio — portfolio cards: company name, sector,
description, stage and status badge."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.1flourish.com/portfolio"
PRIMARY = "1Flourish Capital"


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
    for a in s.select("a.portfolio-card"):
        nm = txt(a.select_one(".card-name"))
        if not nm:
            continue
        sec = txt(a.select_one(".card-sector"))
        badge = txt(a.select_one(".card-badge")) or ""
        href = a.get("href") or ""
        out.append(rec(nm, txt(a.select_one(".card-desc")), href if href.startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec else [], stage=txt(a.select_one(".card-stage")), portfolio_status=badge or None,
                       status="exited" if any(w in badge.lower() for w in ("exit", "acquir")) else ("active" if "active" in badge.lower() else None),
                       detail_url=urljoin(SOURCE_URL, href) if href and not href.startswith("http") else None))
    finish(out, "oneflourish", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
