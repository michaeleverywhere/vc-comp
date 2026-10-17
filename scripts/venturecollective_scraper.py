#!/usr/bin/env python3
"""The Venture Collective portfolio scraper -> venturecollective_companies.json
Source: https://theventurecollective.com/portfolio — portfolio cards: company name, tag
(e.g. Unicorn), description, sector and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://theventurecollective.com/portfolio"
PRIMARY = "The Venture Collective"


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
    for a in s.select("a.card"):
        nm = txt(a.select_one(".card-name"))
        if not nm:
            continue
        foot = a.select_one(".card-foot span")
        sec = txt(foot) if foot and "visit" not in (foot.get("class") or []) else None
        out.append(rec(nm, txt(a.find("p")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       portfolio_tag=txt(a.select_one(".tag"))))
    finish(out, "venturecollective", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
