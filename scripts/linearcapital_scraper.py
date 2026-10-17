#!/usr/bin/env python3
"""Linear Capital portfolio scraper -> linearcapital_companies.json
Source: https://www.linear.vc/portfolio — Portfolio cards: company name, tagline, description,
year and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.linear.vc/portfolio"
PRIMARY = "Linear Capital"


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
    for a in s.select("a.portfolio_item"):
        p = [clean(x) for x in a.stripped_strings if clean(x)]
        if not p or p[0].lower() in seen:
            continue
        seen.add(p[0].lower())
        yr = next((x for x in p if re.fullmatch(r"(19|20)\d\d", x)), None)
        web = next((x for x in p if x.startswith("http")), None)
        out.append(rec(p[0], p[2] if len(p) > 2 and p[2] not in (yr, web) else (p[1] if len(p) > 1 else None), web, PRIMARY, SOURCE_URL, scraped_at,
                       tagline=p[1] if len(p) > 2 else None, year=yr))
    finish(out, "linearcapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
