#!/usr/bin/env python3
"""Shadow Ventures portfolio scraper -> shadowvc_companies.json
Source: https://shadow.vc/investments — investments grid (`div.collection-item-6`):
company name (site-authored logo alt), category, profile link and exit flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://shadow.vc/investments"
PRIMARY = "Shadow Ventures"


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
    for it in s.select("div.collection-item-6"):
        img = it.find("img", alt=True)
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        flag = it.select_one(".portfolio-exit-flag")
        exited = bool(flag) and "w-condition-invisible" not in (flag.get("class") or [])
        a = it.find("a", href=True)
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, category=clean(it.get("data-category")) or None,
                       profile_url=urljoin(SOURCE_URL, a["href"]) if a else None, status="exited" if exited else None))
    finish(out, "shadowvc", ("everywhere_tags",))


if __name__ == "__main__":
    main()
