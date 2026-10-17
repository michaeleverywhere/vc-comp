#!/usr/bin/env python3
"""Mandiri Capital Indonesia portfolio scraper -> mandiri_companies.json
Source: https://www.mandiri-capital.co.id/portfolio — Portfolio list: company name, website, sector,
description (Indonesian), city and year."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.mandiri-capital.co.id/portfolio"
PRIMARY = "Mandiri Capital Indonesia"


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
    for r in s.select("div.portfolio-row"):
        nm = txt(r.select_one("h3.company-name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in r.stripped_strings if clean(x) and clean(x) != nm]
        a = [x for x in r.select("a[href^=http]") if "mandiri-capital.co.id" not in x["href"]]
        yr = next((x for x in p if re.fullmatch(r"(19|20)\d\d", x)), None)
        rest = [x for x in p if x != yr and not re.match(r"^[\w.-]+\.\w{2,}/?$", x)]
        out.append(rec(nm, rest[1] if len(rest) > 1 else None, site(a[0]) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=rest[:1], location=rest[2] if len(rest) > 2 else None, year=yr))
    finish(out, "mandiri", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
