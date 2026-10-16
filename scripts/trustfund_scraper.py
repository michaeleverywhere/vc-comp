#!/usr/bin/env python3
"""Trust Fund portfolio scraper -> trustfund_companies.json
Source: https://www.trustfund.vc/portfolio — portfolio cards (`div.team8_item`): company
name, description and website (logo alts on the page are unreliable and ignored)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.trustfund.vc/portfolio"
PRIMARY = "Trust Fund"


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
    for it in s.select("div.team8_item"):
        nm = txt(it.select_one(".text-size-large.text-weight-semibold"))
        if not nm:
            continue
        out.append(rec(nm, txt(it.select_one("p.paragraph")), site(it.select_one("a.social-link")), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "trustfund", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
