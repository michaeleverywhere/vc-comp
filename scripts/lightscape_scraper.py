#!/usr/bin/env python3
"""Lightscape Partners portfolio scraper -> lightscape_companies.json
Source: https://www.lightscape.vc/portfolio — Next.js companies table: company name (logo
alt), description, tags, location, year and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.lightscape.vc/portfolio"
PRIMARY = "Lightscape Partners"


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
    for a in s.select("a[href^='/companies/']"):
        img = a.find("img")
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        kids = a.find_all(recursive=False)
        divs = [k for k in kids if k.name == "div"]
        tags = [txt(x) for x in a.select("span") if txt(x) and "rounded-full" in " ".join(x.get("class") or [])]
        loc = yr = None
        if len(divs) >= 3:
            bits = [clean(x) for x in divs[2].stripped_strings if clean(x)]
            for b in bits:
                if re.fullmatch(r"(19|20)\d{2}", b):
                    yr = int(b)
                elif not loc:
                    loc = b
        out.append(rec(nm, txt(divs[0]) if divs else None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, location=loc, investment_year=yr,
                       detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "lightscape", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
