#!/usr/bin/env python3
"""Hi Ventures (formerly ALLVP) portfolio scraper -> hiventures_companies.json
Source: https://www.hi.vc/portfolio — Portfolio list: company name, year invested and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.hi.vc/portfolio"
PRIMARY = "Hi Ventures (formerly ALLVP)"


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
    for t in s.select("div.item-title"):
        it = t.find_parent(class_="w-dyn-item") or t.parent
        nm = txt(t)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        m = re.search(r"Hi since\s*(\d{4})", " ".join(it.stripped_strings))
        a = it.select_one("a[href^=http]")
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, year=m.group(1) if m else None))
    finish(out, "hiventures", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
