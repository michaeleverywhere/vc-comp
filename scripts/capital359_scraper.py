#!/usr/bin/env python3
"""359 Capital portfolio scraper -> capital359_companies.json
Source: https://www.359capital.com/ — homepage Webflow portfolio logo list:
company name (site-authored logo alt), category, status (e.g. acquired) and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.359capital.com/"
PRIMARY = "359 Capital"


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
    for it in s.select("div.portfolio-logos_collection-item"):
        img = it.select_one("img[alt]")
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        cat = txt(it.select_one("[fs-list-field=category]"))
        st = [txt(d) for d in it.select("div div") if txt(d) and txt(d) != cat]
        out.append(rec(nm, None, site(it.select_one("a[href^=http]")), PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [],
                       status=st[0].lower() if st else None))
    finish(out, "capital359", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
