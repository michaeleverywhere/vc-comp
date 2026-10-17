#!/usr/bin/env python3
"""Ankona Capital portfolio scraper -> ankona_companies.json
Source: https://www.ankona.com/ — homepage portfolio: company name (site-authored
logo alt), category / one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ankona.com/"
PRIMARY = "Ankona Capital"


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
    for img in s.find_all("img", alt=True):
        nm = clean(img.get("alt"))
        if not nm or len(nm.split()) > 4 or nm.lower() in seen or nm.lower().startswith("ankona"):
            continue
        a = img.find_parent("a", href=re.compile(r"^https?://"))
        if not a or "ankona" in a["href"]:
            continue
        seen.add(nm.lower())
        d = clean(a.get_text(" ", strip=True)) or None
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "ankona", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
