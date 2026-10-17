#!/usr/bin/env python3
"""Silverton Partners portfolio scraper -> silverton_companies.json
Source: https://www.silvertonpartners.com/portfolio — Portfolio archive: company name (link title), first
investment stage, status and sector tags, founders, description, location and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.silvertonpartners.com/portfolio"
PRIMARY = "Silverton Partners"


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
    for it in s.select("div.archives-item"):
        a = it.select_one(".image-wrapper a[title]")
        nm = clean(a.get("title")) if a else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        tax = [txt(x) for x in it.select(".taxonomies li") if txt(x)]
        st = [t for t in tax if re.fullmatch(r"active|exited|acquired|ipo|inactive|closed", t, re.I)]
        out.append(rec(nm, txt(it.select_one(".description-wrapper")), None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[t for t in tax if t not in st], first_investment=txt(it.select_one(".first-investment-wrapper")),
                       founders=", ".join(txt(x) for x in it.select(".founders h5.name") if txt(x)) or None,
                       location=txt(it.select_one(".geo-wrapper")), portfolio_status=", ".join(st) or None,
                       status="exited" if any(re.match(r"exit|acqui|ipo", t, re.I) for t in st) else None,
                       detail_url=a.get("href")))
    finish(out, "silverton", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
