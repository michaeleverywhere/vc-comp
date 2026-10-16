#!/usr/bin/env python3
"""Yes VC portfolio scraper -> yesvc_companies.json
Source: https://yes.vc/portfolio/ — WordPress portfolio list: company name (h3, with exit
notes in parentheses as published, e.g. '(acquired by Grammarly)'), description
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://yes.vc/portfolio/"
PRIMARY = "Yes VC"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select("li.e-in"):
        raw = txt(it.select_one(".portfolio-text-wrapper h3"))
        if not raw:
            continue
        m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", raw)
        nm, note = (clean(m.group(1)), clean(m.group(2))) if m else (raw, None)
        low = (note or "").lower()
        out.append(rec(nm, txt(it.select_one("p.description")), site(it.select_one("a.portfolio-arrow")), PRIMARY,
                       SOURCE_URL, scraped_at, exit_note=note,
                       status="acquired" if "acqui" in low else ("public" if "ipo" in low or "public" in low else None)))
    finish(out, "yesvc", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
