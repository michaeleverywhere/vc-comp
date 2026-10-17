#!/usr/bin/env python3
"""First Star Ventures portfolio scraper -> firststarvc_companies.json
Source: https://firststar.vc/companies — companies list: company name, one-line
description, website and 'acquired' tag (shown only when set)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://firststar.vc/companies"
PRIMARY = "First Star Ventures"


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
    for c in s.select("div.companies-cms_item-link"):
        nm = txt(c.select_one("div.alt-text-32px"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        acq = c.select_one("div.tag") is not None and "acquired" in (txt(c.select_one("div.tag")) or "").lower()
        a = c.find("a", href=re.compile(r"^https?://(?!(www\.)?firststar)")) or c.find_parent("a", href=re.compile(r"^https?://"))
        out.append(rec(nm, txt(c.select_one("p")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, status="exited" if acq else None))
    finish(out, "firststarvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
