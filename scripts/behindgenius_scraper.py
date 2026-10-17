#!/usr/bin/env python3
"""Behind Genius Ventures portfolio scraper -> behindgenius_companies.json
Source: https://www.behindgeniusventures.com/portfolio — Webflow portfolio grid: company name and
sector (the site lists names only)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.behindgeniusventures.com/portfolio"
PRIMARY = "Behind Genius Ventures"


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
    for it in s.select(".portfolio-item"):
        nm = txt(it.select_one(".text-block-7"))
        if nm:
            sec = txt(it.select_one(".text-block-8"))
            m = re.match(r"^(.*?)\s*\(acq\.?\s+(.+?)\)\s*$", nm)
            out.append(rec(m.group(1) if m else nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                           exit_note=f"Acquired by {m.group(2)}" if m else None, status="acquired" if m else None))
    finish(out, "behindgenius", ("everywhere_tags",))


if __name__ == "__main__":
    main()
