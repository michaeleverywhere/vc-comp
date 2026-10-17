#!/usr/bin/env python3
"""Illumina Ventures portfolio scraper -> illuminaventures_companies.json
Source: https://www.illuminaventures.com/portfolio/ — Portfolio cards with modals: company name, sector
and status tags, intro and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.illuminaventures.com/portfolio/"
PRIMARY = "Illumina Ventures"


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
    for it in s.select("article.card-portfolio"):
        nm = txt(it.select_one(".info h4"))
        if not nm:
            continue
        tags = [txt(x) for x in it.select(".info .tags span") if txt(x)]
        st = [t for t in tags if re.search(r"portfolio|exit|acqui|ipo", t, re.I)]
        a = it.select_one(".info a[href^=http]")
        out.append(rec(nm, txt(it.select_one(".info p.intro")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[t for t in tags if t not in st], portfolio_status=", ".join(st) or None,
                       status="exited" if any(re.search(r"exit|acqui|ipo", t, re.I) for t in st) else None))
    finish(out, "illuminaventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
