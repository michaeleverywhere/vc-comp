#!/usr/bin/env python3
"""Social Leverage portfolio scraper -> socialleverage_companies.json
Source: https://socialleverage.com/portfolio/ — portfolio logo wall: company name (site-authored
logo alt)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://socialleverage.com/portfolio/"
PRIMARY = "Social Leverage"


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
    for img in s.find_all("img"):
        nm = clean(re.sub(r"(?i)\s*logo\s*$", "", img.get("alt") or ""))
        if not nm or nm.lower() in {'social leverage'} or nm.lower() in seen or re.search(r"\.(png|jpe?g|svg|webp)$", nm, re.I):
            continue
        seen.add(nm.lower())
        a = img.find_parent("a", href=re.compile(r"^https?://"))
        out.append(rec(nm, None, site(a) if a and 'socialleverage' not in a["href"] else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "socialleverage", ("everywhere_tags",))


if __name__ == "__main__":
    main()
